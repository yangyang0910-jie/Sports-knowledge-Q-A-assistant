from common import MySQLCommon
# 删除某一条历史记录
def delete_one_dao(dialogueId):
    conn=MySQLCommon.get_mysql_conn()
    cur=conn.cursor()
    sql="delete from conversation where dialogue_id=%s or current_id=%s"
    try:
        cur.execute(sql,[dialogueId,dialogueId])
        conn.commit()
        print("删除成功")
        return 200
    except Exception as e:
        conn.rollback()
        print(f"删除失败:{e}")
        return 500
    finally:
        MySQLCommon.close_mysql_conn(cur,conn)
