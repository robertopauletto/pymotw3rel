# shutil_make_archive.py

import logging
import shutil
import sys
import tarfile

logging.basicConfig(
    format='%(message)s',
    stream=sys.stdout,
    level=logging.DEBUG,
)
logger = logging.getLogger('pymotw')

print('Creazione archivio:')
shutil.make_archive(
    'example', 'gztar',
    root_dir='..',
    base_dir='shutil',
    logger=logger,
)

print('\nContenuto archivio:')
with tarfile.open('example.tar.gz', 'r') as t:
    for n in t.getnames():
        print(n)
