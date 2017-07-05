#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROGRAM : importData
# AUTHOR  : codeunsolved@gmail.com
# CREATED : July 5 2017
# VERSION : v0.0.1

import os
import re

import xlrd

from lib.sqlConnector import PostgresqlConnector
import config


def read_xls(path_xls):
    def read_table(tab_name):
        tab_data = []

        tab = wb.sheet_by_name(tab_name)
        nrows = sheet.nrows

        for i in range(nrows):
            if i == 0:
                continue
            tab_data.append(tab.row_values(i))
        return tab_data

    data = {}
    wb = xlrd.open_workbook(path_xls)
    for key in :
        data[key] = read_table(key)


def import_data(data):
    


tab_list = ['research', 'tumor', 'gene', 'variant', 'prognosis', 'subgroup', 'association']