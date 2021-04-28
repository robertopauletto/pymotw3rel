#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import OrderedDict
import datetime
from typing import Union, List, Dict

# from app.site_builder.modulo import Modulo
from app.site_builder.modulo import Modulo
from app.site_builder.footer import Footer


__date__ = ''
__version__ = '0.1'
__doc__ = """Costruisce le pagine indice
Versione %s %s
""" % ( __version__, __date__ )


class DjTabelleIndici:
    base_url = 'indice.html'
    date_fmt = "%d.%m.%Y"
    """
    Rappresenta una pagina che contiene una tabella con l'indice dei moduli
    """
    def __init__(self, moduli: List['Modulo'], footer: Footer):
        """"""
        self._moduli = moduli
        self.footer = footer

    @property
    def elenco_moduli(self) -> List['Modulo']:
        """
        Ritorna un elenco di oggetti `Modulo` ordinati per
        nomi
        """
        return sorted(self._moduli, key=lambda x: x.nome.lower())
    
    @property
    def last_upd(self) -> str:
        """
        Ottiene la data odierna formattata come `DjModulo.dtfmt`
        """
        return datetime.date.today().strftime(DjTabelleIndici.date_fmt)

    @property
    def moduli_per_iniziale(self) -> dict:
        diz = OrderedDict()
        moduli = self.elenco_moduli
        # Da A -> Z
        for i in range(65, 91):
            letter = chr(i)
            if letter in diz:
                continue
            aref = [modulo.nome for modulo in moduli
                    if modulo.nome.upper().startswith(letter)]
            diz[letter] = aref[0] if aref else None
        return diz

    
if __name__ == '__main__':
    pass
