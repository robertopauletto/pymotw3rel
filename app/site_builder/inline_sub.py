from collections import defaultdict
import logging
import os
import string
from typing import Union

# from pymotw3_manager import add_module_handler

__date__=''
__version__='0.2'
__doc__="""Sostituzioni di stringhe specifiche con il corrispondente
codice html
Versione %s %s
""" % ( __version__, __date__ )

logger = logging.getLogger(__name__)
# add_module_handler(logger)

DEFAULT_SUBS = [
    "sbk|<code>",
    "ebk|</code>",
    "sev|<span class='bkItem'>",
    "eev|</span>",
    "<|&lt;",
    ">|&gt;",
]


class InlineSubs:
    """
    Gestione di abbreviazioni nel testo che vengono espanse nei valori
    da rendere
    """
    def __init__(self, file_diz: Union[None, str] = None):
        """(str [, list])

        Inizializza e carica gli elementi predefiniti nel
        dizionario di traduzione oppure gli elementi presenti nel file
        ``file_diz``

        Prerequisito: ``file_diz`` contiene valori nel formato
        chiave|valore dove valore è un valido pezzo di codice html
        """
        self._diz = defaultdict(str)
        self.carica_diz(file_diz)

    def aggiungi_voce(self, chiave: str, valore: str):
        """
        Incrementa il dizionario dei valori da sostituire, oppure sostituisce
        il valore se `chiave` già presente
        """
        self._diz[chiave] = valore

    def carica_diz(self, file_diz):
        """
        Carica le chiavi che restituiscono il codice html dal file
        ``file_diz`` se valorizzato oppure un insieme predefinito (entrambi
        se le chiavi del diz. predefinito non esistono nel file in input.

        Se ``self._diz`` non è vuoto **viene sovrascritto**
        """
        to_parse = DEFAULT_SUBS
        if file_diz and os.path.exists(file_diz):
            to_parse.extend([riga.strip()
                             for riga in open(str(file_diz))
                             if riga and not riga.startswith("#")])

        for riga in to_parse:
            # se i commenti sono anche nel file predefinito
            if not riga or riga.startswith("#"):
                continue
            chiave, valore = riga.strip().split('|')
            self._diz[chiave.strip()] = valore.strip()

    def rimpiazza(self, testo: str) -> str:
        """
        Se un elemento che è chiave di ``self.diz`` si trova in ``testo`` viene
        sostituito con il valore nel dizionario
        """
        return string.Template(testo).safe_substitute(self._diz)
