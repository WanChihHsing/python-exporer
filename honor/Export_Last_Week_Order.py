import os

import mysql.connector
import pandas as pd
from dotenv import load_dotenv

from utils import get_last_week_range

begin_date, end_date = get_last_week_range()

load_dotenv()

# MySQL 数据库连接配置
DB_HOST = os.getenv("NL_DB_HOST")
DB_USERNAME = os.getenv("NL_DB_USERNAME")
DB_PASSWORD = os.getenv("NL_DB_PASSWORD")
DB_NAME = os.getenv("NL_DB_NAME")


def init():
    # 连接到MySQL数据库
    _conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USERNAME,
        password=DB_PASSWORD,
        database=DB_NAME
    )

    _cursor = _conn.cursor(buffered=True)
    _cursor.execute('''
        UPDATE honor_order_2024
        SET push_status = 0,
            update_time= now()
        WHERE shipment_date >= %s
          AND shipment_date <= %s
    ''', (begin_date, end_date))

    _cursor.execute('''
        UPDATE honor_order_2024
        SET push_status = -1
        WHERE place_name in ('金华仓-JD-京东全渠道O2O履约', '金华仓-JD-京东自营', '金华仓-三君能良代发店铺')
          AND shipment_date >= %s
          AND shipment_date <= %s
    ''', (begin_date, end_date))

    _cursor.execute('''
        DROP TEMPORARY TABLE IF EXISTS t1;
    ''')

    _cursor.execute('''
        CREATE TEMPORARY table t1
        SELECT btc_order_id, count(*)
        FROM honor_order_2024
        WHERE shipment_date >= @begin_date
          AND shipment_date <= @end_date
          AND push_status = 0
        GROUP BY btc_order_id
        HAVING count(*) >= 5;
    ''')
    return _conn, _cursor


def destroy(_conn, _cursor):
    _cursor.close()
    _conn.close()


# 订单数量确认
def order_nums_confirm(_conn):
    _query = '''
        SELECT channel_code AS '渠道编码', shop_id, place_name AS '店铺', count(*) AS '订单数量'
        FROM honor_order_2024
        WHERE shipment_date >= %s
          AND shipment_date <= %s
          AND push_status != -1
        GROUP BY shop_id, place_name, channel_code;
    '''
    _df = pd.read_sql(_query, _conn)
    _df.to_excel('订单数量确认.xlsx', index=False)


# 单个订单号串码>=5
def imei_ge_5(_conn, _cursor):
    _query = '''
        SELECT *
        FROM honor_order_2024
        WHERE shipment_date >= %s
          AND shipment_date <= %s
          AND push_status = 0
          AND btc_order_id IN (SELECT btc_order_id FROM t1);
    '''
    _df = pd.read_sql(_query, _conn, params=(begin_date, end_date))
    _df.to_excel('单个订单号串码>=5.xlsx', index=False)


# 手机
def phone(_conn):
    _query = '''
        SELECT *
        FROM honor_order_2024
        WHERE shipment_date >= %s
          AND shipment_date <= %s
          AND push_status = 0
          AND category = 1
          AND btc_order_id not in (SELECT btc_order_id FROM t1);
    '''
    _df = pd.read_sql(_query, _conn, params=(begin_date, end_date))
    _df.to_excel('手机.xlsx', index=False)


# 融合
def other(_conn):
    _query = '''
        SELECT *
        FROM honor_order_2024
        WHERE shipment_date >= %s
          AND shipment_date <= %s
          AND push_status = 0
          AND category != 1
          AND btc_order_id not in (SELECT btc_order_id FROM t1);
    '''
    _df = pd.read_sql(_query, _conn, params=(begin_date, end_date))
    _df.to_excel('融合.xlsx', index=False)


# 串码为空
def imei_is_blank(_conn):
    _query = '''
        SELECT * 
        FROM honor_order_2024_redundant 
        WHERE shipment_date >= %s
          AND shipment_date <= %s
            AND LENGTH(imei) = 0;
    '''
    _df = pd.read_sql(_query, _conn, params=(begin_date, end_date))
    _df.to_excel('串码为空.xlsx', index=False)


if __name__ == "__main__":
    conn, cursor = init()
    order_nums_confirm(conn)
    imei_ge_5(conn, cursor)
    phone(conn)
    other(conn)
    imei_is_blank(conn)
    destroy(conn, cursor)
