"""
Redis操作相关工具类
"""
import redis
from properties import *


# 继承 redis.Redis ,并添加一些自己的方法
class Redis_utils(redis.Redis):

    # 初始化对象,和 r = redis.Redis() 一致
    def __init__(self, host=redis_HOST, port=redis_PORT, db=0, password=redis_PASSWORD):
        super().__init__(host=host, port=port, db=db, password=password)

    # 对 redis 中的哈希结构的取值进行简化(需要进行字节解码编码之间的转换)
    def hgetall_str(self, name):
        bytes_dict = self.hgetall(name)
        print(bytes_dict)
        return {key.decode('utf-8'): value.decode('utf-8') for key, value in bytes_dict.items()}
