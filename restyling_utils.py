# restyling_utils.py

import logging
import os
from shutil import copy

__doc__ = "restyling_utils.py"

logging.basicConfig(level=logging.DEBUG)

REDIRECT_TEMPLATE = """<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="refresh" content="0; url='{dest_path}/{html_file}'" />
  </head>
  <body>
    <h3>
        Pagina trasferita a <a href="{dest_path}/{html_file}">questo indirizzo</a>.
    </h3>
  </body>
</html>
"""


def build_redirects(in_folder: str, out_folder: str,
                    template: str, params: dict):
    """
    Copia in file .html in `in_folder` in `out_folder`, sostituisce il loro
    contenuto in `in_folder` con un markup che redirige verso il corrispondente
    file copiato in `out_folder`

    :param in_folder: contiene i file sorgente da trattare
    :param out_folder: directory dove copiare i file originali oggetto di
                       redirezione
    :param template: il template con il quale generare il markup di redirezione
                     che sostituisce il contenuto nel file originale
    :param params: dest_path contiene il percorso relativo della directory in
                   **remoto** che conterrà i file originali
    :return:
    """
    # per ogni file originale
    for fn in [fn for fn in os.listdir(in_folder)
               if fn.lower().endswith('.html')]:
        # Copia in out_folder il file originale
        src = os.path.abspath(os.path.join(in_folder, fn))
        target = os.path.abspath(os.path.join(out_folder, fn))
        logging.info(f"Copying {src} to \n {target}")
        copy(src, target)
        # Sostituzione del contenuto del file in in_folder
        # con il template di redirezione
        params['html_file'] = fn
        with open(src, 'w') as fh:
            fh.write(template.format(**params))
            logging.info(f"Writing redirect info to {src}")


if __name__ == '__main__':
    params = {"dest_path": '2', 'html_file': ''}
    # print(REDIRECT_TEMPLATE.format(**x))
    build_redirects(r'/home/robby/oldsite', r'/home/robby/2redirect',
                    REDIRECT_TEMPLATE,  params)
