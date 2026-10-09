from common import MySQLCommon

#查询某一条历史记录
from common import MySQLCommon

#查询某场对话的历史记录（带压缩标记和轮次）
def query_one_history_dao(dialogueId):
    conn = MySQLCommon.get_mysql_conn()
    cur = conn.cursor()
    sql = """
        SELECT question, answer, is_compressed, round_number
        FROM conversation
        WHERE current_id=%s OR dialogue_id=%s
        ORDER BY dialogue_id
    """
    cur.execute(sql, [dialogueId, dialogueId])
    result = cur.fetchall()
    MySQLCommon.close_mysql_conn(cur, conn)
    return result