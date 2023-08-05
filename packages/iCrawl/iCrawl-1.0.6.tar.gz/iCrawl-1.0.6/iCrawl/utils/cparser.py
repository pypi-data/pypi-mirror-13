#!/usr/bin/env python
# -*- coding:utf8 -*-

import ConfigParser


def parse_mysql(fname, defaults=None):
    cp = ConfigParser.ConfigParser(defaults)
    if hasattr(fname, 'readline'):
        cp.readfp(fname)
    else:
        cp.read(fname)
    ulist = cp.get("db_use", "keys")
    if not len(ulist):
        return {}
    ulist = ulist.split(",")
    ulist = _strip_spaces(ulist)
    dbs = []
    for one in ulist:
        db_dict = dict()
        sectname = "%s_db" % one
        one_str = str(one)
        db_dict[one_str] = {}
        db_dict[one_str]['dbmode'] = cp.get(sectname, 'optype')
        db_dict[one_str]['dbhost'] = cp.get(sectname, "host")
        db_dict[one_str]['dbport'] = cp.get(sectname, "port")
        db_dict[one_str]['dbuser'] = cp.get(sectname, "user")
        db_dict[one_str]['dbpasswd'] = cp.get(sectname, "passwd")
        db_dict[one_str]['dbname'] = cp.get(sectname, "db")
        db_dict[one_str]['dbcharset'] = cp.get(sectname, "charset")
        db_dict[one_str]['dbunicode'] = cp.get(sectname, "use_unicode")
        dbs.append(db_dict)
    return dbs


def parse_mongo(fname, defaults=None):
    cp = ConfigParser.ConfigParser(defaults)
    if hasattr(fname, 'readline'):
        cp.readfp(fname)
    else:
        cp.read(fname)
    ulist = cp.get("db_use", "keys")
    if not len(ulist):
        return {}
    ulist = ulist.split(",")
    ulist = _strip_spaces(ulist)
    dbs = []
    for one in ulist:
        db_dict = dict()
        sectname = "%s_db" % one
        one_str = str(one)
        db_dict[one_str] = {}
        db_dict[one_str]['dbmode'] = cp.get(sectname, 'optype')
        db_dict[one_str]['dbhost'] = cp.get(sectname, "host")
        db_dict[one_str]['dbport'] = cp.get(sectname, "port")
        db_dict[one_str]['dbuser'] = cp.get(sectname, "user")
        db_dict[one_str]['dbpasswd'] = cp.get(sectname, "passwd")
        db_dict[one_str]['dbname'] = cp.get(sectname, "db")
        db_dict[one_str]['dbcharset'] = cp.get(sectname, "charset")
        db_dict[one_str]['dbunicode'] = cp.get(sectname, "use_unicode")
        dbs.append(db_dict)
    return dbs


def load_dbcfg(dbc, dbs):
    for one in dbs:
        dbc.add_database(
            one.keys()[0],
            host=one.values()[0]['dbhost'],
            port=one.values()[0]['dbport'],
            user=one.values()[0]['dbuser'],
            passwd=one.values()[0]['dbpasswd'],
            db=one.values()[0]['dbname'],
            charset=one.values()[0]['dbcharset'],
            use_unicode=False
        )


def load_mysql(dbc, dbs):
    uses = dbs['use'].split(',')
    for one in uses:
        one = str(one)
        dbc.add_database(
            one,
            host=dbs[one]['host'],
            port=dbs[one]['port'],
            user=dbs[one]['user'],
            passwd=dbs[one]['passwd'],
            db=dbs[one]['db'],
            charset=dbs[one]['charset'],
            use_unicode=False
        )


def load_mongo(mongodb, conf):
        uses = conf['use'].split(',')
        for one in uses:
            one = str(one)
            mongodb.add_mongo(
                one,
                host=conf[one]['host'],
                port=conf[one]['port'],
                user=conf[one]['user'],
                passwd=conf[one]['passwd'],
                db=conf[one]['db'],
            )


def _strip_spaces(alist):
    return map(lambda x: x.strip(), alist)