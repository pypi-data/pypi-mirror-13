#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This code is distributed under the terms and conditions
# from the Apache License, Version 2.0
#
# http://opensource.org/licenses/apache2.0.php

import sqlite3
import pickle


class SqliteList(object):
    journal_mode = None
    autocommit = True

    def __init__(self, filename, journal_mode=None, autocommit=True):
        if journal_mode is not None:
            available = ['WAL', 'OFF', 'DELETE', 'TRUNCATE', 'PERSIST', 'MEMORY']
            if journal_mode.upper() not in available:
                raise ValueError('journal_mode must be one of %s' % available)
            self.journal_mode = journal_mode
        self.autocommit = autocommit

        if self.autocommit:
            self.db = sqlite3.connect(filename, isolation_level=None)
        else:
            self.db = sqlite3.connect(filename)

        self.cursor = self.db.cursor()
        self.current = 1
        self._prepare()

    def _prepare(self):
        if self.journal_mode is not None:
            self.cursor.execute('pragma journal_mode = %s;' % self.journal_mode)
        self.cursor.execute('create table if not exists tbl(id integer primary key, value);')
        self.cursor.execute('create unique index if not exists id_idx on tbl(id);')
        self.cursor.execute('pragma synchronous = off;')
        self.commit()

    def __getitem__(self, index):
        if not isinstance(index, (int, slice)):
            raise TypeError('list indices must be integers, not float')
        if isinstance(index, slice):
            if index.step is not None:
                raise IndexError('step is not allowed')
            offset = index.start or 0
            assert offset >= 0, 'negative indexes in slices are not supported'
            if index.stop is not None:
                # TODO: negative indexes support
                assert index.stop >= 0, 'negative indexes in slices are not supported'
                limit = index.stop - offset
                self.cursor.execute('select value from tbl order by id limit ? offset ?;', [limit, offset])
            else:
                self.cursor.execute('select value from tbl order by id limit -1 offset ?;', [offset])
            result = self.cursor.fetchall()
            if result is None:
                return []
            return [self.__unpack(item[0]) for item in result]
        else:
            order_by = ['desc', ''][index >= 0]
            if index < 0:
                index = abs(index + 1)
            self.cursor.execute('select value from tbl order by id %s limit 1 offset ?;' % order_by, [index])
            value = self.cursor.fetchone()
            if value is None:
                raise IndexError('list index out of range')
            return self.__unpack(value[0])

    def __setitem__(self, index, value):
        if not isinstance(index, int):
            raise TypeError('list indices must be integers, not float')
        order_by = ['desc', ''][index >= 0]
        if index < 0:
            offset = abs(index + 1)
        else:
            offset = index
        self.cursor.execute('select id from tbl order by id %s limit 1 offset ?;' % order_by, [offset])
        id_ = self.cursor.fetchone()
        if id_ is None:
            raise IndexError('list assignment index out of range')
        self.cursor.execute('update tbl set value = ? where id = ?;', [self.__pack(value), id_[0]])
        if self.autocommit:
            self.commit()

    def __delitem__(self, index):
        if isinstance(index, slice):
            start = index.start or 0
            stop = index.stop
            assert start >= 0, 'negative indexes in slices are not supported'
            if stop is not None:
                assert stop >= 0, 'negative indexes in slices are not supported'
                limit = stop - start
                self.cursor.execute('delete from tbl order by id limit ? offset ?;', [limit, start])
            else:
                self.cursor.execute('delete from tbl order by id limit -1 offset ?;', [start])
        else:
            if not isinstance(index, int):
                raise TypeError('list indices must be integers, not float')
            order_by = ['desc', ''][index >= 0]
            if index < 0:
                offset = abs(index + 1)
            else:
                offset = index
            self.cursor.execute('delete from tbl order by id %s limit 1 offset ?;' % order_by, [offset])
        if self.autocommit:
            self.commit()

    def __len__(self):
        self.cursor.execute('select count(1) from tbl;')
        return self.cursor.fetchone()[0]

    def __iter__(self):
        self.current = 1
        return self

    def __next__(self):
        self.cursor.execute('select id, value from tbl where id >= ? order by id limit 1;', [self.current])
        result = self.cursor.fetchone()
        if result is None:
            raise StopIteration
        self.current = result[0] + 1
        return self.__unpack(result[1])

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __bool__(self):
        self.cursor.execute('select id from tbl limit 1;')
        return bool(self.cursor.fetchone())

    @staticmethod
    def __pack(value):
        return sqlite3.Binary(pickle.dumps(value))

    @staticmethod
    def __unpack(packed):
        return pickle.loads(packed)

    def append(self, value):
        self.extend([value])

    def extend(self, lst):
        self.cursor.executemany('insert into tbl(value) values(?);', ([self.__pack(value)] for value in lst))
        if self.autocommit:
            self.commit()

    def pop(self, index=-1):
        order_by = ['desc', ''][index >= 0]
        if index < 0:
            offset = abs(index + 1)
        else:
            offset = index
        self.cursor.execute('select id, value from tbl order by id %s limit 1 offset ?;' % order_by, [offset])
        result = self.cursor.fetchone()
        if result is None:
            raise IndexError('pop from empty list')
        self.cursor.execute('delete from tbl where id = ?;', [int(result[0])])
        if self.autocommit:
            self.commit()
        return self.__unpack(result[1])

    def close(self):
        self.db.close()

    def flush(self):
        self.cursor.execute('delete from tbl;')
        self.commit()

    def commit(self):
        self.db.commit()


def open(filename, journal_mode=None, autocommit=True):
    return SqliteList(filename, journal_mode=journal_mode, autocommit=autocommit)
