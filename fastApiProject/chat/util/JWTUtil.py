from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os
from dotenv import load_dotenv
load_dotenv()
import redis
import uuid
client = redis.Redis(host="localhost", port=6379, db=1, decode_responses=True)
#生成token
def create_token(data:dict):
    copy_data = data.copy()
    #设置token过期时间
    expire = datetime.now(timezone.utc) + timedelta(minutes=int(os.getenv('EFFECTIVE_TIME')))
    #修改data数据
    copy_data.update({
        'exp': expire,
        'iat': datetime.now(timezone.utc),
        'username':data.get("username"),
        'user_id':data.get("user_id"),
        'role':data.get("role"),
        'jti': str(uuid.uuid4())
    })
    #生成token
    return  jwt.encode(
        claims=copy_data,
        key=os.getenv('SECRET_KEY'),
        algorithm=os.getenv('ALGORITHM')
    )

#验证token
def verify_token(token:str):
    try:
        payload = jwt.decode(token, key=os.getenv('SECRET_KEY'), algorithms=[os.getenv('ALGORITHM')])
        return  payload
    except JWTError:
        return None

#拦截器----可以自动获取token，不然就要自己去调用
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/login")
def get_user(token:Annotated[str,Depends(oauth2_scheme)]):
    verify=verify_token(token)
    if verify==None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token已过期或无效",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if is_blacklisted(verify["jti"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token已注销",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = verify.get("user_id")
    # 判断 ---- 假设数据
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )
    return verify

#get_user返回的数据格式：{'exp': ..., 'iat': ..., 'username': '张三', 'user_id': 1, 'role': 'user'}

#存入黑名单
def add_to_blacklist(jti: str, exp: int) -> bool:
    """退出时调用：把 jti 写入黑名单，TTL 为剩余寿命"""
    remaining = exp - int(datetime.now(timezone.utc).timestamp())
    if remaining <= 0:
        return False
    client.set(f"blacklist:{jti}", "revoked", ex=remaining)
    return True

def is_blacklisted(jti: str) -> bool:
    """每次请求调用：检查 jti 是否在黑名单"""
    return client.exists(f"blacklist:{jti}") == 1
