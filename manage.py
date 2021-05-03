# mange.py

from collections import defaultdict
import logging
import os

import click
from flask.cli import with_appcontext

from mylogger import add_module_handler
from app import create_app
from app.extensions import db, migrate
from app.models import GeneratorConfig, Article, Category
from app.admin.scan_translations import get_info, ArticleFromFolder

logger = logging.getLogger('launcher')
logger.setLevel(logging.DEBUG)
add_module_handler(logger, folder='logs')
app = create_app()


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, migrate=migrate,
                gc=GeneratorConfig, Article=Article, category=Category)


def create_tables():
    db.create_all()


@app.cli.command('update-articles-info')
@click.argument("folder", type=click.Path(exists=True))
@click.argument("output", default='artinfos.csv')
def update_articles_info(folder, output):
    """Acquisizione info aggiornate sui file tradotti in formato .csv

    FOLDER è la directory che contiene i file tradotti in fomato .xml

    OUTPUT è il file su cui vengono scritte le informazioni
    (default=artinfos.csv)
    """
    with open(output, mode='w') as fh:
        logger.info(f'Inizio scansione cartella {folder}')
        for article in get_info(folder):
            fh.write(';'.join(article) + '\n')
        logger.info(f'Fine scansione, scritto {output}')
        print(f'Fine scansione, scritto {output}')
    return


@app.cli.command('import-articles')
@click.argument('folder', default='translations', type=click.Path(exists=True))
def import_articles(folder):
    prompt = f'Importare da {folder}? (il database verrà AZZERATO)'
    if not click.confirm(prompt):
        logger.info("Importazione abbandonata dall'utente")
        return
    _trunc_table(Article)
    # _trunc_table(Category)
    bycat = defaultdict(list)
    [bycat[art.categ].append(art) for art in get_info(folder)]
    for categ, articles in bycat.items():
        categ = Category.query.filter_by(descr=categ).first()
        for art in articles:
            article = Article(art.title, categ.id, art.filename,
                              art.lastmod, art.size, art.indexed)
            logger.info(f'Inserting {article} ({categ})')
            db.session.add(article)
    db.session.commit()
    # with open(filename) as fh:
    #     for rk in [row.strip().split(';')
    #                for row in fh.readlines() if row]:
    #         print(rk)
    #         art = Article(*rk)
    #         db.session.add(art)
    #     db.session.commit()


def _add_categ(categories):
    for categ in categories:
        logger.info(f'Adding {categ}')
        db.session.add(Category(categ))
    db.session.commit()


def _trunc_table(obj):
    deleted = obj.query.delete()
    db.session.commit()
    logger.info(f'Eliminati {deleted} oggetti {obj.__name__}')




