# last_ten.py

import datetime
import re
from typing import List

__doc__ = "Rappresenta gli ultimi 10 moduli tradotti/aggiornati"


class LastTen:
    """Rappresentazione degli ultimi 10 moduli tradotti/aggiornati"""
    date_fmt = '%d.%M.%Y'

    def __init__(self, last_upd: str, name: str, descr: str):
        """
        :param last_upd: Ultimo aggiornamento - pattern formato LastTen.date_fmt
        :param name: nome modulo
        :param descr: descrizione
        """
        self._last_upd = datetime.datetime.strptime(last_upd, LastTen.date_fmt)
        self._name = name.strip()
        self.descr = descr.strip()

    @property
    def name(self) -> str:
        """Ritorna il nome del modulo tradotto (che è sempre la prima parola
        se trattasi di moduli combinati - es. profile e pstats"""
        if len(self._name.split()) > 1:
            return self._name.split()[0]
        else:
            return self._name

    @property
    def last_upd(self) -> str:
        """Ritorna la data agg.to"""
        return self._last_upd.strftime(LastTen.date_fmt)

    @property
    def title(self) -> str:
        """Ritorna il titolo del modulo"""
        return f"{self._name} - {self.descr}"

    def __str__(self):
        """Rappresentazione stringa dell'oggetto"""
        return "{self.last_upd}: {self._name} - {self.descr}"


def lastten_factory(rows: list) -> List[LastTen]:
    """Ritorna una lista di oggetti `Lastten`:

    **Prerequisito**: la riga è nel formato dd.mm.aaaa\tnome - descrizione
    """
    last_ten = list()
    for row in rows:
        if not row:
            continue
        dt, _tmp = re.split(r'\s+', row, 1)
        name, descr = _tmp.split('-', 1)
        last_ten.append(LastTen(dt, name, descr))
    return last_ten
