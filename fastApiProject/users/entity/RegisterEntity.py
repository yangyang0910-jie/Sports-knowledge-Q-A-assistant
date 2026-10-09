from pydantic import BaseModel,Field
class RegisterEntity(BaseModel):
    email:str = Field(...,description="账号")
    password:str = Field(...,description="密码")
    username:str = Field(...,description="用户名")
