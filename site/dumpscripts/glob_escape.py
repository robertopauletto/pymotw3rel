# glob_escape.py

import glob

specials = '?*['

for char in specials:
    pattern = 'dir/*' + glob.escape(char) + '.txt'
    print('Ricerca di: {!r}'.format(pattern))
    for name in sorted(glob.glob(pattern)):
        print(name)
    print()
