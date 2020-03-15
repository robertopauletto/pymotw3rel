"""Provides the RSS2Feed class."""

from calendar import timegm
from datetime import datetime
from email.utils import formatdate
from typing import Union, Any
from xml.dom.minidom import Document, Element


class RSS2Feed:
    """An RSS 2.0 feed."""

    class FeedError(Exception):
        pass

    def __init__(self, title: str, link: str, description: str,
                 pub_date: Any = None, bld_date: Any = None):
        """Initialize the feed with the specified attributes.

        :param title: brief title for the feed
        :param link: URL for the page containing the syndicated content
        :param description: longer description for the feed
        :param pub_date: last publication date for the feed (optional)
        :param bld_date: last modified-date for the feed (optional)
        """
        self._document = Document()
        rss_element = self._document.createElement('rss')
        rss_element.setAttribute('version', '2.0')
        self._document.appendChild(rss_element)
        self._channel = self._document.createElement('channel')
        rss_element.appendChild(self._channel)
        self._channel.appendChild(self._create_text_element('title', title))
        self._channel.appendChild(self._create_text_element('link', link))
        self._channel.appendChild(
            self._create_text_element('description', description)
        )
        if pub_date is not None:
            self._set_date('pubDate', pub_date)
        if bld_date is not None:
            self._set_date('lastBuildDate', bld_date)
            
    def _set_date(self, tag_name: str, date: datetime):
        """
        Sets `tag_name`  with `date`
        """
        try:
            timestamp = int(date)
        except TypeError:
            timestamp = timegm(date.utctimetuple())
        self._channel.appendChild(
            self._create_text_element(
                tag_name, formatdate(timestamp)
            )
        )

    def _create_text_element(self, type_: str, text: str):
        """Create a text element and return it."""
        element = self._document.createElement(type_)
        element.appendChild(self._document.createTextNode(text))
        return element

    def append_item(self, title: Union[None, str] = None,
                    link: Union[None, str] = None,
                    description: Union[None, str] = None,
                    pub_date: Union[datetime, None] = None,
                    guid: Union[None, str] = None):
        """Append the specified item to the feed.

        :param title: brief title for the item
        :param link: URL for the page for the item
        :param description: longer drescription for the item
        :param guid: globally unique identifier. It's a string that uniquely
                     identifies the item.
        :param pub_date: date published
        """
        # Either title or description *must* be present
        if title is None and description is None:
            raise self.FeedError(
                "Either title or description must be provided."
            )
        element = self._document.createElement('item')
        if title is not None:
            element.appendChild(self._create_text_element('title', title))
        if link is not None:
            element.appendChild(self._create_text_element('link', link))
        if description is not None:
            element.appendChild(
                self._create_text_element('description', description)
            )
        if pub_date is not None:
            try:
                timestamp = int(pub_date)
            except TypeError:
                timestamp = timegm(pub_date.utctimetuple())
            element.appendChild(
                self._create_text_element('pubDate', formatdate(timestamp))
            )
        if guid is not None:
            element.appendChild(self._create_text_element('guid', guid))
        self._channel.appendChild(element)

    def get_xml(self, pretty_print=True, encoding=None):
        """Return the XML for the feed.

        :pretty_print: if `True` returns a pretty print representation 
        :returns: XML representation of the RSS feed
        """
        return self._document.toxml(encoding) \
            if not pretty_print else self._document.toprettyxml()

