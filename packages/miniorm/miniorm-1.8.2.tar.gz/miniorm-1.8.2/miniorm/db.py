# coding=utf-8
# __author__ = 'ininwn@gmail.com'

import logging
import threading
import time
import traceback
from collections import OrderedDict

from mysql.connector import connection

logger = logging.getLogger("miniorm")


class Model(object):
    buffered = True
    dictionary = True
    connections = {}

    @staticmethod
    def make(name, dbargkws=None, tablename=None):
        return type(tablename or name.lower(), (Model,), dict(tablename=tablename or name.lower(), dbargkws=dbargkws, connections={}))

    @classmethod
    def get_conn(clz):
        ident = threading.currentThread().ident
        if ident not in clz.connections: clz.connections[ident] = connection.MySQLConnection(**clz.dbargkws)
        conn = clz.connections[ident]
        if not conn.is_connected(): conn.reconnect()

        if len(clz.connections) > 1:
            if not hasattr(clz, "conn_purger"):
                t = threading.Thread(target=clz.purge_conn_runner)
                t.daemon = True
                clz.conn_purger = t
                t.start()
        return conn

    @classmethod
    def close(clz):
        ident = threading.currentThread().ident
        logger.debug("close Model in thread: %s %s", clz, ident)
        if ident in clz.connections:
            clz.connections[ident].close()
            del clz.connections[ident]

    @classmethod
    def destory(clz):
        logger.debug("destory Model: %s begin, connections: %s", clz, len(clz.connections))
        for ident, conn in clz.connections.items(): conn.close()
        clz.connections.clear()
        logger.debug("destory Model: %s ok", clz)

    @classmethod
    def purge_conn_runner(clz):
        while 1:
            time.sleep(len(clz.connections) > 1 and 20 or 120)
            try:
                idents = set(clz.connections.keys()) - set([t.ident for t in threading.enumerate()])
                for ident in idents:
                    clz.connections[ident].close()
                    del clz.connections[ident]
                idents and logger.debug("purge_conn_runner removed %s connections", len(idents))
            except:
                logger.error("purge_conn_runner error: %s", traceback.format_exc())

    @classmethod
    def get_by_id(clz, id, select_cols=None):
        conn = clz.get_conn()
        c = conn.cursor(buffered=True, dictionary=True)
        try:
            if select_cols:
                sel = ",".join(" " in c and c or "`%s`" % c for c in select_cols)
                c.execute("select %s from %s where id =%s" % (sel, clz.tablename, "%s"), (id,))
            else:
                c.execute("select * from %s  where id =%s " % (clz.tablename, "%s"), (id,))
            return c.fetchone()
        except Exception as e:
            conn.in_transaction and conn.rollback()
            raise e
        finally:
            conn.in_transaction and conn.commit()
            c.close()

    @classmethod
    def get_one_by_map(clz, params={}, and_or="and", select_cols=None, order_by=None, group_by=None, force_index=None):
        rets = clz.get_by_map(params=params, start=0, limit=1, and_or=and_or, select_cols=select_cols, order_by=order_by, group_by=group_by, force_index=force_index)
        return rets and rets[0] or None

    @classmethod
    def map(clz, func, params={}, and_or="and", select_cols=None, order_by=None, group_by=None, force_index=None):
        i, limit = 0, 300
        while 1:
            start = limit * i
            rets = clz.get_by_map(params, start, limit, and_or=and_or, select_cols=select_cols, order_by=order_by, group_by=group_by, force_index=force_index)

            for ret in rets: func(ret)

            if len(rets) < limit:
                break
            i += 1

    @classmethod
    def all(clz, params={}, and_or="and", select_cols=None, order_by=None, group_by=None, force_index=None):
        alls = []
        clz.map(lambda r: alls.append(r), params, and_or=and_or, select_cols=select_cols, order_by=order_by, group_by=group_by, force_index=force_index)
        return alls

    @classmethod
    def get_by_map(clz, params={}, start=0, limit=50, and_or="and", select_cols=None, order_by=None, group_by=None, force_index=None):
        order_by = order_by and " order by " + ",".join(order_by) or ""
        group_by = group_by and ",".join("(" in g and g or "`%s`" % g for g in group_by) or None
        group_by = group_by and " group by %s" % group_by or ""
        force_index = force_index and " force index (%s)" % (",".join("`%s`" % g for g in force_index)) or ""
        conn = clz.get_conn()
        c = conn.cursor(buffered=True, dictionary=True)
        try:
            if not params:
                if select_cols:
                    sel = ",".join(" " in c and c or "`%s`" % c for c in select_cols)
                    sql = "select %s from %s %s %s %s limit %s,%s" % (sel, clz.tablename, force_index, group_by, order_by, start, limit)
                    logger.debug(sql)
                    c.execute(sql)
                else:
                    sql = "select * from %s %s %s %s limit %s,%s" % (clz.tablename, force_index, group_by, order_by, start, limit)
                    logger.debug(sql)
                    c.execute(sql)
            else:
                conds, vals = Model.combine_fields(params)
                cond = (" " + and_or + " ").join(conds)

                if select_cols:
                    sel = ",".join(" " in c and c or "`%s`" % c for c in select_cols)
                    sql = "select %s from  %s %s where %s %s %s limit %s,%s" % (sel, clz.tablename, force_index, cond, group_by, order_by, start, limit)
                    logger.debug(sql + ", %s" % vals)
                    c.execute(sql, vals)
                else:
                    sql = "select * from %s %s where %s %s %s limit %s,%s" % (clz.tablename, force_index, cond, group_by, order_by, start, limit)
                    logger.debug(sql + ", %s" % vals)
                    c.execute(sql, vals)
            return c.fetchall()
        except Exception as e:
            conn.in_transaction and conn.rollback()
            raise e
        finally:
            conn.in_transaction and conn.commit()
            c.close()

    @staticmethod
    def combine_fields(params):
        fields = []
        vals = []
        for field, val in params.items():
            if field.endswith("$match"):
                fields.append("match(`%s`) against (%%s in boolean mode) " % field[:-6])
            elif field.endswith("$like"):
                fields.append("`%s` like %%s " % field[:-5])
            elif field.endswith("$isnull"):
                fields.append("`%s` is  %s null" % (field[:-7], val and "" or "not"))
            elif field.endswith("$in"):
                fields.append("`%s` in (%s) " % (field[:-3], ",".join(["%s"] * len(val))))
            elif field.endswith("$gt"):
                fields.append("`%s` > %%s " % field[:-3])
            elif field.endswith("$gte"):
                fields.append("`%s` >= %%s " % field[:-4])
            elif field.endswith("$lt"):
                fields.append("`%s` < %%s " % field[:-3])
            elif field.endswith("$lte"):
                fields.append("`%s` <= %%s " % field[:-4])
            else:
                fields.append("`%s` %s %%s " % (field, val is None and "is" or "="))

            if field.endswith("$like"):
                vals.append("%%%s%%" % val)
            elif field.endswith("$match"):
                vals.append("%s" % " ".join(["+%s*" % v for v in val.split(" ") if v.strip()]))
            elif field.endswith("$in"):
                vals.extend(val)
            elif field.endswith("$isnull"):
                pass
            else:
                vals.append(val)
        return fields, vals

    @classmethod
    def exists(clz, params={}, and_or="and"):
        return clz.get_one_by_map(params=params, and_or=and_or) is not None

    @classmethod
    def count_by_map(clz, params={}, and_or="and", distinct=None, group_by=None, order_by=None, start=0, limit=30):
        """
        @order_by 只有在group by有的时候才生效
        @start, limit 只有在group by有的时候才生效
        """
        group_by = group_by and ",".join("(" in g and g or "`%s`" % g for g in group_by) or None
        conn = clz.get_conn()
        c = conn.cursor(buffered=True, dictionary=True)
        try:
            sfields = ["count(%s) as count" % (distinct and "distinct(`" + distinct + "`)" or "*"), (group_by and group_by or None)]
            if not params:
                sql = "select %s from %s %s %s %s " % (
                    ','.join([f for f in sfields if f]),
                    clz.tablename,
                    group_by and " group by %s" % group_by or "",
                    group_by and order_by and " order by " + ",".join(order_by) or "",
                    group_by and " limit %s,%s" % (start, limit) or ""
                )

                logger.debug(sql)
                c.execute(sql)
            else:
                conds, vals = Model.combine_fields(params)
                cond = (" " + and_or + " ").join(conds)
                sql = "select %s from %s where %s %s %s %s " % (
                    ','.join([f for f in sfields if f]),
                    clz.tablename,
                    cond,
                    group_by and " group by %s" % group_by or "",
                    group_by and order_by and " order by " + ",".join(order_by) or "",
                    group_by and " limit %s,%s" % (start, limit) or ""
                )
                logger.debug(sql + ", %s" % vals)
                c.execute(sql, vals)
            if group_by:
                return c.fetchall()
            else:
                return c.fetchone()["count"]
        except Exception as e:
            conn.in_transaction and conn.rollback()
            raise e
        finally:
            conn.in_transaction and conn.commit()
            c.close()

    @classmethod
    def delete_by_id(clz, id):
        conn = clz.get_conn()
        c = conn.cursor(buffered=True, dictionary=True)
        try:
            c.execute("delete from %s where id =%s" % (clz.tablename, "%s"), (id,))
            return c.rowcount
        except Exception as e:
            conn.in_transaction and conn.rollback()
            raise e
        finally:
            conn.in_transaction and conn.commit()
            c.close()

    @classmethod
    def delete_by_map(clz, params={}, and_or="and"):
        if not params: raise Exception("params can not be empty or None! params:%s" % params)
        conds, vals = Model.combine_fields(params)
        cond = (" " + and_or + " ").join(conds)
        conn = clz.get_conn()
        c = conn.cursor(buffered=True, dictionary=True)
        try:
            sql = "delete from %s where %s" % (clz.tablename, cond)
            c.execute(sql, vals)
            logger.debug("sql: %s, %s", sql, vals)
            return c.rowcount
        except Exception as e:
            conn.in_transaction and conn.rollback()
            raise e
        finally:
            conn.in_transaction and conn.commit()
            c.close()

    @classmethod
    def delete_all(clz):
        conn = clz.get_conn()
        c = conn.cursor(buffered=True, dictionary=True)
        try:
            sql = "delete from %s" % (clz.tablename)
            c.execute(sql)
            logger.debug("sql: %s", sql)
            return c.rowcount
        except Exception as e:
            conn.in_transaction and conn.rollback()
            raise e
        finally:
            conn.in_transaction and conn.commit()
            c.close()

    @classmethod
    def truncate(clz):
        conn = clz.get_conn()
        c = conn.cursor(buffered=True, dictionary=True)
        try:
            sql = "truncate table %s" % (clz.tablename)
            c.execute(sql)
            logger.debug("sql: %s", sql)
            return c.rowcount
        except Exception as e:
            conn.in_transaction and conn.rollback()
            raise e
        finally:
            conn.in_transaction and conn.commit()
            c.close()

    @classmethod
    def insert(clz, data, with_insert_id=True):
        if not data: return []
        data = type(data) in (tuple, list) and data or [data, ]
        inserts = []
        conn = clz.get_conn()
        c = conn.cursor(buffered=True, dictionary=True)
        try:
            for d in data:
                d = hasattr(d, "_asdict") and d._asdict() or d
                fields, vals = [], []
                for field, val in d.items():
                    if field.lower() == "id" and val is None:
                        continue
                    fields.append("`%s`" % field)
                    vals.append(val)
                sql = "insert into %s (%s) values(%s) " % (
                    clz.tablename, ",".join(fields), ",".join(["%s"] * len(fields)))

                logger.debug(sql + ", %s" % vals)
                c.execute(sql, vals)

                if with_insert_id:
                    if hasattr(d, "_replace"):
                        d = d._replace(id=c.lastrowid)
                        # print "attach id rep", c.lastrowid
                    elif type(d) in (dict, OrderedDict):
                        d["id"] = c.lastrowid
                        # print "attach id d[id]", c.lastrowid
                    else:
                        d.id = c.lastrowid
                        # print "attach id d.id", c.lastrowid
                inserts.append(d)
            return inserts
        except Exception as e:
            conn.in_transaction and conn.rollback()
            raise e
        finally:
            conn.in_transaction and conn.commit()
            c.close()

    @classmethod
    def columns(clz, more=False):
        conn = clz.get_conn()
        c = conn.cursor(buffered=True, dictionary=True)
        try:
            c.execute("show columns from %s" % clz.tablename)
            return more and c.fetchall() or map(lambda d: d.get("Field"), c.fetchall())
        except Exception as e:
            conn.in_transaction and conn.rollback()
            raise e
        finally:
            conn.in_transaction and conn.commit()
            c.close()

    @classmethod
    def update(clz, data, where=None, and_or="and"):
        if not data: return [], []

        data = type(data) in (tuple, list) and data or [data, ]
        updates, noeffects = [], []

        conn = clz.get_conn()
        c = conn.cursor(buffered=True, dictionary=True)
        try:
            for d in data:
                if where:
                    w_conds, w_vals = Model.combine_fields(where)
                    w_cond = (" " + and_or + " ").join(w_conds)
                else:
                    w_cond = "`id`=%s"
                    if type(d) in (dict, OrderedDict) and "id" in d and d["id"] is not None:
                        w_vals = [d["id"], ]
                    elif hasattr(d, "id") and d.id is not None:
                        w_vals = [d.id, ]
                    else:
                        noeffects.append(d)
                        continue
                p = hasattr(d, "_asdict") and d._asdict() or d
                fields, vals = [], []
                for field, val in d.items():
                    if field.lower().strip() == "id" and val is not None:
                        continue
                    fields.append("`%s`=%%s" % field)
                    vals.append(val)
                sql = "update %s set %s where %s" % (clz.tablename, ",".join(fields), w_cond)
                vss = vals + w_vals
                logger.debug("%s, %s" % (sql, vss))
                c.execute(sql, vss)
                if c.rowcount < 1:
                    noeffects.append(p)  # raise Exception("no data updated: sql:%s,data:%s"%(sql, str(p)))
                else:
                    updates.append(p)
            return updates, noeffects
        except Exception as e:
            conn.in_transaction and conn.rollback()
            raise e
        finally:
            conn.in_transaction and conn.commit()
            c.close()

    @classmethod
    def raw(clz, sql):
        if not sql: return None

        conn = clz.get_conn()
        c = conn.cursor(buffered=True)
        try:
            logger.debug("%s" % sql)
            c.execute(sql)
            return c._rows and c.fetchall() or None  # buffered cursor hack: c._rows
        except Exception as e:
            conn.in_transaction and conn.rollback()
            raise e
        finally:
            conn.in_transaction and conn.commit()
            c.close()
