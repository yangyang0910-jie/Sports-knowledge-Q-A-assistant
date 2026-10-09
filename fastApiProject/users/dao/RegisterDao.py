from common import MySQLCommon
#查询账号是否存在
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
    MySQLCommon.close_mysql_conn(cur,conn)
    if result:
        email=result[0]['email']
        print("用户已存在")
        return  {
            "code":200,
            "msg":"查询成功",
            "data":email
        }
    return {
        "code": 500,
        "msg": "查询失败",
        "data": None
    }
# 添加数据到数据库
def add_mysql(email,ha_password,username,role):
    #连接数据库
    conn = MySQLCommon.get_mysql_conn()
    #添加游标对象
    cur = conn.cursor()
    try:
        #添加数据
        sql ="insert into `userinformation` values (null ,%s,%s,%s,%s)"
        #执行操作
        cur.execute(sql,[email,ha_password,username,role])
        #提交事务
        conn.commit()
        print("添加成功")
        # cur.lastrowid # 返回的是最后一条插入记录的 ID。
        return {"code":200}
    except Exception as e:
        conn.rollback()
        print(e)
        return {"code":500}
    finally:
        MySQLCommon.close_mysql_conn(cur,conn)

if __name__ == '__main__':
    add_mysql(3131355723,123,"yy")
