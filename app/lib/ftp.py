# ftp.py

from collections import namedtuple
import ftplib
import logging
import os
import pathlib
import re
from typing import Union, Tuple, List

from dotenv import load_dotenv

__doc__ = "Trasferisce i file per il sito online"


load_dotenv(dotenv_path='../../.env', override=True)
PORT = int(os.getenv('PYMOTW_FTP_PORT'))
PW = os.getenv('PYMOTW_FTP_PW')
USER = os.getenv('PYMOTW_FTP_USER')
URL = os.getenv('PYMOTW_FTP_URL')
REMOTE_DIR = os.getenv('PYMOTW_FTP_REMOTE_DIR')


RemoteFile = namedtuple('RemoteFile', 'isdir, user, length, dt name')


def upload(url: str, user: str, pw: str, to_upload: List[Tuple[str, str]],
           remote_folder: str = '/', port: int = 21):
    """

    :param url: risorsa ftp
    :param user: utene
    :param pw: password
    :param remote_folder: directory remota
    :param to_upload: lista di tuple con percorsi locali e nomi file remoti
    :param port: porta
    :return:
    """
    ftp = ftplib.FTP(url)
    ftp.port = port
    ftp.login(user, pw)
    ftp.cwd(remote_folder)
    try:
        for loc, remote in to_upload:
            with open(loc, 'wb') as fh:
                ftp.storbinary('STOR ' + remote, fh )
    except IOError as ioerr:
        msg = f"Errore trasferendo {loc}\n{ioerr}"
        raise IOError(msg)


def listdir(url: str, user: str, pw: str, remote_folder: str = '/'
            , port: int = 21) -> list:
    result = list()

    def _cb(item):
        flds = re.split(r'\s+', item)
        isdir = flds[0].startswith('d')
        user = flds[3]
        length = flds[4]
        dt = flds[5:8]
        fn = flds[-1]
        result.append(RemoteFile(isdir, user, length, dt, fn))

    with ftplib.FTP(url) as ftp:
        #  ftp.set_debuglevel(3)
        ftp.port = port
        ftp.login(user, pw)
        ftp.cwd(remote_folder)
        try:
            ftp.dir(_cb)
            return result
        except IOError as ioerr:
            msg = f"Errore"
            raise IOError(msg)
        except Exception:
            raise


if __name__ == '__main__':
    result = listdir(URL, USER, PW, REMOTE_DIR)
    print(result)


