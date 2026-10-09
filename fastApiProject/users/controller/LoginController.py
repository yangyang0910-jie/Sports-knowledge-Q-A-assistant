from fastapi import APIRouter
login_router =APIRouter()
from users.entity.LoginEntity import LoginEntity

from users.service import LoginService
@login_router.post(
    path="/login",
    summary="用密码登录账户"
)
def login_user(loginentity: LoginEntity):
    return LoginService.login_user(loginentity.email,loginentity.password)

@login_router.get(
    path="/sendcode",
    summary="用验证码登录"
)
def send_code(email):
    return LoginService.send_code(email)
@login_router.get(
    path="/checkcode",
    summary="验证验证码"
)
def check_code(email,code):
    return LoginService.check_code(email,code)