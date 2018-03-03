# coding: utf8
import pymysql
import settings
import redis


client = redis.Redis()
ORDER_KEY = 'seven:orderstock'

seven_db_settings = settings.seven_db_settings
seven_db_settings['charset'] = 'utf8mb4'
seven_db = pymysql.connect(**seven_db_settings)
seven_cursor = seven_db.cursor()
ipos_db_settings = settings.ipos_db_settings
ipos_db_settings['charset'] = 'utf8mb4'
ipos_db = pymysql.connect(**settings.ipos_db_settings)
ipos_cursor = ipos_db.cursor()


def db_start():
    global seven_db, seven_cursor, ipos_db, ipos_curosr
    print('running db start...')
    try:
        seven_cursor.execute('select 1;')
        seven_cursor.fetchone()
        return 
    except:
        try:
            seven_db.rollback()
        except:
            pass
    seven_db = pymysql.connect(**seven_db_settings)
    seven_cursor = seven_db.cursor()
    ipos_db = pymysql.connect(**settings.ipos_db_settings)
    ipos_cursor = ipos_db.cursor()
    print('db hading start....')

def db_close():
    global seven_db, seven_cursor, ipos_db, ipos_curosr
    seven_db.close()
    ipos_db.close()


order_sql = 'select id, ordersn from ims_ewei_shop_order where status =1 and uniacid =2'
option_sql = 'select goodsid, optionname, productsn from ims_ewei_shop_order_goods where orderid=%s'
goods_sql = 'select title from ims_ewei_shop_goods where id=%s'

query_stock_sql = 'select sl from ipos_spkcb where concat(spdm,gg1dm,gg2dm)= %s ' \
                  'and zd_id =%s '
shops = (20, 24, 25, 26, 29, 31, 35, 47, 48, 1600)


def order_exists(ordersn):
    return client.sismember(ORDER_KEY, ordersn)


def backup_order(ordersn):
    client.sadd(ORDER_KEY, ordersn)


def del_order(ordersn):
    client.srem(ORDER_KEY, ordersn)


def get_product_data():
    seven_cursor.execute(order_sql)
    for order_id, ordersn in seven_cursor.fetchall():
        if order_exists(ordersn):
            continue

        backup_order(ordersn)
        seven_cursor.execute(option_sql, (order_id, ))
        for goodsid, optionname, productsn in seven_cursor.fetchall():
            color_size = optionname.split('+')
            color, size = color_size[0], color_size[-1]
            seven_cursor.execute(goods_sql, goodsid)
            title = seven_cursor.fetchone()[0]

            yield ordersn, title, color, size, productsn


def _get_stock(productsn):
    """get one product stock"""
    stocks = []
    for shop in shops:
        ipos_cursor.execute(query_stock_sql, (productsn, shop))
        stock = ipos_cursor.fetchone()
        if stock:
            stocks.append(stock[0])
        else:
            stocks.append(-1)
    return stocks


def delete_data(db, model):
    ordersn_set = set()
    
    try:
        seven_cursor.execute(order_sql)
    except Exception as e:
        print('query order error:', e)
    for order_id, ordersn in seven_cursor.fetchall():
        ordersn_set.add(ordersn)
    #print(ordersn_set)
    rcds = model.query.all()
    for rcd in rcds:
        #print(rcd)
        if rcd.order_code not in ordersn_set:
            del_order(rcd.order_code)
            db.session.delete(rcd)
    db.session.commit()


def get_data(db, Model):
    db_start()
    try:
        delete_data(db, Model)
    except Exception as e:
        print('delete data error:', e)
    for p in get_product_data():
        #print(p)
        stocks = _get_stock(p[-1])
        data = p[:-1] + tuple(stocks)
        yield data
    #db_close()

