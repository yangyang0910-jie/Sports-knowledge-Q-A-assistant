from pydantic import BaseModel,Field

class LoginEntity(BaseModel):
    email: str=Field(...,description="账号")
    password: str=Field(...,description="密码")
