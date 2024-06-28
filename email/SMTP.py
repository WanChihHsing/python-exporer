import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()

# MySQL 数据库连接配置
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# 电子邮件账户的配置信息
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')  # QQ 邮箱的授权码，而不是登录密码

# 创建一个MIMEMultipart对象
msg = MIMEMultipart()
msg['From'] = 'Honeypot Report <no-reply@wanwei.com>'
msg['To'] = '799789034@qq.com'
msg['Subject'] = '蜜罐报告'

# 添加邮件内容
body = '每日报告。'
msg.attach(MIMEText(body, 'plain', 'utf-8'))

# 发送邮件
try:
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    text = msg.as_string()
    server.sendmail(SMTP_USERNAME, '799789034@qq.com', text)
    server.quit()
    print("邮件发送成功")
except Exception as e:
    print(f"邮件发送失败: {e}")
