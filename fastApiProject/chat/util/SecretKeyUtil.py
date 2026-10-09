import secrets
# 生成32位密钥 ------每次生成的都不一样所以需要存起来
key =secrets.token_urlsafe(32) #返回的是字节
print(key)