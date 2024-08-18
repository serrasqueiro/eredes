#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c)2023  Henrique Moreira

""" reliq_luz.py -- leitura a partir de e-redes
Copied from my private branch, https://github.com/serrasqueiro/leituras
at branch `new/eredes_AUTO`
"""

import sys
import datetime
import openpyxl

OUT_TEXT = "out.txt"

def main():
    main_script(sys.argv[1:])

def main_script(args):
    param = args if args else ["Leituras_20230216.xlsx"]
    fname = param[0]
    datas = reader(fname)
    first, sec = datas
    assert first, "Data!"
    third, header = row_scan(sec)
    print("#", header)
    # Sorted as e.g.
    #	[('2023-02-14', [175.0, 107.0, 248.0]), ('2023-02-15', [178.0, 109.0, 253.0])]
    new = sorted(third, key=lambda x: x[0], reverse=False)
    all_seq = dumper(new)
    store_text(OUT_TEXT, all_seq)
    return first, third

def store_text(fname:str, seq:list):
    """ Output to 'fname' the sequence, in tsv """

    def myline(this):
        watts = this[1]
        item = [this[0]] + [f"{aval:.0f}" for aval in watts]
        #print("### item:", item)
        astr = '\t'.join(item)
        return astr

    res = "# data\tVazio\tPonta\tCheias\n"
    res += "\n".join([myline(ala) for ala in seq]) + "\n"
    if not fname:
        return False
    with open(fname, "w", encoding="ascii") as fdout:
        fdout.write(res)
    return True

def dumper(seq):
    all_seq = []
    last = []
    for item in seq:
        there = shown(item)
        s_date, vals = there[0], there[-1]
        if last:
            comm = [vals[0] - last[0], vals[1] - last[1], vals[2] - last[2]]
        else:
            comm = []
        last = vals
        dttm = datetime.datetime.strptime(s_date, "%Y-%m-%d")
        info = " " + dttm.strftime("%a")
        if comm:
            print(s_date + info, vals, sum(comm))
        else:
            print(s_date + info, vals, "--")
        all_seq.append((s_date, vals))
    return all_seq

def shown(tups):
    """ Shown one item in 'eredes' """
    item = tups
    if item[3] == "VALIDA":
        del item[3]
    s_item = str(item)
    dttm, op_str, act_str, s_unit, rest1, rest2, rest3 = item
    assert op_str in ("Real",), f"op_str='{op_str}', s_item={s_item}"
    assert act_str in ("Activa", "OP"), f"act_str unexpected: {item}"
    s_date = dttm.strftime("%Y-%m-%d")
    vals = [float(rest1), float(rest2), float(rest3)]
    #print(s_date, vals)
    return s_date, vals

def row_scan(rows) -> tuple:
    res, state = [], "I"
    header = []
    for _, row in rows:
        _, text, _ = row[0]
        if "Data da" in text:
            # Vazio, Ponta, Cheia -- last 3 columns!
            header = [ala for _, ala, _ in [row[0]] + row[-3:]]
            state = "F"
            continue
        if state != "F":
            continue
        data = [tup[2] if tup[2] else tup[1] for tup in row]
        res.append(data)
    return res, header

def reader(fname) -> tuple:
    wbk = openpyxl.open(fname, read_only=True, data_only=True)
    sht = wbk["Leituras"]
    mor, cpe = sht[1][1].value, sht[2][1].value
    print("Morada:", mor)
    assert cpe.startswith("PT",)
    return sht, [(idx, line_data(ala)) for idx, ala in enumerate(sht, 1)]

def line_data(row):
    res = [formatter(cell, col) for col, cell in enumerate(row, 1)]
    return res

def formatter(cell, col):
    adate = cell.value
    try:
        dttm = datetime.datetime.strptime(adate, "%d/%m/%Y") if col == 1 else ""
    except ValueError:
        dttm = ""
    sval = "" if cell.data_type == 'n' else cell.value
    if sval.startswith("V") and sval.endswith("lida"):
        sval = "VALIDA"
    if not dttm:
        if "Operador" in sval:
            sval = "OP"
        if "Energia" in sval:
            sval = "kWh"
    res = (cell.data_type, sval, dttm)
    return res

if __name__ == "__main__":
    main()
