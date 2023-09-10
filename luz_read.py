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
    seqs = []
    for tup in datas:
        fname, data = tup
        seq = do_print(fname, data)
        seqs.append(seq)
    return seqs

def do_print(fname, data):
    if fname:
        print("#", fname)
    lines = [line.split("\t") for line in data]
    seq = get_from_quads(lines)
    assert seq is not None, "Invalid: " + fname
    # Get the differences
    last = [-1, -1, -1]
    prev_day = -1
    dare = []
    for dttm, abs_day, tup in seq:
        i_date, trip = tup
        a_sum = 0
        for idx in range(3):
            a_sum += float(trip[idx] - last[idx])
        if prev_day >- 1:
            smart_calc((dttm, abs_day, (i_date, a_sum)), prev_day, dare)
            #print(i_date, a_sum)
        last = trip
        prev_day = abs_day
    for tup in dare:
        #print(tup[2:])
        i_date, a_sum = tup[2]
        print(i_date, f"{a_sum:8.3f}")
    return seq

def smart_calc(infos, prev_day, dare:list):
    dttm, abs_day, tup = infos
    i_date, a_sum = tup
    # Inject estimations if day now and before are not consecutive
    if abs_day - prev_day <= 0:
        return False
    if abs_day - prev_day <= 1:
        dare.append((dttm, abs_day, (i_date, a_sum)))
        return False
    dim = a_sum / (abs_day - prev_day)
    for day in range(prev_day + 1, abs_day + 1):
        new = datetime.datetime.fromordinal(day)
        s_date = new.strftime("%Y-%m-%d")
        #print(":::___", i_date, s_date, a_sum, dim)
        s_date += " ---"
        if day == abs_day:
            s_date = i_date.replace(' ', '*')
        dare.append((new, day, (s_date, dim)))
    return True

def get_from_quads(lines):
    seq = []
    last_day = -1
    for s_date, s_val1, s_val2, s_val3 in lines:
        dttm = datetime.datetime.strptime(s_date, "%Y-%m-%d")
        info = " " + dttm.strftime("%a")
        val1, val2, val3 = int(s_val1), int(s_val2), int(s_val3)
        #print(":::", s_date + info, val1, val2, val3)
        abs_day = dttm.toordinal()
        item = (dttm, abs_day, (s_date + info, [val1, val2, val3]))
        if abs_day < last_day:
            print("Bogus date (not sorted):", s_date)
            return None
        if abs_day == last_day:
            # Just ignore duplicates
            continue
        last_day = abs_day
        seq.append(item)
    return seq

if __name__ == "__main__":
    main()
