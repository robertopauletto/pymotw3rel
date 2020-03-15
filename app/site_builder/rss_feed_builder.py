# rss_feed_builder.py

import datetime
from typing import Union

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
        

class Feed:
    """Rappresenta un file rss """
    def __init__(self, title: str, link: str, description: str = ''):
        """
        Istanzia titolo, indirizzo e descrizione del feed
        """
        self._title = title
        self._link = link
        self._descr = description
        self._items = list()
        
    def add_item(self, feed_item: FeedItem):
        """
        Aggiunge un elemento al feed
        """
        self._items.append(feed_item)
    
    def get_feed(self, pretty: bool = True):
        """Ritorna la rappresentazione xml del feed"""
        if not self._items:
            raise AttributeError("Almeno un elemento deve essere presente")
        feed = RSS2Feed(self._title, self._link, self._descr)
        # with open(r'/home/robby/deb.txt', mode='w') as fh:
        #     for item in self._items:
        #         #print item._title
        #         # try:
        #         #     fh.write("%s %s %s\n" %
        #         (item._title, item._lnk, item._descr))
        #         # except:
        #         #     print item._title
        #         #     raise
        #         feed.append_item(
        #             title=item._title,
        #             link=item._lnk,
        #             description=item._descr,
        #             pub_date=item._dt,
        #             guid=item._guid
        #         )
        return feed.get_xml(pretty, encoding='utf-8')
