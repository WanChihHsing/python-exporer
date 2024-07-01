import csv
import os

import pandas as pd
import pymysql
from dotenv import load_dotenv

load_dotenv()

# MySQL 数据库连接配置
DB_HOST = os.getenv("NL_DB_HOST")
DB_USERNAME = os.getenv("NL_DB_USERNAME")
DB_PASSWORD = os.getenv("NL_DB_PASSWORD")
DB_NAME = os.getenv("NL_DB_NAME")

# 读取 Excel 文件
df = pd.read_excel('串码为空_fix.xlsx', sheet_name='Sheet1')

# 连接到 MySQL 数据库
connection = pymysql.connect(
    host=DB_HOST,
    user=DB_USERNAME,
    password=DB_PASSWORD,
    database=DB_NAME
)

update_sql = """
    UPDATE honor_order_2024_test
    SET `create_order_time`      = %s,
        `shop_id`                = %s,
        `trade_no`               = %s,
        `update_time`            = now(),
        `btc_order_id`           = %s,
        `category`               = %s,
        `supplier_code`          = %s,
        `supplier_name`          = %s,
        `shipment_date`          = %s,
        `sales_type`             = %s,
        `unit_price_pay`         = %s,
        `order_time`             = %s,
        `guide_price`            = %s,
        `product_name`           = %s,
        `product_code`           = %s,
        `imei`                   = %s,
        `pay_price`              = %s,
        `business_code`          = %s,
        `channel_code`           = %s,
        `city_name`              = %s,
        `place_code`             = %s,
        `place_name`             = %s,
        `place_type`             = %s,
        `oms_item_no`            = %s,
        `cut_price`              = %s,
        `coup_regard_amt`        = %s,
        `external_order_id`      = %s,
        `external_order_item_id` = %s,
        `fq_order_time`          = %s,
        `fq_product_name`        = %s,
        `fq_num`                 = %s,
        `interest_free_amt`      = %s,
        `refund_interest_amt`    = %s,
        `rate`                   = %s,
        `product_presale_flag`   = %s,
        `presale_price`          = %s,
        `push_status`            = %s,
        `error_msg`              = %s
    WHERE `uuid` = %s
"""

insert_sql = """
    INSERT INTO honor_order_2024_test
    VALUES (%s, %s, %s, %s, now(), %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

# 指定要删除的文件路径
file_path = 'error_report.csv'

# 检查文件是否存在
if os.path.exists(file_path):
    # 删除文件
    os.remove(file_path)
    print(f'File {file_path} has been deleted.')
else:
    print(f'File {file_path} does not exist.')

try:
    with connection.cursor() as cursor:
        # 遍历 DataFrame 中的每一行
        for index, row in df.iterrows():
            record = row.to_dict()
            # 移除键为 'update_time' 的项
            if 'update_time' in record:
                del record['update_time']
            # 检查并替换 NaN 值
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
            # 将字典转换为列表
            record_list = list(record.values())
            # 将第一个元素移动到末尾
            record_list = record_list[1:] + [record_list[0]]
            # 执行 SQL 语句
            result = cursor.execute(update_sql, record_list)
            if result == 0:
                print('No record found')
                try:
                    record_list = list(record.values())
                    cursor.execute(insert_sql, record_list)
                except Exception as e:
                    print(e)
                    record['error_msg'] = str(e)
                    # 将 record 输出到 CSV 文件
                    with open(file_path, 'a', newline='') as csvfile:
                        fieldnames = record.keys()
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writerow(record)
                    continue

    # 提交更改
    connection.commit()

finally:
    # 关闭数据库连接
    connection.close()
