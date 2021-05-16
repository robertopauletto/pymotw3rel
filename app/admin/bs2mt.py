# bs2mt.py

from collections import namedtuple
from datetime import datetime
import glob
import logging
import os
import re
from shutil import copy
from typing import Generator, Union, Any, List, Tuple

__doc__ = "bs2mt.py"

logging.basicConfig(filename='/tmp/scan_alerts.txt', filemode="a",
                    level=logging.DEBUG)

TRAN_FOLDER_PATTERN = '../../translations'
TRAN_BK_ROOT = '/home/robby/pmtow3tranbk'

vowels = 'aeiou'
tags = ['<avvertimento>', '<danger>', '<success>', '<note>']
Report = namedtuple('Report', 'filename tag lineno')


def _get_filenames(filepattern: str) -> Generator:
    for filename in glob.glob(filepattern):
        yield os.path.abspath(filename)


def _print_report(results: List[Report],
                  sort_by_filename: bool = True,
                  to_log: bool = True):
    if sort_by_filename:
        report = sorted(results, key=lambda x: x.filename)
    for rep in report:
        output = f"{rep.filename:<30} {rep.lineno:>5} {rep.tag:<15}"
        if to_log:
            logging.info(output)
        else:
            print(output)


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
    for filename in _get_filenames(filepattern):
        result.extend(_scan_alerts(filename))
    _print_report(result, True)
    print(' '.join(
        sorted(os.path.splitext(rep.filename)[0] for rep in result)))


def fix_conj(filepattern: str, tran_fld: str, bkroot_fld: str, preview: bool):
    conj_re = re.compile(r'\s[aeio]d\s[a-zA-Z]')
    reports = []
    filenames = sorted(_get_filenames(filepattern), key=lambda x: x.lower())
    for filename in filenames:
        logging.info(f"Parsing {filename}:")
        reports.extend(_fix_conj(filename, conj_re))
    diz_reports = _get_dict_from_conj_reports(reports)
    _sub_conj(diz_reports, tran_fld, bkroot_fld, preview)


def _sub_conj(results: dict, tran_folder: str,
              bk_folder_root: str, preview: bool = True):
    bk_folder = f"{bk_folder_root}-"\
                f"{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    if not preview:
        os.mkdir(bk_folder)
    for filename, result in results.items():
        bk_path = os.path.join(bk_folder, filename)
        tr_path = os.path.join(TRAN_FOLDER_PATTERN, filename)
        if not preview:
            if not os.path.exists(bk_path):
                copy(tr_path, bk_path)
        for occurrences in result.values():
            if len(occurrences) > 1:
                for occurrence in occurrences[1:]:
                    logging.info(f"Ignoring {occurrence['summary']}")
                    print(f"Ignoring {occurrence['summary']}")
            if not preview:
                _make_sub(tr_path, occurrences[0])


def _make_sub(filename: str, occurrence: dict):
    logging.info(f"Performing subs for {filename}:")
    with open(filename) as fh:
        lines = [line for line in fh.readlines()]

    logging.info(f"Old line: {lines[occurrence['row']-1]}")
    logging.info(f"Subbing : {occurrence['summary']}")
    newline = lines[occurrence['row']-1].replace(
        occurrence['string'],
        occurrence['string'][:2] + occurrence['string'][3:], 1
    )
    lines[occurrence['row'] - 1] = newline
    logging.info(f"New line: {lines[occurrence['row']-1]}")

    with open(filename, mode='w') as fh:
        fh.write(''.join(lines))


def _fix_conj(filename: str, conj_re: re.Pattern):
    result = []
    with open(filename) as fh:
        for i, line in enumerate(fh.readlines()):
            occurrences = _find_and_replace_conj(
                line.strip(), conj_re, i+1, filename)
            if occurrences:
                result.extend(occurrences)
    logging.info(f"{len(result)} occurrences")
    return result


def _find_and_replace_conj(line: str, conj_re: re.Pattern, lineno: int,
                           filename: str) -> list:
    occurrences = []
    for m in conj_re.finditer(line):
        occ = m.string[m.start():m.end()]
        if occ[1].lower() == occ[-1].lower():
            logging.info(f"Mantenuta 'd' eufonica ({occ})")
            continue
        elif line[m.start()+1:].lower().startswith('ad esempio'):
            logging.info(f"Mantenuta espressione per convenzione {occ}")
            continue
        elif occ[-1] not in vowels:
            continue
        else:
            start = m.start() - 15 if m.start() > 15 else 0
            end = m.end() + 15 if m.end() + 15 <= len(line) else 0
            if end:
                context = m.string[start:end]
            else:
                context = m.string[start:]
            occurrences.append({
                'filename': os.path.basename(filename),
                'string': line[m.start():m.end()],
                'context': f"|Occ: {occ}| / ...{context}...",
                'row': int(lineno),
                'start': m.start(),
                'end': m.end(),
                'summary': f"Row {lineno:>5}: from {m.start():>5} "
                           f"to {m.end():>5} Occ: {occ}| / ...{context}..."
            })
    return occurrences


def _get_dict_from_conj_reports(results: List[Report]):
    retval = dict()
    for report in results:
        if report['filename'] not in retval:
            retval[report['filename']] = {}
        if report['row'] not in retval[report['filename']]:
            retval[report['filename']][report['row']] = []
        retval[report['filename']][report['row']].append(report)
    return retval


if __name__ == '__main__':
    # scan_alerts(GLOB_PATTERN + '/*.xml')
    fix_conj(
        TRAN_FOLDER_PATTERN + '/[s]*.xml',
        TRAN_FOLDER_PATTERN,
        TRAN_BK_ROOT,
        False
    )
