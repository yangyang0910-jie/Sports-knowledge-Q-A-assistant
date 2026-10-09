from common import MySQLCommon

# 获取未压缩消息（按会话ID查，带 is_compressed=0 过滤，杜绝重复压缩）
def get_uncompressed_messages_dao(session_id):
    conn = MySQLCommon.get_mysql_conn()
    cur = conn.cursor()
    # current_id = 会话ID；dialogue_id = 会话ID 兼容"会话第一行"(首轮 current_id=0)
    sql = """SELECT question, answer, round_number
             FROM conversation
             WHERE (current_id = %s OR dialogue_id = %s) AND is_compressed = 0
             ORDER BY round_number"""
    try:
        cur.execute(sql, [session_id, session_id])
        result = cur.fetchall()
        print(f"查询未压缩消息成功，共 {len(result)} 条")
        return result
    except Exception as e:
        print(f"查询未压缩消息失败:{e}")
        return []
    finally:
        MySQLCommon.close_mysql_conn(cur, conn)


# 获取未压缩消息的最大轮数
def get_max_uncompressed_round_dao(session_id):
    conn = MySQLCommon.get_mysql_conn()
    cur = conn.cursor()
    sql = """SELECT MAX(round_number) AS max_round
             FROM conversation
             WHERE (current_id = %s OR dialogue_id = %s) AND is_compressed = 0"""
    try:
        cur.execute(sql, [session_id, session_id])
        result = cur.fetchone()
        if result and result['max_round'] is not None:
            return result['max_round']
        return 0
    except Exception as e:
        print(f"查询最大轮数失败:{e}")
        return 0
    finally:
        MySQLCommon.close_mysql_conn(cur, conn)


# 历史记录压缩保存（dialogid 列存的是"会话ID"，如 88）
def compress_save_dao(new_summary, session_id, lastround):
    conn = MySQLCommon.get_mysql_conn()
    cur = conn.cursor()
    sql = "INSERT INTO compress (conpresstext, dialogid, lastround, createtime) VALUES (%s, %s, %s, now())"
    try:
        cur.execute(sql, [new_summary, session_id, lastround])
        conn.commit()
        print("保存成功")
        return 200
    except Exception as e:
        conn.rollback()
        print(f"保存失败:{e}")
        return 500
    finally:
        MySQLCommon.close_mysql_conn(cur, conn)


# 标记已压缩（按轮次边界 + 会话ID，含会话第一行）
def compress_dao(round_number, session_id):
    conn = MySQLCommon.get_mysql_conn()
    cur = conn.cursor()
    sql = """UPDATE conversation SET is_compressed = 1
             WHERE round_number <= %s
               AND round_number IS NOT NULL
               AND (current_id = %s OR dialogue_id = %s)"""
    try:
        cur.execute(sql, [round_number, session_id, session_id])
        conn.commit()
        print("更新压缩状态成功")
        return 200
    except Exception as e:
        conn.rollback()
        print(f"更新失败:{e}")
        return 500
    finally:
        MySQLCommon.close_mysql_conn(cur, conn)


# 获取旧摘要（compress.dialogid 存的是会话ID）
def get_summary_from_db(session_id):
    conn = MySQLCommon.get_mysql_conn()
    cur = conn.cursor()
    sql = "SELECT conpresstext FROM compress WHERE dialogid = %s ORDER BY lastround DESC LIMIT 1"
    try:
        cur.execute(sql, [session_id])
        result = cur.fetchone()
        print("查询成功")
        if result:
            return result['conpresstext']
        return None
    except Exception as e:
        print(f"查询失败:{e}")
        return None
    finally:
        MySQLCommon.close_mysql_conn(cur, conn)
