#加密密码
from passlib.context import CryptContext
crypt =CryptContext(schemes=["bcrypt"],deprecated="auto")
def hash_password(password:str) -> str:
    return crypt.hash(str(password))

#验证密码
def verify_password(password:str, hashed_password:str) -> bool:
    return crypt.verify(str(password), hashed_password)
if __name__ == '__main__':
    verify_password(22)