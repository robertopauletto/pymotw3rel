# con_personalizzazioni_sito/sitecustomize.py

print('Caricamento di sitecustomize.py')

import site
import platform
import os
import sys

path = os.path.join('/opt',
                    'python',
                    sys.version[:3],
                    platform.platform(),
                    )
print('Si aggiunge il nuovo percorso', path)

site.addsitedir(path)
