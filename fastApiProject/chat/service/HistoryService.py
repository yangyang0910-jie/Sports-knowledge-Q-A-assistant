from chat.dao import HistoryDao, QueryOneDao, DeleteOneDao


#历史记录菜单栏
def history_menu(username):
    datas = HistoryDao.history_menu_dao(username)
    result =[]
    for data in datas:
        result.append({
            "dialogueId":data['dialogue_id'],
            "question":data['question'],
            # "time":data['data_time'].strftime('%Y-%m-%d %H:%M:%S'),
            "active": "false"
        })
    print(result)
    return{
        "code":200,
        "msg":"获得历史记录",
        "data":result
    }
#查询某场对话的完整历史
def query_one_history(dialogueId):
    datas = QueryOneDao.query_one_history_dao(dialogueId)
    result = []
    for r in datas:
        result.append({
            "role": "user",
            "content": r['question'],
            "compressed": bool(r['is_compressed']),   #压缩标记
            "round": r['round_number'] or 0           #所属轮次
        })
        result.append({
            "role": "assistant",
            "content": r['answer'],
            "compressed": bool(r['is_compressed']),
            "round": r['round_number'] or 0
        })
    return {"code": 200, "msg": "查询成功", "data": result}

#删除历史记录
def delete_one_history(dialogueId):
    datas =DeleteOneDao.delete_one_dao(dialogueId)
    if datas ==200:
        return {
            "code":200,
            "msg":"删除成功",
            "data":None
        }
    return {
        "code":500,
        "msg":"删除失败",
        "data":None
    }

#搜索菜单栏的记录
def search_menu(username,question):
    result= HistoryDao.search_menu_dao(username,question)
    return {
        "code": 200,
        "msg": "查询成功",
        "data": result
    }