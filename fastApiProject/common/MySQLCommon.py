import pymysql
import os
from dotenv import load_dotenv
load_dotenv()

def get_mysql_conn():
    return pymysql.connect(
        #ip
        host =os.getenv("MY_HOST"),
        #端口
        port = int(os.getenv("MY_PORT")),
        #数据库账户
        user = os.getenv("MY_USER"),
        #密码
        password = os.getenv("MY_PASSWORD"),
        #数据库名字
        database= os.getenv("MY_DATABASE"),
        #字符集
        charset=os.getenv("MY_CHARSET"),
        #dict的方式查询
        cursorclass=pymysql.cursors.DictCursor
    )
def close_mysql_conn(cursor,conn):
    cursor.close()
    conn.close()