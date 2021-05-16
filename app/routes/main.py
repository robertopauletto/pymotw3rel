# main.py

import datetime
import json
import logging
from math import ceil
import os
import re
from shutil import copy
import webbrowser

from flask import (
    render_template, redirect, Blueprint, request, url_for, session, flash,
    jsonify
)
import pyperclip

from mylogger import add_module_handler
from app.extensions import db
from app.models import GeneratorConfig, Category, Article, search_all
from app.forms import (
    HTMLGeneratorForm, BuilderLog, CategoryForm, NewArticleForm,
    ArticleBoilerplate, SourceForm, SearchArticlesForm
)
from app.site_builder.modulo import (
    translated_module_names, translated_module_for_automcompletions)
from app.site_builder.builder import (
    build_module, build_index, build_module_table,
    get_categorie, crea_nuovo_articolo, save_categorie, create_privacy_page
)
from app.lib.common import (get_article_boilerplate, create_new_article_file,
                            parse_text_for_spellcheck)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
add_module_handler(logger, folder='logs')

main = Blueprint('main', __name__)
translated_modules = []


@main.route('/')
@main.route('/index')
def index():
    """Pagina principale"""
    return redirect(url_for('main.article', key='all'))


@main.route('/config', methods=['GET', 'POST'])
def config():
    """Gestione configurazione"""
    parameters, objlist = GeneratorConfig.parse_config()
    if request.method == 'POST':
        category, prompt = GeneratorConfig.update_config(objlist, request.form)
        flash(category, prompt)
        return redirect(url_for('main.config'))
    return render_template('config.html',
                           parameters=parameters, title='Configurazione')


def _check_module_list(translated_modules: list,
                       modules_to_build: str) -> tuple:
    """
    Verifica se i nomi modulo passati nel form corrispondono a quelli di un
    modulo tradotto

    :param translated_modules: elenco nomi moduli tradotti
    :param modules_to_build: stringa da form utente con moduli tradotti
    :return: 1) la stringa moduli da tradurre depurata di quelli non trovati
             2) lista nomi moduli non trovati
    """
    retval = []
    orig_modules_list = modules_to_build.split()
    for module in orig_modules_list:
        if module.endswith('.xml'):
            module = module.replace('.xml', '')
        found = len([mod for mod in translated_modules
                     if module.lower() == mod.lower()])
        if not found:
            continue
        retval.append(module)
    return " ".join(retval), set(orig_modules_list).difference(set(retval))


@main.route('/generator', methods=['GET', 'POST'])
def generator():
    """Generatore html articoli"""
    global translated_modules
    diz = _get_config_items()
    if not translated_modules:
        translated_modules = translated_module_names(diz['tran_dir'])

    data = translated_module_for_automcompletions(diz['tran_dir'])
    with open('app/static/js/autocomp.json', mode="w") as fh:
        json.dump(data, fh)

    log = ""
    form = HTMLGeneratorForm()
    # Se ricevo già il nome del modulo dal url referente (pagina articoli)
    if 'module' in request.args:
        session['module'] = request.args['module']

    if form.validate_on_submit():
        tmplog = ""
        module = form.modules.data
        module_ok, module_ko = _check_module_list(translated_modules, module)
        for mod_ko in module_ko:
            log += f"Il modulo {mod_ko} non esiste o non è stato tradotto\n"

        if not module_ok:
            flash("error", "Nessun modulo con il testo richiesto")
            return redirect(url_for('main.generator'))

        module = module_ok
        if module:
            logger.info(f"Generazione di {module} iniziata")
            log += f"Generazione di {module} iniziata\n"
            tmplog, check_syntax, modulo = build_module(module.split())
            session['module'] = module
        log += '\n'.join(tmplog) if tmplog else "\n"
        if form.privacy_page.data:
            logger.info('Ricostruzione degli indici')
            log += '\n'.join(create_privacy_page("privacy.html"))
            session['privacy_page'] = True
        if form.spellcheck:
            pass
        if form.rebuild_index.data:
            logger.info('Ricostruzione degli indici')
            log += '\n'.join(build_index())
            session['rebuild_index'] = True
        if form.rebuild_table.data:
            logger.info('Ricostruzione tabella moduli')
            log += '\n'.join(build_module_table())
            session['rebuild_table'] = True

        session['log'] = log
        if module:
            session['module_fullpath'] = modulo
        session['check_syntax'] = (parse_text_for_spellcheck(check_syntax)
                                   if form.spellcheck.data else None)
        flash('success', 'Codice HTML generato per il modulo')
        return redirect(url_for('main.builder_log'))

    # else:
    #     pass

    m = session.get('module', '')
    return render_template('generator.html',
                           title='Generatore Codice HTML',
                           form=form, defname=m)


@main.route('/search', methods=['GET', 'POST'])
def search():
    value = request.args['sitesearch']
    results = search_all(value)
    return render_template('search.html', titolo='Ricerca', results=results)


def _get_config_items():
    parameters, objlist = GeneratorConfig.parse_config()
    diz = dict()
    for obj in objlist:
        diz[obj.conf_key] = obj.conf_value
    return diz


@main.route('/source/<string:module_name>', methods=['GET', 'POST'])
def source(module_name):
    """Mostra il testo xml dell'articolo"""
    diz = _get_config_items()
    orig_mod_name = ""
    print(orig_mod_name)

    module_path = os.path.abspath(
        os.path.join(diz["tran_dir"], module_name)
    )
    if not os.path.exists(module_path):
        flash("error", f"File {os.path.abspath(module_path)} not found")
        return redirect(url_for('main.article', key='all'))
    with open(module_path) as fh:
        module_text = fh.read()
    form = SourceForm()

    if form.validate_on_submit():
        bkfolder = os.path.join(diz["tran_dir"], "backup")
        fn, ext = os.path.splitext(os.path.basename(module_path))
        versioned = f"{bkfolder}/{fn}-" \
                    f"{datetime.datetime.now().strftime('%Y%m%d%H%M%s')}{ext}"
        copy(module_path, versioned)
        with open(module_path, mode='w') as fh:
            fh.write(form.source_text.data)
        module_text = form.source_text.data
        flash("success", 'Articolo modificato')

    form.source_text.data = module_text
    return render_template(
        'source.html', module_text=module_text, module_path=module_path,
        module_filename=os.path.basename(module_path), form=form
    )


@main.route('/article/<string:key>', methods=['GET', 'POST'])
def article(key):
    """Elenco articoli, `key` è il filtro per id categoria"""
    diz = _get_config_items()
    form = SearchArticlesForm()
    page = request.args.get('page', 1, type=int)

    if request.method == 'POST' and request.form['filter_text']:
        articles = Article.query.filter(
            Article.title.contains(request.form['filter_text'])
        ).paginate(page, 10, False)
    else:
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
                headers=',TITOLO,CATEGORIA,NOME FILE,ULTIMO AGG.,'
                        'DIMENSIONE, INDICIZZATO'.split(','))
    return render_template('article.html', key=None, data=data,
                           form=form, title="Elenco Articoli")


@main.route('/new_article', methods=['GET', 'POST'])
def new_article():
    """Nuovo articolo"""
    form = NewArticleForm()
    form.categ.choices = [(-1, '--Selezionare una categoria--')] + \
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
    check_syntax = []
    if session['check_syntax']:
        check_syntax = session['check_syntax']
        pyperclip.copy(check_syntax)
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
                           title="Log elaborazione",
                           form=form, logcontent=lc,
                           check_syntax=check_syntax)
