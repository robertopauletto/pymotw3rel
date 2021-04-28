# models.py

from collections import defaultdict
from datetime import datetime, date
import os
import string
from typing import Union, Tuple, DefaultDict, List

from .extensions import db


class GeneratorConfig(db.Model):
    """Gestione configurazione"""
    id = db.Column(db.Integer, primary_key=True)
    conf_key = db.Column(db.String(50), nullable=False, unique=True)
    conf_value = db.Column(db.String(256), nullable=False)
    conf_tag = db.Column(db.String(30), nullable=False)
    conf_tip = db.Column(db.String)
    conf_tabname = db.Column(db.String, nullable=False)

    def __init__(self, key: str, value: str,
                 tag: str, tip: Union[str, None] = None) -> None:
        self.conf_key = key
        self.conf_value = value
        self.conf_tag = tag
        self.conf_tip = tip
        self.conf_tabname = ''.join(self.conf_key)

    @staticmethod
    def get_value(key: str):
        item = GeneratorConfig.query.filter_by(conf_key=key).first()
        return item.conf_value

    @staticmethod
    def parse_config() -> Tuple[DefaultDict[str, List['GeneratorConfig']],
                                List['GeneratorConfig']]:
        """
        Divide le chiavi di configurazione per argomenti da visualizzare
        nella pagina di gestione
        """
        retval = defaultdict(list)
        objlist = list()
        for rk in GeneratorConfig.query.all():
            retval[rk.conf_tabname].append(rk)
            objlist.append(rk)
        return retval, objlist

    @staticmethod
    def update_config(objlist: list, form: dict):
        """
        Aggiornamento parametri di configurazione
        :param objlist:
        :param form:
        :return:
        """
        for genform in objlist:
            value = form[f'value_{genform.id}']
            tip = form[f'tip_{genform.id}']
            if value != genform.conf_value:
                genform.conf_value = value
            if tip and tip != genform.conf_tip:
                genform.conf_tip = tip
            db.session.add(genform)
            db.session.commit()

    @staticmethod
    def get_template_def_name() -> str:
        return GeneratorConfig.query.filter_by(
            conf_key='new_article_template_name'
        ).first().conf_value

    @staticmethod
    def get_boilerplate_article_path() -> str:
        """Ottiene il nome del file contentente il codice boilerplate"""
        folder = GeneratorConfig.query.filter_by(
            conf_key='translated_modules_dir'
        ).first().conf_value
        fn = GeneratorConfig.query.filter_by(
            conf_key='new_article_template_name'
        ).first().conf_value
        return os.path.join(folder, fn)

    @staticmethod
    def get_translations_folder() -> str:
        """Ottiene il percorso della cartella traduzioni"""
        return GeneratorConfig.query.filter_by(
            conf_key='translated_modules_dir'
        ).first().conf_value

    def __repr__(self):
        return f'<GeneratorConfig {self.conf_key}: {self.conf_value}>'


class Article(db.Model):
    """Rappresenta un articolo tradotto"""
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    categ_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    artcat = db.relationship('Category', backref='article')
    filename = db.Column(db.String(255), nullable=False, unique=True)
    lastmod = db.Column(db.DateTime)
    size = db.Column(db.Integer)
    indexed = db.Column(db.Integer)

    def __init__(self, title: str, categ_id: int, filename: str,
                 lastmod: Union[str, datetime.date],
                 size: Union[str, None], indexed: str):
        self.title = title
        self.categ_id = categ_id
        self.filename = filename
        if isinstance(lastmod, date):
            self.lastmod = lastmod
        else:
            self.lastmod = datetime.strptime(lastmod, '%Y/%m/%d')
        self.size = int(size) if size else 0
        self.indexed = int(indexed)

    def __repr__(self):
        return f'<Article {self.id} - {self.title} ({self.lastmod})>'

    @staticmethod
    def exists(name: str) -> bool:
        return Article.query.like(name).count() > 0


class Category(db.Model):
    """Rappresenta una categoria del modulo"""
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    descr = db.Column(db.String(255), nullable=False)
    articles = db.relationship('Article', backref='category',
                               lazy='dynamic')

    def __init__(self, name: str):
        self.descr = name

    def __repr__(self):
        return f'<Category {self.id} - {self.descr}>'

    @staticmethod
    def get_list(as_title: bool = False) -> List[Tuple[int, str]]:
        """
        Ottiene l'elenco delle categorie e dell'id associato
        :param as_title: se `True` ritorna la versione *title* della descrizione
        :return:
        """
        categories = Category.query.order_by(Category.descr).all()
        choices = [(categ.id, categ.descr) for categ in categories]
        if as_title:
            choices = [(categ[0], categ[1].title()) for categ in choices]
        return choices


def search_all(value: str) -> list:
    results = list()
    # Find modules
    value = f"%{value.lower()}%"
    mod_found = Article.query.filter(Article.title.like(value))
    for item in mod_found:
        results.append({
            "filename": f"{os.path.splitext(item.filename)[0]}.html",
            "title": item.title,
            "categ": item.artcat.descr
        })
    return results
