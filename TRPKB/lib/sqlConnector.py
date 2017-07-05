#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROGRAM : sqlConnector
# AUTHOR  : codeunsolved@gmail.com
# CREATED : June 14 2017
# VERSION : v0.0.1

import psycopg2


class DoesNotExist(Exception):
    def __init__(self):
        super(DoesNotExist, self).__init__()


class OneMoreRecords(Exception):
    def __init__(self, message):
        super(OneMoreRecords, self).__init__(message)


class PostgresqlConnector(object):
    def __init__(self, config):
        """Config example

        postgresql_config_example = {
            'user': 'username',
            'password': 'password',
            'host': '127.0.0.1',
            'database': 'database'
        }
        """
        self.conn = psycopg2.connect(**config)
        self.cursor = self.conn.cursor()

    def get(self, tab, select_cols, where_cols, vals):
        where_cols_vals = zip(where_cols, vals)
        get_grammar = "SELECT {} FROM \"{}\" WHERE {}".format(
            ', '.join(select_cols), tab, ' AND '.join(["{} = {}".format(x, y) for x, y in where_cols_vals]))
        self.cursor.execute(get_grammar)
        if self.cursor.rowcount == 1:
            return self.cursor.fetchone()
        elif self.cursor.rowcount == 0:
            raise DoesNotExist()
        else:
            raise OneMoreRecords("get {} records! only one excepted.".format(self.cursor.rowcount))

    def insert(self, tab, cols, vals):
        insert_grammar = "INSERT INTO \"{}\"({}) VALUES({});".format(
            tab, ', '.join(cols), ', '.join(['%s'] * len(cols)))
        self.cursor.execute(insert_grammar, vals)
        self.conn.commit()

    def update(self, tab, set_cols, where_cols, vals):
        update_grammar = "UPDATE \"{}\" SET {} WHERE {}".format(
            tab, ', '.join(["{} = %s".format(x) for x in set_cols]),
            ' AND '.join(["{} = %s".format(x) for x in where_cols]))
        self.cursor.execute(update_grammar, vals)
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()
