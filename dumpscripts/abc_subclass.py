# abc_subclass.py

import abc
from abc_base import PluginBase


class SubclassImplementation(PluginBase):

    def load(self, input):
        return input.read()

    def save(self, output, data):
        return output.write(data)


if __name__ == '__main__':
    print('Sottoclasse:', issubclass(RegisteredImplementation,
                                  PluginBase))
    print('Istanza:', isinstance(RegisteredImplementation(),
                                  PluginBase))
