from users.dao import RegisterDao
from users.util import RegisterUtil
#注册账号
def register_user(email, password,username):
    data = RegisterDao.inquire_users(email)
    if email ==data["data"]:
        return {
            "code":201,
            "msg":"用户已存在",
            "data":None
        }
    role ="user"
    ha_password= RegisterUtil.hash_password(password)
    data = RegisterDao.add_mysql(email,ha_password,username,role)
    if data['code']==200:
        return {
            "code":200,
            "msg":"添加成功",
            "data":None
        }
    return {
        "code": 500,
        "msg": "添加失败",
        "data": None
    }
if __name__ == '__main__':
    register_user("3131355723@qq.com",20030910,"y")