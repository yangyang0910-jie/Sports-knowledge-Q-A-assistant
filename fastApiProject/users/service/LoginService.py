import smtplib
from email.mime.text import MIMEText
import random
from users.util import RegisterUtil, RedisUtil
from users.dao import LoginDao
import os
from dotenv import load_dotenv
load_dotenv()
from chat.util import JWTUtil

#密码登录
def login_user(email, password):
    #查询用户是否存在
    data = LoginDao.inquire_users(email)
    print(data['data'])
    #{'user_id': 7, 'email': '3131355723@qq.com', 'password': '$2b$12$ly4/y5E1fw/IS0NcSyDlneU.I7e/kQajlY/algxDF9.iuEDsp8l6.', 'user_name': 'yy'}
    if data['data'] == None:
        return {
            "code": 501,
            "msg": "查询失败，用户不存在",
            "data": None
        }
    # 存在-----取出哈希密码，比对用户传来的密码
    datas = RegisterUtil.verify_password(password,data["data"]['password'])
    print("验证结果为：",datas)

    token_data = {}
    user_info = data['data']
    token_data['username'] = user_info.get('user_name')
    token_data['user_id'] = str(user_info.get('user_id'))
    token_data['role'] = user_info.get('role')
    if  datas:
        access_token = JWTUtil.create_token(token_data)
        return {
            "code": 200,
            "msg": "登录成功",
            "data": {
                "access_token":access_token,
                "token_type":"bearer",
                "username":token_data['username'],
            }
        }
    return {
            "code": 500,
            "msg": "密码输入错误",
            "data": None
    }
if __name__ == '__main__':
    login_user("3131355723@qq.com",20030910)

# 发验证码
def send_code(email):
    data=LoginDao.inquire_users(email)
    print(data["data"])
    # 判断用户是否存在
    if data["data"] is None:
        return {
            "code": 500,
            "msg": "账号不存在，请先注册",
            "data": None
        }
    username =data["data"]['user_name']
    #存在----发送验证码
    #生成4位验证码
    code=random.randint(1000,9999)
    # 配置发送消息
    sender=os.getenv("SENDER_EMAIL") #发送方，验证码从这里发出
    sender_pwd =os.getenv("SENDER_EMAIL_PASSWORD") #授权码
    subject ="这是你的验证码" #邮件主题
    content = f"验证码位为{code},有效期1分钟"

    #创建邮件对象
    message =MIMEText(content,"plain","utf-8")
    #添加内容
    message["From"]=sender
    message["To"]=email
    message["Subject"]=subject

   #发送邮件
    try:
        # 构建发送邮件的对象
        smtp =smtplib.SMTP(
            host=os.getenv("SMTP_HOST"),
            port=int(os.getenv("SMTP_PORT")),
        )
        #开启发送服务
        smtp.starttls()
        #验证发送方的邮箱和授权码是否能对上
        smtp.login(sender,sender_pwd)
        #发送邮件 ----从哪里【发送方】----到哪里【接收方】-----发送内容【邮件对象】
        smtp.sendmail(sender,email,message.as_string())
        #发送成功后退出
        smtp.quit()

        #验证码存入redis
        #连接redis
        redis = RedisUtil.get_redis_conn()
        redis.setex(email,60,code)
        RedisUtil.close_redis_conn(redis)
        return {
            "code": 200,
            "msg":"发送成功",
            "data": username
        }
    except Exception as e:
        print(f"邮件发送失败{e}")
        return {
            "code": 500,
            "msg": "发送失败",
            "data": None
        }
# if __name__ == '__main__':
#     send_code("3131355723@qq.com")


def check_code(email:str,code:str):
    #配置JWT登录接口
    data = LoginDao.inquire_users(email)
    if data["data"] is None:
        return {
            "code": 500,
            "msg": "账号不存在，请先注册",
            "data": None
        }
    token_data = {}
    user_info=data['data']
    token_data['username'] = user_info.get('user_name')
    token_data['user_id'] = str(user_info.get('user_id'))
    token_data['role'] = user_info.get('role')

    re=RedisUtil.get_redis_conn()
    datas = re.get(email)
    RedisUtil.close_redis_conn(re)
    print(type(data))
    if datas == code:
        #生成token并发送到前端
        access_token = JWTUtil.create_token(token_data)
        return {
            "code": 200,
             "msg": "验证成功",
             "data":{
                "access_token":access_token,
                "token_type":"bearer",
                 "username": token_data['username']
            }
        }
    if datas == None:
        return {
        "code": 500,
        "msg": "验证码已过期",
        "data": None,
    }
    return {
        "code": 500,
        "msg": "验证输入错误",
        "data": None,
    }


# if __name__ == '__main__':
#     check_code("3131355723@qq.com",4479)