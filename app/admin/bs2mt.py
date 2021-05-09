# bs2mt.py

from collections import namedtuple
import glob
import logging
import os
import re

__doc__ = "bs2mt.py"

logging.basicConfig(filename='/tmp/scan_alerts.txt', filemode="w",
                    level=logging.DEBUG)

GLOB_PATTERN = '../../translations'

tags = ['<avvertimento>', '<danger>', '<success>', '<note>']
Report = namedtuple('Report', 'filename tag lineno')


def _scan_alerts(filename: str):
    modules = []
    with open(filename) as fh:
        fn = os.path.basename(filename)
        logging.debug(f'Scanning {fn}')
        for i, line in enumerate(fh.readlines()):
            for tag in tags:
                if re.match(tag, line, re.IGNORECASE):
                    logging.info(f"Found {tag}, line {i+1}")
                    modules.append(Report(fn, tag, i+1))
            logging.info("\n")
    return modules


def scan_alerts(filepattern: str):
    result = []
    for filename in glob.glob(filepattern):
        result.extend(_scan_alerts(filename))
    report = sorted(result, key=lambda x: x.filename)
    for rep in report:
        print(f"{rep.filename:<30} {rep.lineno:>5} {rep.tag:<15}")
    print(' '.join(
        sorted(os.path.splitext(rep.filename)[0] for rep in result)))


if __name__ == '__main__':
    scan_alerts(GLOB_PATTERN + '/*.xml')
