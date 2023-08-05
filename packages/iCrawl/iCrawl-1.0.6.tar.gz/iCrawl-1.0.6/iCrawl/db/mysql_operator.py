#!/usr/bin/env python
# -*- coding:utf8 -*-
"""
mysql-connector-python的游标操作封装
提供全部的数据库简单操作
"""

import string

import mysql.connector as dblib
import mysql.connector.cursor as dblib_cursor
from iCrawl.excep.mysql_exception import ExecuteNotChooseError


class MySQLCursorDict(dblib_cursor.MySQLCursor):
    def _row_to_python(self, rowdata, desc=None):
        row = super(MySQLCursorDict, self)._row_to_python(rowdata, desc)
        if row:
            return dict(zip(self.column_names, row))
        return None


def fix_sql(sql, params):
    if sql is None:
        return sql

    if params is not None and isinstance(params, dict):
        for k in params.keys():
            v = params.get(k, '')
            s1 = "%" + "(%s)" % k
            s2 = "'%s'" % v
            sql = sql.replace(s1, s2)
    sql = sql.replace('\n', ' ').replace('\t', ' ').replace('  ', ' ').replace('  ', ' ').\
        replace('  ', ' ').replace('  ', ' ').replace('  ', ' ').replace('  ', ' ')
    return sql


class BaseHandler(object):
    """
    数据库基础类
    """

    def __init__(self, conn_name, conn, curstype='TUPLE', auto_commit=False, db=''):
        self.name = conn_name
        self.conn = conn
        self.curstype = curstype
        if curstype == 'TUPLE':
            self.cursor = conn.cursor()
        else:
            self.cursor = conn.cursor(cursor_class=MySQLCursorDict)
        self.conn.autocommit = auto_commit
        self.initialize()
        self.db = db

    def initialize(self):
        pass

    def show_tables(self):
        return '\n'.join([','.join(i) for i in self.fetch_data("show tables")])

    def close(self):
        """
        not close really , but relase connection
        """
        self.cursor.close()
        del self.conn, self.cursor

    def query_all(self, sql, data=None):
        """
        执行SQL
        """
        self.cursor.execute(sql, data)
        return self.cursor.fetchall()

    def query_one(self, sql, data=None):
        """
        执行SQL
        """
        self.cursor.execute(sql, data)
        return self.cursor.fetchone()

    def query(self, sql, data=None, qt='all'):
        self.cursor.execute(sql, data)
        if qt.lower() == 'one':
            return self.cursor.fetchone()
        else:
            return self.cursor.fetchall()

    def operate(self, sql, data, method='SINGLE'):
        """
        操作数据
        method: 执行方式SINGLE, MANY
        return: 影响行数
        """
        try:
            method = {'SINGLE': 'SINGLE', 'MANY': 'MANY'}[method]
        except:
            raise ExecuteNotChooseError('executing method error, you must choose SINGLE or MANY.')
        if method == 'SINGLE':
            num = self.cursor.execute(sql, data)
        else:  # MANY
            num = self.cursor.executemany(sql, data)
        return num

    def update(self, sql, data=None, method='SINGLE'):
        return self.operate(sql, data, method=method)

    def delete(self, sql, data=None, method='SINGLE'):
        return self.operate(sql, data, method=method)

    def insert(self, sql, data=None, method='SINGLE'):
        return self.operate(sql, data, method=method)

    def fetch_data(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()


class HotelDataBaseHandler(BaseHandler):
    debug = 1
    charset = 'utf8'

    def initialize(self):
        self.debug = 0

    def set_debug(self, debug):
        self.debug = debug

    def get_debug(self):
        return self.debug

    def rename_table(self, _src_table, des_table):

        if len(_src_table.strip()) < 1 or len(des_table.strip()) < 1:
            return -1
        sql = "ALTER TABLE " + _src_table + " RENAME " + des_table + ";"
        try:
            self.cursor.execute(sql)
        except dblib.Error, error:
            print "rename_table Error:", error
            return -1
        return 0

    def exec_sql(self, sql, params=None):

        if self.debug:
            print fix_sql(sql, params)
        try:
            self.cursor.execute(sql, params)
        except dblib.IntegrityError, error:
            print fix_sql(sql, params)
            print "exec_sql IntegrityError", error
            return -2
        except dblib.Error, error:
            print fix_sql(sql, params)
            print "exec_sql Error:", error
            return -1
        return self.cursor.rowcount

    def move_table(self, src_table, des_table):

        sql = "INSERT INTO " + des_table + " SELECT * FROM " + src_table + ";"
        if self.debug:
            print sql
        try:
            self.cursor.execute(sql)
        except dblib.Error, error:
            print sql
            print "move_table Error:", error
            return -1
        return 0

    def truncate_table(self, src_table):

        sql = "TRUNCATE TABLE " + src_table + ";"
        if self.debug:
            print sql
        try:
            self.cursor.execute(sql)
        except dblib.Error, error:
            print sql
            print "truncate_table Error:", error
            return -1
        return 0

    def drop_table(self, table):

        sql = "DROP TABLE " + table + ";"
        if self.debug:
            print sql
        try:
            self.cursor.execute(sql)
        except dblib.Error, error:
            print sql
            print "drop_table Error:", error
            return -1
        return 0

    def table_exists(self, table):

        sql = "SHOW TABLES LIKE '" + table + "';"
        if self.debug:
            print sql
        try:
            self.cursor.execute(sql)
        except dblib.Error, error:
            print "table_exists Error:", error
            return -1
        else:
            data = self.cursor.fetchall()
            if len(data) == 1:
                item = data[0][0]
                if item == table:
                    return 1
        return 0

    def get_a_cloumn(self, sql):
        return self.get_a_column(sql)

    def get_a_column(self, sql, params=None):
        item = ""
        if self.debug:
            print fix_sql(sql, params)
        try:
            self.cursor.execute(sql, params)
        except dblib.Error, error:
            print fix_sql(sql, params)
            print "get_a_column Error:", error
            return item
        else:
            data = self.cursor.fetchall()
            if len(data) == 1:
                item = data[0][0]
            else:
                if self.debug:
                    print "get_a_column [%s] Error DataLen:" % sql, data
        return item

    def get_cloumns(self, sql, params=None):
        return self.get_columns(sql, params)

    def get_columns(self, sql, params=None):
        item = []
        if self.debug:
            print sql
        try:
            self.cursor.execute(sql, params)
        except dblib.Error, error:
            print sql
            print "get_columns Error:", error
            return item
        else:
            data = self.cursor.fetchall()
            if len(data) == 1:
                item = data[0]

        return item

    def get_sql_data(self, sql, params=None):
        data = []
        if self.debug:
            print fix_sql(sql, params)
        try:
            self.cursor.execute(sql, params)
        except dblib.Error, error:
            print fix_sql(sql, params)
            print "get_sql_data Error:", error
            return data
        else:
            data = self.cursor.fetchall()
        return data

    def get_sql_data_dict(self, sql, params=None):
        _dict = dict()
        if self.debug:
            print fix_sql(sql, params)
        try:
            self.cursor.execute(sql, params)
        except dblib.Error, error:
            print fix_sql(sql, params)
            print "get_sql_data_dict Error:", error
        else:
            data = self.cursor.fetchall()
            for item in data:
                _dict[item[0]] = tuple(item[1:])
                if self.debug:
                    print "get_sql_data_dict:%s\t" % item[0], _dict[item[0]]
        return _dict

    def get_sql_data_dict2(self, sql, params=None):
        _dict = dict()
        if self.debug:
            print fix_sql(sql, params)
        try:
            self.cursor.execute(sql, params)
        except dblib.Error, error:
            print fix_sql(sql, params)
            print "get_sql_data_dict2 Error:", error
        else:
            data = self.cursor.fetchall()
            for item in data:
                if len(item) > 2:
                    if item[0] not in _dict:
                        _dict[item[0]] = {}
                    _dict[item[0]][item[1]] = tuple(item[2:])
                else:
                    _dict[item[0]] = tuple(item[1:])
        return _dict

    def get_tables(self):
        items = []
        sql = "SHOW TABLES"
        try:
            self.cursor.execute(sql)
        except dblib.Error, error:
            print sql
            print "get_tables %s Error:" % sql, error
            return items
        else:
            data = self.cursor.fetchall()
            for item in data:
                items.append(item[0])
        return items

    def get_table_fields(self, tablename):
        items = []
        sql = "show full columns from %s" % tablename
        try:
            self.cursor.execute(sql)
        except dblib.Error, error:
            print sql
            print "get_table_fields %s Error:" % tablename, error
            return items
        else:
            items = self.cursor.fetchall()
        return items

    def show_columns(self, table):
        """
        查看表的列
        table: 表名称
        columns: 列名
        """
        sql = '''select column_name, data_type
                    from information_schema.columns
                 where table_schema = %s and table_name=%s
              '''
        columns = {}
        tables = self.query_all(sql, (self.db, table))
        usetype = {'DICT': {'column_name': 'column_name', 'data_type': 'data_type'},
                   'TUPLE': {'column_name': 0, 'data_type': 1}}[self.curstype]
        for col in tables:
            colname = str(col[usetype['column_name']])
            coltype = str(col[usetype['data_type']])
            if 'int' in coltype.lower():
                columns[colname] = int
            elif 'double' in coltype or 'float' in coltype:
                columns[colname] = float
            else:
                columns[colname] = str
        return columns

    def get_create_table_sql(self, table, to_table=""):
        item = ""
        sql = "SHOW CREATE TABLE " + table
        try:
            self.cursor.execute(sql)
        except dblib.Error, error:
            print sql
            print "get_create_table_sql Error:", error
            return item
        else:
            data = self.cursor.fetchall()
            if len(data) == 1:
                item = data[0][1]
        sql2 = item.split("\n")
        if to_table != "":
            sql2[0] = "CREATE TABLE " + to_table + " ("
        item = "\n".join(sql2)
        return item

    def print_desc(self, table):
        fields = self.get_table_fields(table)
        print "-" * 80
        print "%-20s %-15s %-8s %-10s %-20s" % ('name', 'type', 'is null', 'default', 'comment')
        print "-" * 80
        for field in fields:
            fname, ftype, fcollation, fnull, fkey, fdefault, fextra, fprivileges, fcomment = field
            print "%-20s %-15s %-8s %-10s %-20s" % (fname, ftype, fnull, fdefault, fcomment)
        print "-" * 80

    @staticmethod
    def _print(data):
        len_col = []
        printfmt = " "
        for item in data:
            if len(len_col) < len(item):
                for i in range(len(item)):
                    len_col.append(0)
            for i in range(len(item)):
                if len_col[i] < len(str(item[i])):
                    len_col[i] = len(str(item[i]))
        print "", "-" * 80
        for lencol in len_col:
            printfmt += "%%%ds " % lencol
        for item in data:
            print printfmt % item
        print "", "-" * 80

    def print_data(self, sql):
        data = self.get_sql_data(sql)
        self._print(data)

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def get_insert_id(self):
        return self.cursor.lastrowid

    def show_table_info(self, table):
        print "[%s]" % table
        self.print_desc(table)
        cnt = int(self.get_a_column('select count(*) from ' + table))
        if cnt > 0:
            # print "[%s Data]" % Table
            print "Count=%d" % cnt
            if cnt > 100:
                first = 50
            else:
                first = cnt
            self.print_data('Select * from %s limit %d' % (table, first))

    def sql2strings(self, sql, split='|', addtitle=False, forcealign=False):
        """
        导出sql返回的数据到文本列表中
        """
        lines = []
        datas = self.get_sql_data(sql)
        if addtitle:
            descs = self.cursor.description
            line = ""
            for desc in descs:
                line += str(desc[0]) + split
            lines.append(line)
            print line
        if forcealign:
            alignlens = {}
            for data in datas:
                i = 0
                for d in data:
                    i += 1
                    if type(d) == type(u'1'):
                        d = d.encode('utf8')
                    # print type(d),d
                    l = len(str(d).decode('utf8').encode('gbk', 'ignore'))
                    if i not in alignlens:
                        alignlens[i] = l
                    else:
                        if l > alignlens[i]:
                            alignlens[i] = l
            for data in datas:
                line = ""
                i = 0
                for d in data:
                    i += 1
                    if type(d) == type(u'1'):
                        d = d.encode('utf8')
                    fmt = "%%-%ds" % alignlens[i]
                    line += ((fmt % str(d).decode('utf8').encode('gbk', 'ignore')).decode('gbk') + split).encode('utf8')
                line = line.replace('\r', '\\r')
                line = line.replace('\n', '\\n')
                lines.append(line)
            return lines

        else:
            for data in datas:
                line = ""
                for d in data:
                    if type(d) == type(u'1'):
                        d = d.encode('utf8')
                    line += str(d) + split
                line = line.replace('\r', '\\r')
                line = line.replace('\n', '\\n')
                lines.append(line)
            return lines

    def sql2table(self, sql, headers, addtitle=False, prefix='<table cellspacing="0" cellpadding="1" border="1">',
                  postfix='</table>'):
        """
        headers是列表参数, 如['a', 'b', 'c']
        导出sql返回的数据到html表格
        <tr>
        <td width="100">你好</td>
        <td width="300">他好</td>
        </tr>
        <tr>
        <td width="100">你们好</td>
        <td width="300">他们好</td>
        </table>
        """

        lines = []
        datas = self.get_sql_data(sql)

        if len(datas) < 1:
            return ''

        if len(headers) > 0:
            line = "<tr>"
            for header in headers:
                line += "<td>%s</td>" % str(header)
            line += "</tr>"
            print line
            lines.append(line)

        if addtitle:
            descs = self.cursor.description
            line = "<tr>"
            for desc in descs:
                line += "<td>%s</td>" % str(desc[0])
            line += "</tr>"
            lines.append(line)
            print line

        for data in datas:
            line = "<tr>"
            for d in data:
                if type(d) == type(u'1'):
                    d = d.encode('utf8')
                line += "<td>%s</td>" % str(d)
            line += "</tr>"
            line = line.replace('\r', '<br/>')
            line = line.replace('\n', '<br/>')
            lines.append(line)
        html = prefix + string.join(lines, '\n') + postfix
        return html

    def sql2file(self, sql, outfile, split='|'):
        """
        导出数据到指定文件
        """
        lines = self.sql2strings(sql, split)
        with open(outfile, 'at') as fo:
            for line in lines:
                fo.write(line + '\r\n')
        return len(lines)

    def makecode(self, table):
        fields = self.get_table_fields(table)
        insert = 'insert into %s ({columns}) \n values ({values})' % table
        update = 'update %s set {columns}' % table
        columns = []
        ucolumns = []
        for field in fields:
            fname, ftype, fcollation, fnull, fkey, fdefault, fextra, fprivileges, fcomment = field
            columns.append(fname)
            ucolumns.append('%s = %%(%s)s' % (fname, fname))

        insert = insert.replace('{columns}', string.join(columns, ',')).\
            replace('{values}', "%(" + string.join(columns, ')s,%(') + ")s")
        print "-" * 80
        print insert
        update = update.replace('{columns}', string.join(ucolumns, ','))
        print "-" * 80
        print update
        print "-" * 80
        for field in fields:
            fname, ftype, fcollation, fnull, fkey, fdefault, fextra, fprivileges, fcomment = field
            print 'print "%s=[%%s]" %% h["%s"]' % (fname, fname)