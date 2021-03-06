# gc_get_referents_cycles.py

import gc
import pprint
import queue


class Graph(object):

    def __init__(self, name):
        self.name = name
        self.next = None

    def set_next(self, next):
        print('Collegamento nodi {}.next = {}'.format(self, next))
        self.next = next

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.name)

# Costruisce un ciclo di Grafi
one = Graph('uno')
two = Graph('due')
three = Graph('tre')
one.set_next(two)
two.set_next(three)
three.set_next(one)

print()

seen = set()
to_process = queue.Queue()

# Si parte con una catena di oggetti vuota ed il Grafo tre.
to_process.put(([], three))

# Cerca dei cicli, costruendo la catena di oggetti per ogni oggetto che
# viene trovato nella coda in modo che si possa stampare l'intero ciclo quando
# si finisce
while not to_process.empty():
    chain, next = to_process.get()
    chain = chain[:]
    chain.append(next)
    print('In esame:', repr(next))
    seen.add(id(next))
    for r in gc.get_referents(next):
        if isinstance(r, str) or isinstance(r, type):
            # Ignorastringhe e classi
            pass
        elif id(r) in seen:
            print
            print('Trovato un ciclo per {}:'.format(r))
            for i, link in enumerate(chain):
                print('  {}: '.format(i), end=' ')
                pprint.pprint(link)
        else:
            to_process.put((chain, r))

