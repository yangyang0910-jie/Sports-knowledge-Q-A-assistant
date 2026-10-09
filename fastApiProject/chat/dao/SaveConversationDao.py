from common import MySQLCommon

#保存对话
def saveConversationDao(current_id,username,question,answer):
    conn = MySQLCommon.get_mysql_conn()
    cur = conn.cursor()
    try:
        current_id = int(current_id)
        #计算轮次：新会话第1轮；旧会话查它已有几轮再+1
        if current_id == 0:
            round_number = 1
        else:
            cur.execute(
                "SELECT IFNULL(MAX(round_number),0)+1 AS rn FROM conversation WHERE current_id=%s OR dialogue_id=%s",
                [current_id, current_id]
            )
            round_number = cur.fetchone()['rn']

        sql = """
            INSERT INTO conversation
                (current_id, user_name, question, answer, is_compressed, round_number)
            VALUES (%s,%s,%s,%s,0,%s)
        """
        cur.execute(sql, [current_id, username, question, answer, round_number])
        conn.commit()
        print("提交成功")
        return cur.lastrowid
    except Exception as e:
        conn.rollback()
        print(f"添加失败:{e}")
        return 0
    finally:
        MySQLCommon.close_mysql_conn(cur,conn)