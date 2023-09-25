# builder.py

# from __future__ import division

try:
    import codecs
    from collections import defaultdict, OrderedDict, deque
    import datetime
    import glob
    import logging
    from math import ceil
    import os
    import os.path
    import string
    import sys
    import traceback
    from typing import List, Union, Any, Tuple
    from urllib.parse import urlparse, urljoin

    from django import template, setup
    from django.template import loader, exceptions

#    from pymotw3_manager import add_module_handler
    from app.site_builder.dj_indice import Indice
    from app.site_builder.dj_modulo import DjModulo
    from app.site_builder.dj_tabelle_indici import DjTabelleIndici
    from app.site_builder.footer import Footer
    import app.site_builder.modulo_xml2html as xml2html
    from app.site_builder.index_builder import ottieni_tabella
    from app.site_builder.modulo import Modulo, elenco_per_indice
    from app.lib.common import my_title
    import app.lib.last_ten as lt
    from app.site_builder.inline_sub import InlineSubs
    from app.site_builder.rss_feed_builder import Feed, FeedItem
except ImportError as imperr:
    raise ImportError('Errore importazione modulo ' + imperr.name)


__date__ = ''
__version__ = '1.0'
__doc__ = """
Il punto di entrata dell'applicazione (nella modalità console)

** da agosto 2017 l'entrata dal modulo è DEPRECATA **, utilizzare l'interfaccia
Flask (`main_flask.py`)

Qui vengono costruite le singole pagine, gli indici e le tabelle
riepilogative

Le pagine vengono costruite basandosi su bootstrap 3

I tipi di pagine che possono essere costruite sono:

pagine riepilogative con teasers (:py:func:`crea_pagine_indice`)
    sono le pagine che contengono gli incipit dei moduli (12 per pagina), dalle
    quali si può accedere al dettaglio del singolo modulo

pagina modulo
    la pagina che descrive il modulo (se ne possono costruire anche in batch)

pagine indice (:py:func:`crea_tabella_indice`)
    le pagine che riepilogano tutti i moduli presenti

Argomenti della versione console:

- Nessun argomento: ricostruzione di tutti i moduli (dopo conferma)
- Se il primo argomento inizia con ind si ricostruisce la pagina indice
- Se il primo argomento inizia con tab si ricostruisce la tabella riepilogativa
- qualsiasi altra stringa iniziale rappresenta il nome di un modulo 
  da costruire, se ne possono passare diverse separate da virgola

Versione %s %s
""" % ( __version__, __date__ )

logger = logging.getLogger(__name__)
# add_module_handler(logger)


builder_conf = {}


def set_builder_conf(dictconf):
    """Imposta la configurazione per l'istanza"""
    global builder_conf
    builder_conf = dictconf


FOOTER = Footer(
    nome='PyMOTW-it 3',
    periodo=str(datetime.date.today().year),
    data_agg=datetime.date.today().strftime("%d-%m-%Y"),
    email='pymotwit3(at)fastmail.com'
)


def imposta_param_django(template_dirs):
    """(list of str)

    Imposta i parametri di configurazione per django ed assegna i
    percorsi per i file template in `template_dirs`
    """
    from django.conf import settings
    if not settings.configured:
        settings.configure(
            DEBUG=True, TEMPLATE_DEBUG=True,
            TEMPLATE_DIRS=template_dirs,
            TEMPLATES=[
                {
                    'BACKEND': 'django.template.backends.django.DjangoTemplates',
                    'DIRS': template_dirs
                }
            ],
            INSTALLED_APPS=(
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.sites',
                'django.contrib.messages',
                ),
        )
    setup()
    print()


def build(template_file, context_dict, rendered_file):
    """(str, dict, str)

    Rendering in `rendered_file` dalla pagina template `template_file`
    utilizzando gli elementi in `context`
    """
    try:
        t = loader.get_template(template_file)
        with open(rendered_file, mode='w') as fh:
            x = t.render(context_dict, builder_conf["def_charset"])
            fh.write(x)
    except exceptions.TemplateDoesNotExist:
        raise
    except exceptions.TemplateSyntaxError:
        raise
    except Exception as ex:
        print(traceback.format_exc())


def _chunks(l, n):
    """(list, int) -> list

    Ritorna blocchi di `n` elementi in `l`
    """
    return [l[i:i+n] for i in range(0, len(l), n)]


def _categorie_per_indice(elenco_moduli):
    """(list of :py:class:`Modulo`) -> list

    Scorre `elenco_moduli`, ottiene un dizionario per categoria di modulo che
    contiene i moduli appartenenti a detta categoria; quindi scorre il
    dizionario ordinato per chiavi e ritorna una lista formata da liste il
    cui primo elemento è il nome della categoria ed il secondo è una lista di
    tuple il cui primo valore è il nome del modulo ed il secondo l'indirizzo

    Serve per popolare la barra destra delle pagine indice (elenco moduli per
    categorie)
    """
    dd = defaultdict(list)
    for modulo in elenco_moduli:
        dd[my_title(modulo.categoria)].append((modulo.nome, modulo.url))
    l = []
    for k in sorted(dd.keys()):
        l.append((k, dd[k]))
    return l


def get_categorie(file_categ):
    """
    Ottiene le categorie degli articoli

    :param file_categ: il file da leggere
    :return: una tupla con il nome della categoria in ordine alfabetico
    """
    if not os.path.exists(file_categ):
        moduli = sorted(elenco_per_indice(builder_conf['tran_dir']),
                        key=lambda x: x.nome.lower())
        return [(cat[0], cat[0]) for cat in _categorie_per_indice(moduli)]
    else:
        moduli = sorted([row.strip() for row in open(file_categ)])
        print()
        return [(m, m) for m in moduli]


def save_categorie(file_categ, lista_categ):
    """
    Sslva `lista_categ` in `file_categ`

    :param file_categ: il file su cui salvare (sovrascrive)
    :param lista_categ: l'elenco delle categorie da salvare
    :return:
    """
    with open(file_categ, 'w') as fh:
        fh.write('\n'.join(lista_categ))


def crea_nuovo_articolo(filetemplate, outfile, categoria, nome_modulo, scopo,
                        descrizione, data_pubb, aggiungi_a_indice, filecron):
    """
    Crea un file da utilizzare come base per la scrittura di un nuovo articolo

    :param filetemplate: il file template di partenza
    :param outfile: il file da creare per utilizzarlo nella traduzione
    :param categoria: la categoria dell'articolo
    :param nome_modulo: il nome del modulo (utilizzato nel jumbo)
    :param scopo: lo scopo del modulo (utilizzato nel jumbo)
    :param descrizione: incipit dell'articolo
    :param data_pubb: data pubblicazione da usare nella home
    :param aggiungi_a_indice: se `True` l'articolo si aggiunge alla tabella dei
                              moduli
    :param filecron: il file che traccia le data di pubblicazione degli
                     articoli (che verrà aggiornato con `data_pubb`,
                    `nome_modulo` e `scopo`
    :return: il percorso del file creato
    """
    titolo_articolo = "{} - {}".format(nome_modulo, descrizione)
    data_pubb = datetime.date.strftime(data_pubb, '%d.%m.%Y')
    subs = {
        "categ": categoria,
        "titolo_articolo": titolo_articolo,
        "descrizione_articolo": scopo,
        "data_pubb": data_pubb,
        "nome_modulo": nome_modulo
    }

    if not aggiungi_a_indice:
        subs['indicizza'] = r'\n<indicizza>no</indicizza>\n'
    else:
        subs['indicizza'] = ''  # se indicizzo è default non serve tag

    if filecron:
        with open(filecron, mode='a') as fh:
            fh.write('\n{}\t{}'.format(data_pubb, titolo_articolo))

    with open(filetemplate) as fhi:
        with open(outfile, mode='w') as fho:
            fho.write(string.Template(fhi.read()).safe_substitute(subs))
    return os.path.abspath(outfile)


def create_privacy_page(template_name: str) -> list:
    """
    :param template_name:
    :return:
    """
    moduli, categ_per_indice = _get_modules_and_categories_for_sidebar(
        builder_conf['tran_dir']
    )
    indice = Indice(moduli, 0, categ_per_indice, 0, 0)

    # Gestione sezione ultimi moduli aggiornati
    cronology_path = os.path.join(
            builder_conf['translated_modules_dir'],
            builder_conf["translated_modules_name"]
        )
    last_ten = _get_last_ten(cronology_path,
                             int(builder_conf['show_last_updated']), True)

    privacy_content = builder_conf['privacy_content']
    render_dic = {'indice': indice, 'last_ten': last_ten,
                  'privacy_content': privacy_content,
                  'titolo_pagina': 'Privacy (PyMOTW-it 3)'}

    build(template_name, render_dic,
          os.path.join(builder_conf["html_dir"],
                       os.path.basename(template_name)))
    return [f'\ncreata pagina privacy ({os.path.basename(template_name)})']


def crea_pagine_indice(template_name, file_indice, mod_per_pagina, footer):
    """(str, str, int, Footer)

    Crea le pagine indice, che contengono i teaser per 12 moduli ognuna
    """
    moduli = sorted(elenco_per_indice(builder_conf['tran_dir']),
                    key=lambda x: x.nome.lower())
    categ_per_indice = _categorie_per_indice(moduli)

    # Gestione sezione ultimi moduli aggiornati
    cronology_path = os.path.join(
            builder_conf['translated_modules_dir'],
            builder_conf["translated_modules_name"]
        )
    last_ten = _get_last_ten(cronology_path,
                             int(builder_conf['show_last_updated']), True)

    #  render_dic = dict()

    moduli_per_pagina = _crea_pagina_indice(
        moduli, builder_conf["modules_by_page"]
    )
    # La prima pagina in realtà non ha un valore di indice quindi non potrebbe
    pagine = len(moduli_per_pagina)-1
    for pagina, moduli in moduli_per_pagina.items():
        indice = Indice(moduli, footer, categ_per_indice, pagina, pagine)

        render_dic = {
            'indice': indice,
            'last_ten': last_ten,
            'titolo_pagina': 'Privacy (PyMOTW-it 3)'
        }
        fn = '{}{}.html'.format(
            file_indice, '_' + str(pagina) if pagina else ''
        )
        build(template_name, render_dic,
              os.path.join(builder_conf["html_dir"], fn))
    return


def _crea_pagina_indice(moduli, mpp):
    """Prepara i moduli che devono essere mostrati in ogni pagina indice

    :param list moduli: i moduli tradotti
    :param int mpp: il numero massimo di moduli per pagina
    :return: dict con chiavi i numeri pagina e valori gli oggetti Modulo
             contenuti
    """
    mpp = int(mpp)
    coda_moduli = deque(moduli)
    max_pagine = int(ceil(len(moduli) / mpp))
    diz = OrderedDict()
    for pagina in range(0, max_pagine):
        cnt = 0
        while cnt < mpp:
            if not coda_moduli:
                break
            if pagina not in diz:
                diz[pagina] = list()
            diz[pagina].append(coda_moduli.popleft())
            cnt += 1
    return diz


def crea_pagina_modulo(template_name: str, file_modulo: str,
                       footer: Footer, tag_ind: list,
                       log: list = None) -> tuple:
    """
    Crea la pagina per un modulo.

    :param template_name: il nome del modello per il rendering
    :param file_modulo: il file xml dal quale ricavare la pagina html
    :param footer: oggetto :py:class:`Footer` che contiene info da inserire
                   nel footer della pagina
    :param tag_ind: indici da usare per l'indice di spalla
    :param log: una lista che conterrà le info di log rilasciate dai metodi che
                compongono la pagina
    """
    indice, main_content, is_ind, vedi_anche, check_sintassi, zipfile = \
        xml2html.render_articolo(
            file_modulo, builder_conf["examples_dir"],
            builder_conf["zip_files_dir"], tag_ind, log, builder_conf
        )
    fn = os.path.splitext(os.path.basename(file_modulo))[0]
    modulo = Modulo.ottieni_modulo(builder_conf["tran_dir"], fn)
    m = DjModulo(indice, main_content, vedi_anche, modulo, footer, zipfile)

    fn += '.html'
    dic = {'modulo': m, 'titolo_pagina': f"{modulo.nome} (PyMOTW-it 3)"}

    build(template_name, dic, os.path.join(builder_conf["html_dir"], fn))
    return is_ind, check_sintassi


def get_cronologia(file_cronologia: str):
    """(str) -> list of tuple

    Ottiene i dati relativi alla data di pubblicazione dei moduli
    """
    retval = []
    for riga in open(file_cronologia).readlines():
        if not riga or not riga[0].isdigit():
            continue
        data, temp = riga.strip().split(" ", 1)
        nome, junk = temp.split('-', 1)
        retval.append((data, nome.strip()))
    return retval


def abbina_cronologia(cronologia, moduli, data_fmt='%d.%m.%Y'):
    """(list of tuple, Modulo)

    Cerca la data di pubblicazione del modulo, aggiorna l'oggetto se la
    trova
    """
    for modulo in moduli:
        isinstance(modulo, Modulo)
        for data, nome in cronologia:
            nome_alias = nome.split(":")
            if nome_alias[0].lower() == modulo.nome.lower().replace('_', '.'):
                modulo.data_pub = datetime.datetime.strptime(data, data_fmt)
                if len(nome_alias) == 2:
                    modulo.nome_per_rss = nome_alias[1]
                else:
                    modulo.nome_per_rss = nome_alias[0]
                break
        if not modulo.data_pub:
            print(modulo.nome)


def crea_feed_rss(base_path: str, outfile: str, title: str,
                  description: str, xml_declarations: list):
    """
    Scrive un feed rss contentente l'elenco dei moduli presenti nel sito

    :param base_path:
    :param outfile:
    :param title:
    :param description: non necessaria
    :param xml_declarations: dichiarazioni diverse da `<?xml version ...?>`
    :return:
    """
    moduli = elenco_per_indice(builder_conf['tran_dir'])
    cronology = os.path.join(
        builder_conf['translated_modules_dir'],
        builder_conf["translated_modules_name"]
    )
    abbina_cronologia(get_cronologia(cronology), moduli)
    moduli_ordinati = Modulo.ordina_per_data(moduli)
    folder = os.path.join(builder_conf["html_dir"]
                          if 'html_dir' in builder_conf
                          else r'/home/robby/tmpdebug')
    local_feed = os.path.join(folder, outfile)
    outfile = urljoin(base_path, outfile)
    feed = Feed(title, outfile, description, xml_declarations)
    for modulo in moduli_ordinati:
        assert isinstance(modulo, Modulo)
        link_guid = urljoin(base_path, modulo.url)
        item = FeedItem(
            title=modulo.nome_per_rss,
            lnk=link_guid,
            descr=xml2html.striphtml(modulo.descrizione),
            date=datetime.datetime.combine(
                modulo.data_pub, datetime.datetime.min.time(),
            ),
            guid=link_guid
        )
        feed.add_item(item)
        # print(modulo.nome, modulo.descrizione)
    logging.info(f"Inseriti {feed.count_items} elementi")
    with codecs.open(local_feed, mode='w', encoding='utf-8') as fh:
        fh.write(feed.get_feed())
    logging.info(f"Scritto {local_feed}")


def _get_last_ten(cronology_file: str,
                  nr_displayed: int, reverse: bool = True) -> List[lt.LastTen]:
    """
    Ottiene elenco degli ultimi moduli tradotti

    :param cronology_file: percorso completo file cronologia
    :param nr_displayed: numero elementi da visualizzare
    :param reverse: se `True` ritorna i più recenti
    """
    with open(cronology_file) as fh:
        last_ten = lt.lastten_factory(
            [row.strip() for row in fh.readlines()]
        )
    # nr_ultimi_agg = nr_displayed
    last_ten = last_ten[-nr_displayed:] \
        if len(last_ten) > nr_displayed else last_ten
    if reverse:
        last_ten.reverse()
    return last_ten


def _get_modules_and_categories_for_sidebar(tran_dir: str) -> tuple:
    modules = sorted(elenco_per_indice(tran_dir), key=lambda x: x.nome.lower())
    categories = _categorie_per_indice(modules)
    return modules, categories


def crea_tabella_indice(template_name: str):
    """
    Crea la pagina che contiene la tabella che riepiloga tutti i moduli

    :param template_name: il nome del modello per il rendering
    """
    cronology_path = os.path.join(
            builder_conf['translated_modules_dir'],
            builder_conf["translated_modules_name"]
        )
    last_ten = _get_last_ten(cronology_path,
                             int(builder_conf['show_last_updated']), True)

    moduli = sorted(elenco_per_indice(builder_conf['tran_dir']),
                    key=lambda x: x.nome.lower())
    categ_per_indice = _categorie_per_indice(moduli)
    indice = Indice(moduli, FOOTER, categ_per_indice, 0, 0)

    # corpo = ottieni_tabella(moduli)
    m = DjTabelleIndici(moduli, FOOTER)
    diz_indice = m.moduli_per_iniziale
    fn = 'indice_alfabetico.html'
    dic = {
        'modulo': m,
        'idx': diz_indice,
        'indice': indice,
        'last_ten': last_ten,
        'titolo_pagina': 'Privacy (PyMOTW-it 3)'
    }
    build(template_name, dic, os.path.join(builder_conf["html_dir"], fn))


def _sintassi(pn):
    return '%s [ind|tab|<nome_modulo>]' % os.path.basename(pn)


def rebuild_all():
    crea_pagine_indice(
        builder_conf["template_index_name"],
        builder_conf["file_indice"],
        builder_conf["modules_by_page"],
        FOOTER
    )
    crea_tabella_indice(builder_conf["template_tabalfa_name"])

    pattern = "%s/*.xml" % builder_conf['tran_dir']
    for choice in glob.glob(pattern):
        if not os.path.exists(choice):
            exit(0)
        print("Costruzione pagina {} in corso ...".format(
            os.path.basename(choice))
        )
        if 'riferimenti_' in choice:
            is_ind = crea_pagina_modulo(
                builder_conf["template_ref_name"], choice, FOOTER)
        else:
            is_ind = crea_pagina_modulo(
                builder_conf["template_module_name"], choice, FOOTER)
        # crea_pagina_modulo(TEMPLATE_MODULE_NAME, choice, FOOTER)


# def pubblica(moduli):
#     crea_pagine_indice(
#         builder_conf["template_index_name"],
#         builder_conf["file_indice"],
#         builder_conf["modules_by_page"],
#         FOOTER
#     )
#     crea_tabella_indice(builder_conf["template_tabalfa_name"])


def _norm_path(modulo: str, def_dir: str, def_ext: str = '.xml') -> str:
    """Ottiene un valido percorso per `modulo`"""
    if not modulo.endswith(def_ext):
        modulo += def_ext
    return os.path.abspath(os.path.join(def_dir, modulo))


# def _check_module_list(module_to_build: list, log: list) -> list:
#     transl_modules = elenco_per_indice(builder_conf['tran_dir'])
#     retval = []
#     for module in module_to_build:
#         if module.endswith('.xml'):
#             module = module.replace('.xml', '')
#         found = len([mod for mod in transl_modules if module == mod.nome])
#         if not found:
#             log.append(f"{module} non esiste o non è stato tradotto")
#             continue
#         retval.append(module)
#     return retval, log


# Funzioni da utilizzare se modulo chiamato
def build_module(moduli: list) -> tuple:
    """Funzione principale per i consumatori del modulo

    :param moduli: una lista di moduli da rendere (percorso completo)
    :return: log operazione, testo per verifica sintassi, percorso modulo
    """
    # Ottengo il percorso assoluto delle directory dei template django
    tmpdirs_norm = [os.path.abspath(folder)
                    for folder in builder_conf["template_dirs"].split(';')]

    imposta_param_django(tmpdirs_norm)
    log = []
    check_sintassi = None

    # modulo = None
    # moduli, log = _check_module_list(moduli, log)
    for modulo in moduli:
        modulo = _norm_path(modulo, builder_conf["tran_dir"])
        x = os.getcwd()
        logger.info(f'Elaborazione di {modulo}')
        if not os.path.exists(modulo):
            log.append(f"Modulo {modulo} non trovato")
            logger.info(f"Modulo {modulo} non trovato")
            continue
        if 'riferimenti_' in modulo:  # non fanno parte dei moduli
            is_ind, check_sintassi = crea_pagina_modulo(
                builder_conf["template_ref_name"],
                modulo, FOOTER,
                builder_conf["tag_summary"], log
            )
        else:
            is_ind, check_sintassi = crea_pagina_modulo(
                builder_conf["template_module_name"],
                modulo, FOOTER,
                builder_conf["tag_summary"], log
            )
        log.append(
            f"Costruzione pagina {os.path.basename(modulo)} terminata\n")
    return log, check_sintassi, modulo


def build_index():
    """Crea pagine indice ed il feed rss"""
    log = ['\nCreazione pagine indice']
    crea_feed_rss(
        builder_conf["rss_remote_root_folder"],
        builder_conf["rss_feed_name"],
        builder_conf["rss_feed_title"],
        builder_conf["rss_feed_descr"],
        builder_conf['rss_feed_directives'].split('\n')
    )
    crea_pagine_indice(
        builder_conf["template_index_name"],
        builder_conf["file_indice_name"],
        builder_conf["modules_by_page"],
        FOOTER
    )
    return log


def build_module_table():
    log = ['\nCreazione tabella moduli']
    crea_tabella_indice(builder_conf["template_tabalfa_name"])
    return log


if __name__ == '__main__':
    print("Utilizzare l'interfaccia web")
    print("Fine")
