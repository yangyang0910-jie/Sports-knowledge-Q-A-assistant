from fastapi import APIRouter, Depends
from chat.util.JWTUtil import get_user
from chat.service import HistoryService
history_router = APIRouter(dependencies=[Depends(get_user)])
@history_router.get(
    path="/historyMenu",
    summary="历史记录菜单栏"
)
def history_menu(name:dict = Depends(get_user)):
    username =name.get('username')
    return HistoryService.history_menu(username)

@history_router.get(
    path="/queryOneHistory",
    summary="查询单条历史记录"
)
def query_one_history(dialogueId):
    return HistoryService.query_one_history(dialogueId)

@history_router.get(
    path="/deleteOneHistory",
    summary="删除历史记录",
)
def delete_one_history(dialogueId):
    return HistoryService.delete_one_history(dialogueId)

@history_router.get(
    path="/searchMenu",
    summary="搜索菜单栏的历史记录",
)
def search_menu(question:str,name:dict = Depends(get_user)):
    username = name.get('username')
    return HistoryService.search_menu(username,question)