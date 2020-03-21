# models.py

from collections import defaultdict
from datetime import datetime
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
                 lastmod: str, size: str, indexed: str):
        self.title = title
        self.categ_id = categ_id
        self.filename = filename
        self.lastmod = datetime.strptime(lastmod, '%Y/%m/%d')
        self.size = int(size)
        self.indexed = int(indexed)

    def __repr__(self):
        return f'<Article {self.id} - {self.title} ({self.lastmod})>'


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
