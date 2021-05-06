#!/usr/bin/env python
# -*- coding: utf-8 -*-

__date__=''
__version__='0.1'
__doc__="""Contiene dati da inserire in un footer
Versione %s %s
""" % ( __version__, __date__ )


class Footer:
    """Contiene dati da inserire in un footer"""
    def __init__(self, nome: str, periodo: str, data_agg: str, email: str):
        self.nome_sito = nome
        self.periodo = periodo
        self.data_agg = data_agg
        self.email = email
