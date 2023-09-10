#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c)2023  Henrique Moreira

""" luz_read.py -- leitura de TSV (3: Vazio+Ponta+Cheias)
"""

# pylint: disable=missing-function-docstring

import sys
import os
import datetime


def main():
    main_script(sys.argv[1:])

def main_script(args):
    param = args if args else ["raw_data"]
    if len(param) > 1 or param[0].startswith("-"):
        print("Too many parameters: enter only the directory.")
        return None
    code = runner(param[0])
    return code

def runner(a_dirname):
    files = [
        os.path.realpath(os.path.join(a_dirname, ala.name)) for ala in os.scandir(a_dirname) if ala.is_file() and ala.name.endswith(".tsv")
    ]
    if not files:
        print("Bummer, no .tsv files to dump!")
        return 2
    dumper(files)
    return 0

def dumper(files:list):
    datas = []
    for fname in files:
        with open(fname, "r", encoding="ascii") as fdin:
            tup = (
                fname,
                [line.rstrip() for line in fdin.readlines() if not line.startswith("#")]
            )
        datas.append(tup)
    for tup in datas:
        fname, data = tup
        do_print(fname, data)
    return True

def do_print(fname, data):
    if fname:
        print("#", fname)
    lines = [line.split("\t") for line in data]
    for s_date, s_val1, s_val2, s_val3 in lines:
        dttm = datetime.datetime.strptime(s_date, "%Y-%m-%d")
        info = " " + dttm.strftime("%a")
        val1, val2, val3 = int(s_val1), int(s_val2), int(s_val3)
        print(":::", s_date + info, val1, val2, val3)
    return True

if __name__ == "__main__":
    main()
