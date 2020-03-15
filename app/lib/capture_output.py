#!/usr/bin/env python
# -*- coding: utf-8 -*-
# capture_output.py

import subprocess
import os
import re


__doc__ = """
Cattura l'output degli script di esempio

L'idea è di non inserire il risultato degli script nella pagina html con 
copia/incolla ma dinamicamente eseguendo lo script stesso. 
"""
__version__ = "0.2"
__changelog__ = """
2018-08-15 - Refactoring della classe, ora è possibile catturare l'output di
comandi di shell diversi da python
"""


class CaptureOutputException(Exception):
    pass


class CaptureOutputScript(object):
    """Cattura l'output degli script di esempio

    L'idea è di non inserire il risultato degli script nella pagina html con
    copia/incolla ma dinamicamente eseguendo lo script stesso.

    **Per ora funziona solo in ambienti Unix**
    """
    prompts = tuple('$#')  # Possibili prompt
    pyintpattern = re.compile(r'.*python[\d{1}]?[\.{1}]?[\d{1}]?$',
                              re.IGNORECASE)
    # def_interpreter = 'python3'

    def __init__(self, shellcmd=None, script_name=None):
        """([str] [,str])

        :param shellcmd: Il nome della console da chiamare (def. bash)
        :param script_name: Il nome dello script che verrà creato come
                            wrapper per l'esecuzione del comando
        """
        self._output = list()
        # self._pycommand = None
        self._shell_command = None
        self._cmdline = list()
        self._shell_cmd = '/bin/bash' or shellcmd
        self._script_name = '_pyrunner.sh' or script_name

    @property
    def output(self):
        """Ritorna il risultato del comando eseguito"""
        return '\n'.join(self._output)

    def _create_shell_script(self, path):
        """(str [,str]) -> str

        Crea un file bash con all'interno il codice per eseguire il comando.

        :param path: il percorso su cui scrivere il file bash
        :return: il nome dello script bash da eseguire
        """
        # TODO: gestire la riga di shebang non boilerplate
        wkdir = os.path.abspath(path)
        script = os.path.join(wkdir, self._script_name)
        code = [
            "#!/usr/bin/env bash",
            'cd ' + wkdir,
            ' '.join(self._cmdline)
        ]
        with open(script, mode='w') as fh:
            fh.write('\n'.join(code))
        return script

    def _parse_cmd_line(self, cmdline):
        """(str) ->  bool

        Elabora la riga di comando tentando di ottenere il comando e gli
        argomenti

        Se la riga non inizia con un prompt noto ritorna False, True altrimenti
        """
        if not cmdline.startswith(CaptureOutputScript.prompts):
            return False
        self._output.append("$ " + cmdline[1:].strip() + '\n')
        self._cmdline = re.split(r'\s+', cmdline[1:].strip())
        return True

    def run(self, cmdline, workfolder=None, substitute=None, decoder='utf-8'):
        """(str [,str] -> str

        Crea uno script al cui interno inserisce la riga di comando da
        eseguire

        :param cmdline: la riga di comando da eseguire
        :param substitute: lista di tuple che contiene valori letterali
                           da sostituire ed il valore di rimpiazzo
                           nell'output ritornato (per questioni di privacy/
                           sicurezza non si vuole stampare l'intero percorso
                           del file system se richiesto, inoltre un percorso
                           lungo può generare confusione nel lettore
        :param: il tipo di decodifica per il file
        :return: l'output del comando o l'eventuale errore verificatosi
        """
        if not self._parse_cmd_line(cmdline):
            return list('Impossibile il parsing della riga di comando')

        sh_script = self._create_shell_script(workfolder)
        try:
            self._output.append(subprocess.check_output(
                [self._shell_cmd, sh_script], shell=False,
                stderr=subprocess.STDOUT
            ).decode(decoder))
        except subprocess.CalledProcessError as suberr:
            self._output.append(suberr.output.decode(decoder))

        if substitute:
            self._subtext(substitute)
        return self._output

    def _subtext(self, substitute):
        """(list of tuple)

        Sostituisce il primo elemento con il secondo per ogni voce nella tupla
        nell'output del comando

        :param substitute: i dati da sostituire
        :return: il testo modificato
        """
        try:
            for item in substitute:
                src, target = item
                for i, line in enumerate(self._output):
                    self._output[i] = line.replace(src, target)
        except:
            raise CaptureOutputException("Errore in sostituzione output")


if __name__ == '__main__':
    # Qualche verifica
    cmdline = "$ find extension -name '*.py'"
    cmdline = '# python3 -m unittest -v unittest_expectedfailure.py'
    #cmdline = r'# python3 -m unittest unittest_simple.py'
    wkdir = '../dumpscripts'
    c = CaptureOutputScript()
    output = c.run(cmdline, wkdir)
    print(output)


