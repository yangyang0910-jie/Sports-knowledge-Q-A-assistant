from fastapi import FastAPI
from users.controller.RegisterController import users_router
from users.controller.LoginController import login_router
from chat.controller.ChatController import chat_router
from chat.controller.HistoryController import history_router
app = FastAPI()

# 注册子路由
app.include_router(
    router=users_router,
    prefix="/users",
    tags=["users"]
)
# 登录子路由
app.include_router(
    router=login_router,
    prefix="/users",
    tags=["users"]
)
#聊天子路由
app.include_router(
    router=chat_router,
    prefix="/chat",
    tags=["chat"]
)
#历史子路由
app.include_router(
router=history_router,
    prefix="/history",
    tags=["history"]
)
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Service is running!"}

# 启动服务
if __name__ == '__main__':
    # 导入uvicorn包来写命令启动fastapi服务器项目
    import uvicorn as uv
    # 配置启动
    uv.run(
    # 启动项目的文件，即FastAPI()对象所在的文件
    app="main:app",  # 配置启动的项目文件 --- mαin.py中的αpp对象
    host="localhost",  # 配置启动的服务器地址
    port=8000,  # 配置启动的服务器端口
    reload=False,  #配置关闭自动重启
)

#跨域配置
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"], #允许得域名 ----- 完整的客户端域名
    allow_credentials=True, #允许携带的cookie
    allow_methods=['*'],#允许请求的方法
    allow_headers=['Authorization', 'Content-Type', 'Accept'], # 允许的请求头
)