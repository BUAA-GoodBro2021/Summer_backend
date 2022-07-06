"""
Django Login Utils
"""
import hashlib
import time
import jwt
from django.http import JsonResponse

from key import TOKEN_SECRET_KEY


# Hash-md5 加密字符串
def hash_encode(str_key):
    """
    :param str_key: 需要使用 md5 加密的字符串
    :return: md5 加密后的字符串
    哈希算法 - 给定明文，计算出定长的，不可逆的值
    """
    # 生成一个 md5 加密对象
    md5 = hashlib.md5()
    # 进行 md5 加密(要求加密字符串为二进制形式，需要进行encode操作)
    md5.update(str_key.encode())
    # 完成加密
    return md5.hexdigest()


# 签发登录令牌
def sign_token(payload, exp=3600 * 24):
    """
    :param payload: 私有声明字典
    :param exp: 过期时间
    :return: 签发的登录令牌
    """
    # 获取当前时间戳，并计算得到该令牌的过期时间
    payload['exp'] = time.time() + exp
    # 使用 HS256 算法配合密钥签发登录令牌
    token = jwt.encode(payload, TOKEN_SECRET_KEY, algorithm='HS256')
    return token


# 登录状态检测装饰器
def login_decorator(func):
    def wrap(request, *args, **kwargs):
        # 校验请求方式
        if request.method != 'POST':
            result = {'result': 0, 'msg': '请求方式错误'}
            return JsonResponse(result)

        # 获取token request.POST.get('token')
        token = request.POST.get('token', '')

        # token是否存在
        if len(token) == 0:
            result = {'result': -1, 'msg': '请先登录'}
            return JsonResponse(result)

        # 校验token
        try:
            # 查看令牌是否过期或者被篡改
            payload = jwt.decode(token, TOKEN_SECRET_KEY, algorithms=['HS256'])
        except Exception as e:
            # 如果失败需要进行重新登录
            result = {'result': -1, 'msg': r"请重新登录!"}
            return JsonResponse(result)

        # 获取令牌中的user_id信息
        user_id = payload.get('user_id', '')
        request.user_id = user_id

        return func(request, *args, **kwargs)
    return wrap
