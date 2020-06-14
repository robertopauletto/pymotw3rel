# con_personalizzazioni_utente/usercustomize.py

print('Caricamento di usercustomize.py')

import site
import platform
import os
import sys

path = os.path.expanduser(os.path.join('~',
                                       'python',
                                       sys.version[:3],
                                       platform.platform(),
                                       ))
print('Aggiunta nuovo percorso', path)

site.addsitedir(path)
