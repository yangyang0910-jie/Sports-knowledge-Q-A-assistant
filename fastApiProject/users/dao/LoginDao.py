from common import MySQLCommon

#查询用户是否存在
def inquire_users(email):
    #连接对象
    conn=MySQLCommon.get_mysql_conn()
    #创建游标对象
    cur = conn.cursor()
    #查询用户
    sql = "select * from userinformation where email=%s"
    #执行
    cur.execute(sql,[email])
    result = cur.fetchall()
    print(result)
    MySQLCommon.close_mysql_conn(cur,conn)
    if result:
        return  {
            "code":200,
            "msg":"查询成功",
            "data":result[0]
        }
    return {
        "code": 500,
        "msg": "查询失败，用户不存在",
        "data": None
    }
if __name__ == '__main__':
    inquire_users(22)

