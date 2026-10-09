from common import MySQLCommon
#生成菜单栏的历史记录
def history_menu_dao(username):
    #连接
    conn = MySQLCommon.get_mysql_conn()
    #创建游标对象
    cur =conn.cursor()
    #查询
    sql = "select dialogue_id,question from conversation where user_name=%s and current_id=0"
    #执行
    cur.execute(sql,[username])
    #查出结果
    result = cur.fetchall()
    #关闭
    MySQLCommon.close_mysql_conn(cur,conn)

    return result
#搜索菜单栏历史记录
def search_menu_dao(username,question):
    # 连接
    conn = MySQLCommon.get_mysql_conn()
    # 创建游标对象
    cur = conn.cursor()
    # 查询
    sql = "select question from conversation where question LIKE %s and user_name=%s and current_id=0"
    # 执行
    cur.execute(sql, ['%' + question + '%',username])
    # 查出结果
    result = cur.fetchall()
    # 关闭
    MySQLCommon.close_mysql_conn(cur, conn)

    return result