import os.path

import paramiko
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("server_host")  # 服务器地址
port = int(os.getenv("SERVER_PORT"))  # SSH端口
username = os.getenv("server_username")  # SSH用户名
password = os.getenv("server_password")  # SSH密码
directory = "/Users/wanwei/PrivateProjects/nmu-exam/"  # 本地项目所在文件夹

# 初始化全局变量用于tqdm进度条
progress_bar = None


def find_jar_path(jar_name):
    for root, dirs, files in os.walk(directory):
        if jar_name in files:
            return os.path.join(root, jar_name)
    return None


def release_port(ssh, _jar_name):
    try:
        # 查找占用指定端口的进程ID
        command = f"ps aux | grep {_jar_name} | grep -v grep | awk '{{print $2}}'"
        stdin, stdout, stderr = ssh.exec_command(command)
        pid = stdout.read().decode().strip()

        if pid:
            # 终止进程
            ssh.exec_command(f"kill -9 {pid}")
            print(f"[{_jar_name}]进程已终止")
        else:
            print(f"[{_jar_name}]未启动")
    except Exception as e:
        print(f"释放端口时发生错误：{e}")


def print_progress(transferred, total):
    global progress_bar
    if progress_bar is None:
        progress_bar = tqdm(total=total, unit='B', unit_scale=True)
    progress_bar.update(transferred - progress_bar.n)


def upload_and_deploy(_jar):
    try:
        local_path = find_jar_path(_jar)
        jar_name = _jar.split(".")[0]
        remote_path = f"/home/exam/{_jar}"  # 服务器上存放JAR包的路径
        # 创建SSH客户端
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password)

        # 使用SFTP上传文件
        sftp = ssh.open_sftp()
        sftp.put(local_path, remote_path, callback=print_progress)
        sftp.close()
        print(f"JAR包上传成功：{remote_path}")

        # 释放服务端口
        release_port(ssh, jar_name)

        # 执行部署命令
        # 服务器使用 which java 查找
        deploy_command = f"nohup /usr/local/jdk17/bin/java -jar {remote_path} > /home/exam/logs/{jar_name}.log 2>&1 &"
        print(f"执行部署命令：{deploy_command}")
        ssh.exec_command(deploy_command)
        # 关闭SSH连接
        ssh.close()
        print(f"[{jar_name}]部署完成")

    except Exception as e:
        print(f"发生错误：{e}")


if __name__ == "__main__":

    gateway = "xueyi-gateway.jar"
    auth = "xueyi-auth.jar"
    nuv = "xueyi-modules-nuv.jar"
    system = "xueyi-modules-system.jar"
    tenant = "xueyi-modules-tenant.jar"

    upload_and_deploy(gateway)
