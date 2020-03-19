# scan_translations

from collections import namedtuple
import datetime
import os
import re
from typing import List, Union

__doc__ = "Scansiona la dir traduzioni e raccoglie info sui file .xml"

RE_TITLE = re.compile(r'(\n<titolo_1>)(.*)(</titolo_1>)', re.DOTALL)
RE_CATEG = re.compile(r'(\n<categoria>)(.*)(</categoria>)', re.DOTALL)
EXT = '.xml'


def _strip_text(regex: re.Pattern, text: str, group_no: int) -> str:
    """
    Estrae la porzione di testo che appartiene al `group_no` se
    espressione regolare trova corrispondenza

    :param regex:
    :param text:
    :param group_no:
    :return: testo richiesto oppure stringa vuota se match non corrisposto
             o se gruppo non raggiunto
    """
    matches = regex.finditer(text)
    for i, match in enumerate(matches):
        if group_no < len(match.groups()):
            return match.groups()[group_no].strip()
    return ''


ArticleFromFolder = namedtuple('Article', 'title categ filename lastmod size')


def get_info(folder: str, ext: str = EXT) -> List[ArticleFromFolder]:
    """
    Cerca in `folder` i file con suffisso `.ext` ed estrae info in
    `Article`

    **Da usare per ricostruire il database degli articoli**

    :param folder:
    :param ext:
    :return:
    """
    articles = list()
    for fn in [os.path.join(folder, fn)
               for fn in os.listdir(folder)
               if fn.endswith(ext)]:
        with open(fn) as fh:
            text = fh.read()
        title = _strip_text(RE_TITLE, text, 1)
        categ = _strip_text(RE_CATEG, text, 1).lower()
        filename = os.path.split(fn)[-1]
        lastmod = datetime.datetime.fromtimestamp(os.stat(fn).st_mtime)
        size = os.stat(fn).st_size
        articles.append(
            ArticleFromFolder(title, categ, filename,
                              lastmod.strftime('%Y/%m/%d'), str(size))
        )
    return articles


if __name__ == '__main__':
    l, dd = get_info('../../translations')
    print()
