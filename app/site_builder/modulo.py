# modulo.py

import os.path
import sys
from typing import List

from app.lib.common import ottieni_moduli_tradotti, ottieni_modulo
from app.site_builder.inline_sub import InlineSubs

__doc__ = "Rappresenta un modulo da rendere con i template di Django"


class Modulo:
    """Rappresenta un modulo tradotto"""
    insubs = InlineSubs()

    def __init__(self, nome: str, ext: str = 'html'):
        """Ottiene il nome del modulo"""
        self.nome = nome
        self.versione = None
        self.titolo = ''
        self.descrizione = ''
        self.data_agg = None
        # self.url = f'{os.path.splitext(nome)[0]}.html'
        self.url = f'{nome}.{ext}'
        self.categoria = ''
        self.data_pub = None
        self.nome_per_rss = None
        self.indicizza = False
        self.titolo_ref = ''

    def __raw__(self):
        return f"{self.nome} - {self.titolo}"

    def __str__(self):
        return f"{self.nome} - {self.titolo}"

    @property
    def nome_per_teaser(self) -> str:
        return self.nome.replace('_', ' ')

    @staticmethod
    def ottieni_modulo(path_modulo: str, nome_modulo: str) -> 'Modulo':
        """Ritorna un oggetto `Modulo` elaborando `nome_modulo`"""
        diz = ottieni_modulo(path_modulo, nome_modulo)
        m = Modulo(nome_modulo)
        m.nome = diz['nome_modulo']
        m.categoria = diz['categ']
        m.data_agg = diz['agg']
        m.descrizione = diz['descr']
        m.titolo = diz['titolo']
        m.versione = diz['versione']
        m.titolo_ref = m.titolo.split('-')[0]
        return m
    
    def per_tabella_indice(self) -> list:
        """Ritorna info da utilizzare nel template della tabella indice"""
        return [
            self.data_agg.strftime('%d.%m.%Y'),
            self.nome,
            self.titolo
        ]

    @staticmethod
    def ordina_per_data(moduli: List['Modulo']) -> List['Modulo']:
        """
        Ritorna un elenco di moduli ordinati per data di pubblicazione,
        se presente, in ordine decrescente
        """
        moduli_ok = [m for m in  moduli if m.data_pub]
        return sorted(moduli_ok, key=lambda m: m.data_pub, reverse=True)


def elenco_per_indice(tran_dir: str) -> List[Modulo]:
    """
    Ritorna una lista di oggetti `Modulo` per comporre l'indice dei moduli
    :param tran_dir: la directory con i file .xml di traduzione
    :return:
    """
    elenco = list()
    insubs = InlineSubs()
    for k, v in ottieni_moduli_tradotti(tran_dir).items():
        if not v['indicizza']:  # Un modulo da ignorare
            continue
        modulo = Modulo(k)
        modulo.data_agg = v['agg']
        modulo.descrizione = insubs.rimpiazza(v['descr'])
        modulo.titolo = v['titolo']
        modulo.versione = v['versione']
        modulo.categoria = v['categ']
        modulo.indicizza = v['indicizza']
        elenco.append(modulo)
    # Modulo.ordina_per_data(elenco)
    return elenco
