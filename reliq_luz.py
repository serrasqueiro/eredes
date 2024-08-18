#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c)2023, 2024  Henrique Moreira
#
# reader of e-redes Leituras_...xlsx

import sys
import datetime
import openpyxl

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
    dumper(new)
    return first, third

def dumper(seq):
    last = []
    for idx, item in enumerate(seq, 1):
        there = shown(item, idx)
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

def shown(tups, idx):
    item = tups
    if item[3] == "VALIDA":
        del item[3]
    valid_ops = ("OP", "Cliente")
    s_item = str(item)
    #print("DEBUG:", idx, "item:", item, f"(len={len(item)})")
    dttm, op_str, act_str, s_unit, rest1, rest2, rest3 = item
    assert op_str in valid_ops, f"op_str='{op_str}', s_item={s_item},\n\nNot in: {valid_ops}"
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
        if "Operador" in sval or (col == 2 and sval == "Real"):
            sval = "OP"
        if "Energia" in sval:
            sval = "kWh"
    res = (cell.data_type, sval, dttm)
    return res

if __name__ == "__main__":
    main()
