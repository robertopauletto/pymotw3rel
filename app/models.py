# models.py

from collections import defaultdict
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

    def __repr__(self):
        return f'<GeneratorConfig {self.conf_key}: {self.conf_value}>'

