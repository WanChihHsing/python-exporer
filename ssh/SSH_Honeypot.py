import os
import socket
import threading

import paramiko
import paramiko.common
import pymysql
from dotenv import load_dotenv

load_dotenv()

# MySQL 数据库连接配置
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


# 初始化数据库
def init_db():
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


# 创建一个文件来保存登录尝试
LOG_FILE = "ssh_honeypot_log.txt"


# 日志记录登录尝试
def log_attempt(username, password):
    with open(LOG_FILE, "a") as f:
        f.write(f"Username: {username}, Password: {password}\n")


# Mysql记录登录尝试
def log_attempt_mysql(username, password):
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO logins (username, password, login_time) VALUES (%s, %s, now())
    ''', (username, password))
    conn.commit()
    conn.close()


# 创建一个假的服务器密钥
host_key = paramiko.RSAKey.generate(2048)


class SSHHoneypot(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.common.AUTH_SUCCESSFUL
        return paramiko.common.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        log_attempt_mysql(username, password)
        return paramiko.common.AUTH_FAILED


def start_honeypot(port=22):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', port))
    server_socket.listen(100)

    print(f"[*] SSH Honeypot listening on port {port}")

    while True:
        client, addr = server_socket.accept()
        print(f"[*] Connection from {addr}")
        transport = paramiko.Transport(client)
        transport.add_server_key(host_key)

        honeypot = SSHHoneypot()

        try:
            transport.start_server(server=honeypot)
        except paramiko.SSHException:
            print("[!] SSH negotiation failed")
            continue
        except EOFError:
            print("[!] EOFError")
            continue

        # 处理客户端连接
        chan = transport.accept(20)
        if chan is None:
            print("[!] No channel")
            continue

        chan.close()


if __name__ == "__main__":
    start_honeypot()
