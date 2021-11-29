# rss_feed_builder.py

import datetime
from typing import Union, List

from app.site_builder.rss2feed import RSS2Feed

__doc__ = "Crea il file xml che rappresenta un feed rss"


class FeedItem:
    """Rappresenta un elemento di un feed"""

    def __init__(self, title: str, lnk: str,
                 descr: str = '',
                 date: datetime.datetime = datetime.datetime.utcnow(),
                 guid: Union[None, str] = None):
        """
        Istanzia i campi di un feed
        """
        self._title = title
        self._lnk = lnk
        self._descr = descr
        self._dt = date
        self._guid = guid

    def __str__(self) -> str:
        return f"{self._title} - {self._dt}"

    def item2rssfeed(self) -> dict:
        """Ritorna una rappresentazione dizionario per alimentazione
        del feed RSS"""
        return {
            "title": self._title,
            "link": self._lnk,
            "description": self._descr,
            "pub_date": self._dt,
            "guid": self._guid
        }


class Feed:
    """Rappresenta un file rss """

    def __init__(self, title: str, link: str, description: str = None,
                 xml_declarations: list = None):
        """
        Istanzia titolo, indirizzo e descrizione del feed
        """
        self._title = title
        self._link = link
        self._descr = description or ''
        self._declarations = xml_declarations or []
        self._feeditems: List[FeedItem] = list()

    @property
    def count_items(self):
        """Numero di elementi nel canale"""
        return len(self._feeditems)

    def add_item(self, feed_item: FeedItem):
        """
        Aggiunge un elemento al feed
        """
        self._feeditems.append(feed_item)

    def _add_declaration(self, xmldoc: str,
                         declarations: list, linesep: str = '\n'):
        rows = xmldoc.split(linesep)
        rows.insert(1, '\n'.join(declarations))
        return linesep.join(rows)

    def get_feed(self, pretty: bool = True):
        """
        Ritorna la rappresentazione xml del feed
        :param pretty: se `True` ritorna il testo pretty-printed
        :return: il feed in formato xml
        """
        if not self._feeditems:
            raise AttributeError("Almeno un elemento deve essere presente")
        feed = RSS2Feed(self._title, self._link, self._descr)
        for item in self._feeditems:
            feed.append_item(**item.item2rssfeed())
        # patch - adding a stylesheet declaration for the xml
        # self._declarations.append(
        #     '<?xml-stylesheet type="text/css" href="/css/xmlstyle.css" ?>')
        if self._declarations:
            return self._add_declaration(
                # Questo accrocchio funziona solo se il file è formattato
                # con separatori di riga pertanto con questa opzione viene
                # forzato a true il parametro dell'argomento `pretty`
                feed.get_xml(True, encoding='utf-8'),
                self._declarations
            )
        else:
            return feed.get_xml(pretty, encoding='utf-8')
