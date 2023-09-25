# index_builder.py

import codecs
from functools import partial
import os.path
import re
import traceback
from typing import List

from django.utils.encoding import smart_str

from app.site_builder.my_html import MyHtml
from app.site_builder.modulo import Modulo

h = MyHtml()  # Si occupa del rendering in HTML dei dati

# DEF_CHARSET = 'utf-8'


def ottieni_tabella(elenco_moduli: List[Modulo]):
    """
    Rendering nel tag <table> di `elenco_moduli`
    """
    for_tbl = [';'.join(modulo.per_tabella_indice())
               for modulo in elenco_moduli]
    return h.table(for_tbl, False)
