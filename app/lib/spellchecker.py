# spellchecker

import os

import textblob



t = "Una prova di controllo orografico co qualche erore di tropo od anche"


def check(text: str, language: str = 'it-IT'):
    blob = textblob.TextBlob(t)
    print(blob.detect_language())
    print(blob.correct())


if __name__ == '__main__':
    check(t)
