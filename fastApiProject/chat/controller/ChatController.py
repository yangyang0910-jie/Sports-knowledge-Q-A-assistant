from typing import Annotated
from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse
from chat.service import ChatService
from chat.util.JWTUtil import get_user, add_to_blacklist
from chat.entity.SaveConversationEntity import SaveConversationEntity
import json
chat_router = APIRouter(dependencies=[Depends(get_user)])
@chat_router.get(
    path="/chat",
    summary="对话聊天",
)
def chat(question:str,dialogueId:str):
    # 只要代码能走到这里，说明前端肯定带了合法的 Token！
    # 如果没带 Token，或者 Token 过期，上面那一行就会直接报 401 错误，根本进不来
    def generation():
        for data in ChatService.chat(question,dialogueId):
              yield f"data:{json.dumps({'content':data})}\n\n"
        yield f"data:{json.dumps({'content': '[done]'})}\n\n"

    return StreamingResponse(
        content=generation(),
        media_type="text/event-stream"
    )
@chat_router.post(
    path="/saveConversation",
    summary="保存历史记录",
)
def save_conversation(saveconversationentity: SaveConversationEntity,name: dict = Depends(get_user)):
    username = name.get("username")
    return ChatService.save_conversation(saveconversationentity,username)

@chat_router.post(
    path="/logout",
    summary="退出登录",
)
def logout(user: Annotated[dict, Depends(get_user)]):
    add_to_blacklist(user["jti"], user["exp"])
    return {"detail": "退出成功"}