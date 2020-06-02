# main.py

import datetime
import logging
from math import ceil
import os
import re
import webbrowser

from flask import (
    render_template, redirect, Blueprint, request, url_for, session
)


from mylogger import add_module_handler
from app.extensions import db
from app.models import GeneratorConfig, Category, Article
from app.forms import (
    HTMLGeneratorForm, BuilderLog, CategoryForm, NewArticleForm
)
from app.site_builder.builder import (
    build_module, build_index, build_module_table,
    get_categorie, crea_nuovo_articolo, save_categorie
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
add_module_handler(logger, folder='logs')

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/index')
def index():
    return render_template('index.html', titolo="T")


@main.route('/config', methods=['GET', 'POST'])
def config():
    parameters, objlist = GeneratorConfig.parse_config()
    if request.method == 'POST':
        GeneratorConfig.update_config(objlist, request.form)
        return redirect(url_for('main.config'))
    return render_template('config.html',
                           parameters=parameters, title='Configurazione')


@main.route('/generator', methods=['GET', 'POST'])
def generator():
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


@main.route('/new_article', methods=['GET', 'POST'])
def new_article():
    form = NewArticleForm()
    categories = Category.query.order_by(Category.descr).all()
    choices = [(categ.id, categ.descr) for categ in categories]
    def_template = GeneratorConfig.query.filter_by(
        conf_key='new_article_template_name'
    ).first()
    form.template.data = def_template.conf_value
    choices.insert(0, (-1, '--Selezionare una categoria--'))
    form.categ.choices = choices

    data = dict()
    error = None

    if form.validate_on_submit():
        title = form.name.data
        filename = f'{title}.xml'
        dtmod = datetime.datetime.strptime(form.publish_date.data, '%Y-%m-%d')
        cat_id = form.categ.id
        is_ind = form.add_to_index.data
        print()

    return render_template(
        "new_article.html", error=error, form=form, title="Nuovo Articolo",
        categorie=categories, def_template=def_template
    )


@main.route('/category', methods=['GET', 'POST'])
def category():
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


@main.route('/article/<string:key>', methods=['GET', 'POST'])
def article(key):
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
    next_url = url_for('main.article', key='all', page=articles.next_num) \
        if articles.has_next else None
    prev_url = url_for('main.article', key='all', page=articles.prev_num) \
        if articles.has_prev else None

    data = dict(articles=articles, next=next_url, prev=prev_url,
                source_articles_folder=diz['tran_dir'],
                headers='ID,TITOLO,CATEGORIA,NOME FILE,ULTIMO AGG.,'
                        'DIMENSIONE, INDICIZZATO'.split(','))
    return render_template('article.html', key=None, data=data)


@main.route('/source', methods=['GET', 'POST'])
def source():
    return render_template('source.html')


@main.route('/article_new', methods=['GET', 'POST'])
def article_new():
    pass
