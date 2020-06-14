# esempio_trace/recurse.py

def recurse(level):
    print('recurse({})'.format(level))
    if level:
        recurse(level - 1)


def not_called():
    print('Questa funzione non viene mai chiamata.')
