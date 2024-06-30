import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pymysql
from dotenv import load_dotenv

load_dotenv()

# MySQL 数据库连接配置
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


# 查询昨日的连接和登录次数
conn = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)
cursor = conn.cursor()
cursor.execute('''
        SELECT COUNT(*) FROM connections WHERE DATE(conn_time) = CURDATE() - INTERVAL 1 DAY
    ''')
conn_count = cursor.fetchone()[0]
cursor.execute('''
        SELECT COUNT(*) FROM logins WHERE DATE(login_time) = CURDATE() - INTERVAL 1 DAY
    ''')
login_count = cursor.fetchone()[0]
conn.close()

# 电子邮件账户的配置信息
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

# 创建一个MIMEMultipart对象
msg = MIMEMultipart()
msg['From'] = SENDER_EMAIL
msg['To'] = RECIPIENT_EMAIL
msg['Subject'] = 'Honeypot Daily Report'

# 添加邮件内容
body = f'昨日尝试连接 {conn_count} 次.\n昨日尝试登录 {login_count} 次.\n'
msg.attach(MIMEText(body, 'plain', 'utf-8'))

# 发送邮件
# 连接到邮件服务器并发送邮件
try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
    print("Email sent successfully!")
except Exception as e:
    print(f"Failed to send email: {e}")