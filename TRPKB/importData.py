#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROGRAM : importData
# AUTHOR  : codeunsolved@gmail.com
# CREATED : July 5 2017
# VERSION : v0.0.1

import sys
import xlrd


def read_xls(path_xls, kb):
    def read_table(tab_name):
        tab_data = []

        sheet = wb.sheet_by_name(tab_name)
        nrows = sheet.nrows

        for i in range(nrows):
            if i == 0:
                continue
            tab_data.append(sheet.row_values(i))
        return tab_data

    tab_snp = ['research', 'tumor', 'gene', 'variant', 'prognosis', 'subgroup', 'association']
    tab_exp = ['research', 'tumor', 'gene', 'prognosis', 'subgroup', 'association']

    data = {}
    wb = xlrd.open_workbook(path_xls)

    if kb == 'snp':
        tab_list = tab_snp
    elif kb == 'exp':
        tab_list = tab_exp

    for key in tab_list:
        data[key] = read_table(key)

    return data


def check_association(data, kb):
    def check_range(val, i, flag):
        if val:
            try:
                v_1, v_2 = [float(x) for x in val.split('-')]
            except Exception as e:
                print("No.{} {}: {}?".format(i + 2, flag, val))
            else:
                if v_1 >= v_2:
                    print("No.{} {}: {}".format(i + 2, flag, val))

    if kb == 'snp':
        u_i = 14
        m_i = 19
    elif kb == 'exp':
        u_i = 13
        m_i = 18

    for i, x in enumerate(data['association']):
        u = x[u_i]
        m = x[m_i]

        check_range(u, i, 'U')
        check_range(m, i, 'M')


if __name__ == '__main__':
    path_xls = sys.argv[1]
    kb = sys.argv[2]

    data = read_xls(path_xls, kb)
    check_association(data, kb)
