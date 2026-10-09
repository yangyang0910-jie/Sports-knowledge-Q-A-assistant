from fastapi import APIRouter
#创建子路由对象
users_router =APIRouter()
from users.entity.RegisterEntity import RegisterEntity
from users.service import RegisterService

@users_router.post(
    path='/register',
    summary="注册账号",
)
def register_user(registerentity:RegisterEntity):
    return RegisterService.register_user(registerentity.email,registerentity.password,registerentity.username)

