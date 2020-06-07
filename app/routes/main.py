# main.py

import datetime
import logging
from math import ceil
import os
import re
import webbrowser

from flask import (
    render_template, redirect, Blueprint, request, url_for, session, flash
)

from mylogger import add_module_handler
from app.extensions import db
from app.models import GeneratorConfig, Category, Article
from app.forms import (
    HTMLGeneratorForm, BuilderLog, CategoryForm, NewArticleForm,
    ArticleBoilerplate
)
from app.site_builder.builder import (
    build_module, build_index, build_module_table,
    get_categorie, crea_nuovo_articolo, save_categorie
)
from app.lib.common import get_article_boilerplate, create_new_article_file
import pyperclip

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
add_module_handler(logger, folder='logs')

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/index')
def index():
    """Pagina principale"""
    return render_template('index.html', titolo="T")


@main.route('/config', methods=['GET', 'POST'])
def config():
    """Gestione configurazione"""
    parameters, objlist = GeneratorConfig.parse_config()
    if request.method == 'POST':
        GeneratorConfig.update_config(objlist, request.form)
        return redirect(url_for('main.config'))
    return render_template('config.html',
                           parameters=parameters, title='Configurazione')


@main.route('/generator', methods=['GET', 'POST'])
def generator():
    """Generatore html articoli"""
    form = HTMLGeneratorForm()

    if form.validate_on_submit():
        module = form.modules.data.lower()
        logger.info(f"Generazione di {module} iniziata")
        is_sidebar_fixed = form.fixed_sidebar.data
        logger.info(
            f"Barra Indice {'fissa' if is_sidebar_fixed else 'flottante'}"
        )
        tmplog, check_sintassi = build_module(module.split(), is_sidebar_fixed)
        if form.spellcheck:
            pass
        log = '\n'.join(tmplog)
        if form.rebuild_index.data:
            logger.info('Ricostruzione degli indici')
            log += '\n'.join(build_index())
            session['rebuild_index'] = True
        if form.rebuild_table.data:
            logger.info('Ricostruzione tabella moduli')
            log += '\n'.join(build_module_table())
            session['rebuild_table'] = True

        session['log'] = log
        session['module'] = module
        session['check_sintassi'] = (check_sintassi if form.spellcheck.data
                                     else None)
        return redirect(url_for('main.builder_log'))
    else:
        pass

    m = session.get('module', '')
    return render_template('generator.html',
                           titolo='Generatore Codice HTML',
                           form=form, defname=m)


@main.route('/article/<string:key>', methods=['GET', 'POST'])
def article(key):
    """Elenco articoli, `key` è il filtro per id categoria"""
    parameters, objlist = GeneratorConfig.parse_config()
    diz = dict()
    for obj in objlist:
        diz[obj.conf_key] = obj.conf_value

    page = request.args.get('page', 1, type=int)
    if key and re.match(r'^\d+$', key):
        articles = Article.query.filter_by(
            categ_id=int(key)
        ).paginate(page, 10, False)
    else:
        articles = Article.query.paginate(
            page, 10, False
        )
    next_url = url_for('main.article', key=key, page=articles.next_num) \
        if articles.has_next else None
    prev_url = url_for('main.article', key=key, page=articles.prev_num) \
        if articles.has_prev else None

    data = dict(articles=articles, next=next_url, prev=prev_url,
                source_articles_folder=diz['tran_dir'],
                headers='ID,TITOLO,CATEGORIA,NOME FILE,ULTIMO AGG.,'
                        'DIMENSIONE, INDICIZZATO'.split(','))
    return render_template('article.html', key=None, data=data)


@main.route('/new_article', methods=['GET', 'POST'])
def new_article():
    """Nuovo articolo"""
    form = NewArticleForm()
    form.categ.choices = [(-1, '--Selezionare una categoria--')] +\
        Category.get_list(True)
    form.template.data = GeneratorConfig.get_template_def_name()
    form.publish_date.data = datetime.date.today()

    if form.validate_on_submit():
        descr = form.description.data
        title = f"{form.name.data} - {form.purpose.data}"
        categ_id = form.categ.data
        filename = f'{form.name.data}.xml'
        lastmod = form.publish_date.data
        is_ind = form.add_to_index.data
        article = Article(title, categ_id, filename, lastmod, None, is_ind)
        db.session.add(article)
        db.session.commit()
        art_path = GeneratorConfig.get_boilerplate_article_path()
        with open(art_path) as fh:
            boilerplate_text = get_article_boilerplate(
                fh.read(), article, descr
            )
        session['boilerplate'] = boilerplate_text
        session['new_article_path'] = os.path.join(
            GeneratorConfig.get_translations_folder(), filename
        )
        return redirect(url_for('main.article_boilerplate'))

    data = dict()
    error = None
    session['boilerplate'] = None
    session['new_article_path'] = None

    return render_template(
        "new_article.html", form=form, title="Nuovo Articolo",
        action='Inserisci'
    )


@main.route('/article_boilerplate', methods=['GET', 'POST'])
def article_boilerplate():
    if 'boilerplate' not in session:
        redirect(url_for('main.article', key='all'))
    form = ArticleBoilerplate()
    form.text.data = session['boilerplate']

    if request.method == 'POST':
        if 'copiatesto' in request.form:
            pyperclip.copy(form.text.data)
            flash('Testo copiato negli appunti', 'success')
        elif 'scrivifile' in request.form:
            create_new_article_file(session['new_article_path'], form.text.data)
            flash(f"Creato file {session['new_article_path']}", 'success')

    return render_template(
        'new_article_source.html', form=form,
        nomefile=session['new_article_path'], title='Testo Articolo'
    )


@main.route('/category', methods=['GET', 'POST'])
def category():
    """Elenca categorie e modifica / elimina categoria"""
    if request.method == 'POST':
        id = request.form['catid']
        descr = request.form['catdescr']
        cat = Category.query.filter_by(id=id).first()
        if 'aggiorna' in request.form:
            cat.descr = descr
            db.session.add(cat)
        elif 'elimina' in request.form:
            db.session.delete(cat)
        db.session.commit()
    categories = Category.query.all()
    data = dict(categories=categories, headers=('ID', 'NOME', 'NR. ARTICOLI'))
    return render_template('categorie.html', data=data)


@main.route('/category_new', methods=['GET', 'POST'])
def category_new():
    """Nuova categoria"""
    form = CategoryForm()
    error = None
    descr = ''
    if form.validate_on_submit():
        descr = form.descr.data.lower()
        cat = Category.query.filter_by(descr=descr).first()
        if cat:
            error = 'Categoria già presente!'
        else:
            db.session.add(Category(descr))
            db.session.commit()
            return redirect(url_for('main.category'))

    return render_template("category_new.html", form=form, error=error,
                           titolo='Nuova Categoria', descr=descr)


@main.route('/builder_log', methods=['GET', 'POST'])
def builder_log():
    """Mostra il risultato dell'elaborazione"""
    form = BuilderLog()
    lc = session.get('log', '')
    x = request
    if form.validate_on_submit():
        if 'apri' in request.form:
            pwd = os.path.abspath(os.curdir)
            htmldir = GeneratorConfig.get_value('html_dir')
            fn, _ = os.path.splitext(session['module'])
            webpage = os.path.join(htmldir, f'{fn}.html')
            webbrowser.open(webpage)
        else:
            return redirect(url_for('main.generator'))

    # notify(nobj, 'Scritta pagina ' + session.get('module', ''))
    return render_template('builder_log.html',
                           titolo="Log elaborazione",
                           form=form, logcontent=lc)


@main.route('/source', methods=['GET', 'POST'])
def source():
    """Mostra il testo xml dell'articolo"""
    return render_template('source.html')

