import os
from dotenv import load_dotenv
import redis

load_dotenv()

# 获取连接
def get_redis_conn():
    return redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=int(os.getenv("REDIS_PORT")),
        db=int(os.getenv("REDIS_DB")),
        # 如果redis无法存入数据，添加下面的配置protocol=2 3 中的一个，应该是2
        # protocol=2,
        decode_responses=True
    )

# 关闭连接
def close_redis_conn(conn):
    conn.close()
