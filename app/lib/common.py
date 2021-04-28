# common.py

import datetime
import logging
from os import name
import os.path
import shutil
import string
import sys
import re
from typing import Union, List, Dict

from app.models import Article

__doc__ = "Utility varie"

# sys.path.append(r'../database')

PATHS = {
    'posix': r'/home/robby',
    'mac':  r'/Users/robby',
    'win32': r'c:\users\robby',
}


def get_article_boilerplate(model: str, article: Article,
                            descr: str) -> str:
    """
    Genera contenuto boilerplate per un nuovo articolo
    Passare il contenuto di questa funzione a `create_new_article_file`
    :param model: il template di partenza
    :param article:
    :param descr: la descrizione del modulo
    :return: la stringa boilerplate
    """
    tmpl = string.Template(model)
    name, purpose = article.title.split('-')
    values = {
        'categoria': article.artcat.descr,
        'modulo': name.strip().title(),
        'scopo': purpose,
        'descrizione': descr,
        'indicizza': 'sì' if article.indexed else 'no'
    }
    return tmpl.safe_substitute(values)


def create_new_article_file(outfile: str, boilerplate: str,
                            overwrite: bool = False) -> None:
    """
    Scrive il testo boilerplate di un articolo, sovrascrive il file `overwrite`
    :param outfile:
    :param boilerplate:
    :param overwrite:
    :return:
    """
    if not overwrite and os.path.exists(outfile):
        shutil.copyfile(outfile, f'{outfile}.bk')
    with open(outfile, mode='w') as fh:
        fh.write(boilerplate)


# def get_root(paths: dict = PATHS, fixed_path: str = ''):
#     """
#     Ritorna la radice del percorso di lavoro in base al sistema
#     operativo in cui viene eseguito lo script, scegliendo tra i
#     valori in `paths`
#     """
#     if sys.platform == 'darwin':
#         return os.path.join(paths['mac'], fixed_path )
#     if name in paths.keys():
#         return os.path.join(paths[name], fixed_path )
#     else:
#         return os.path.join('.', fixed_path)
#
#
# def html_path():
#     """
#     Metodo di convenienza che ottiene il percorso dei file html tradotti
#
#     >>> print( html_path())
#     /home/robby/Dropbox/Code/python/pymotw-it/html
#     """
#     return get_root(fixed_path=OLD_HTML_FOLDER)
#
#
# def xml_path(path_):
#     """
#     Metodo di convenienza che ottiene il percorso dei file xml tradotti
#     """
#     return get_root(fixed_path=path_)


def get_xml_files(xmlpath: str, nome_modulo: Union[str, None] = None):
    """
    Metodo di convenienza che estrae i percorsi completi dei file xml
    con la traduzione
    
    Se `nome_modulo` è valorizzato recupera solo i file il cui nome
    contiene `nome_modulo` altrimenti recupera tutti i file .xml
    """
    if nome_modulo:
        return [
            os.path.splitext(os.path.basename(filename))[0]
            for filename in os.listdir(xmlpath)
            if filename.endswith('.xml') and nome_modulo in filename
        ]
    else:
        return [
            os.path.splitext(os.path.basename(filename))[0]
            for filename in os.listdir(xmlpath)
            if filename.endswith('.xml')
        ]


def my_title(frase):
    """(str) -> str
    
    Capitalizzazione delle parole di una frase a ragion veduta (nel senso
    che non vengono rese maiuscole tutte le parole di una frase, le
    preposizioni e gli articoli)

    >>> print(my_title("il lupo perde il pelo ma non il vizio"))
    'il Lupo Perde il Pelo Ma Non il Vizio'

    TODO: Sicuramente funzione imperfetta da verificare più accuratamente
    """
    non_capitalizzare = (
        'di da in con su per tra fra il la lo gli uno uno una del '
        'dello della degli dei al allo agli alle ed od nel nei negli'
    )
    retval = list()

    for parola in frase.split():
        if len(parola) > 1 and parola not in non_capitalizzare:
            parola = parola.title()
        retval.append(parola)
    return " ".join(retval)


def _estrai_da_tag(righe: list, nome_tag: str, ripeti: bool = False) -> list:
    """
    Scansione `righe` e ritorna il testo racchiuso tra `tag` 
    Se `ripeti` == `False` ritorna non appena individua la prima occorrenza
    di `nome_tag`
    
    Da utilizzare per recuperare valori di tag univoci tipo descrizione
    """
    nome_tag = "%s" % nome_tag
    retval = []
    is_aperto = False
    for riga in righe:
        if riga[1:].startswith(nome_tag):
            if not is_aperto:
                is_aperto = True
        elif riga[2:].startswith(nome_tag):
            is_aperto = False
            if not ripeti:
                return retval
        else:
            if is_aperto:
                retval.append(riga.strip())
    return retval            


RE_CATEGORIA = re.compile(r'<categoria>(.*)</categoria>')


def _ottieni_categoria(righe: list) -> Union[str, None]:
    for riga in righe:
        match = RE_CATEGORIA.match(riga)
        if match and len(match.groups()) == 1:
            return match.groups()[0]
    return None


RE_INDICIZZA = re.compile(r'<indicizza>(.*)</indicizza>')


def _is_da_indicizzare(righe: list) -> bool:
    for riga in righe:
        match = RE_INDICIZZA.match(riga)
        if match and len(match.groups()) == 1:
            valore = match.groups()[0]
            if valore and valore == "no":
                return False
    return True

            
RE_DATA_ARTICOLO = re.compile(r'<data_articolo>(.*)</data_articolo>')


def _ottieni_data_articolo(righe: list) -> Union[str, None]:
    for riga in righe:
        match = RE_DATA_ARTICOLO.match(riga)
        if match and len(match.groups()) == 1:
            return match.groups()[0].strip()
    return None
        

def ottieni_modulo(path_modulo, nome_modulo):
    # modulo = get_xml_files(path_modulo)[0]
    # xml_dir = xml_path(path_modulo)
    fn = os.path.join(path_modulo, f"{nome_modulo}.xml")
    if not os.path.exists(fn):
        print("Articolo non presente: %s" % os.path.basename(fn))
        return None
    return _ottieni_modulo(fn)


def _ottieni_modulo(nome_file: str) -> Union[dict, None]:
    """
    Legge `nome_file` e recupera i tag che contengono le info:
    
    - descrizione modulo
    - titolo
    - data aggiornamento (ultima data accesso al file)
    - versione traduzione
    - categoria
    """
    righe = open(nome_file).readlines()
    if not righe:
        logging.warning(f"{nome_file} è vuoto")
        return None

    descr = ' '.join(_estrai_da_tag(righe, 'descrizione'))
    titolo = " ".join(_estrai_da_tag(righe, 'titolo_1'))
    categ = _ottieni_categoria(righe).strip()
    if not categ:
        # print(os.path.basename(nome_file), " manca categoria")
        logging.warning(f"{os.path.basename(nome_file)}, manca categoria")
        categ = 'Sconosciuta'
    data_articolo = _ottieni_data_articolo(righe)
    ultimo_agg = datetime.date.fromtimestamp(os.stat(nome_file).st_mtime)
    indicizza = _is_da_indicizzare(righe)
    if '-' in titolo:
        nome_modulo, titolo = titolo.strip().split('-', 1)
    else:
        nome_modulo = titolo
    return {
        'descr': descr,
        'nome_modulo': nome_modulo,
        'titolo': titolo,
        'agg': ultimo_agg,
        'versione': "",  # Non più necessaria per python3
        'categ': categ,
        'data_articolo': data_articolo,
        'indicizza': indicizza,
    }
        

def ottieni_moduli_tradotti(tran_dir: str) -> dict:
    """
    Ritorna un dizionario con chiave nome modulo che contiene:

    - data ultima modifica
    - titolo
    - versione
    - descrizione
    :param tran_dir: la directory con i file .xml dei moduli tradotti
    :return:
    """
    retval = dict()
    da_elaborare = get_xml_files(tran_dir)
    for modulo in da_elaborare:
        fn = os.path.join(tran_dir, f"{modulo}.xml")
        if not os.path.exists(fn):
            logging.warning(f"Articolo non presente: {os.path.basename(fn)}")
            continue
        retval[modulo] = _ottieni_modulo(fn)
    return retval


def accenti2entity(val):
    """(str) -> str
    
    Sostituisce le vocali accentate in `val` con le corrispondenti entità
    xml
    
    >> accenti2entity("il colibrì è un volatile")
    >> 'il colibr&igrave; &egrave un volatile
    """
    p
