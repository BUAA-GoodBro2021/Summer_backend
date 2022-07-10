"""
用户相关的函数式响应
"""
from user.models import User
from utils.Sending_utils import *


# 用户注册(不需要登录状态检验)
def register(request):
    """
    :param request: 请求体
    :return:        1 - 成功， 0 - 失败

    请求体包含包含 username，password1，password2，email
    """
    if request.method == 'POST':

        # 获取表单信息
        username = request.POST.get('username', '')
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if len(username) == 0 or len(password1) == 0 or len(password2) == 0:
            result = {'result': 0, 'message': r'用户名与密码不允许为空!'}
            return JsonResponse(result)

        if User.objects.filter(username=username, is_active=True).exists():
            result = {'result': 0, 'message': r'用户已存在!'}
            return JsonResponse(result)

        if password1 != password2:
            result = {'result': 0, 'message': r'两次密码不一致!'}
            return JsonResponse(result)

        email = request.POST.get('email', '')

        if len(email) == 0:
            result = {'result': 0, 'message': r'邮箱不允许为空!'}
            return JsonResponse(result)

        # 生成假用户
        user = User.objects.create(username=username, password=password1, is_active=False)

        # 需要加密的信息
        payload = {
            'user_id': user.id,
            'email': email,
        }
        # 发送注册邮件
        send_result = send_email(payload, email, 'register')
        if not send_result:
            result = {'result': 0, 'message': r'发送失败!请检查邮箱格式'}
            return JsonResponse(result)
        else:
            result = {'result': 1, 'message': r'发送成功!请及时在邮箱中查收.'}
            return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 用户注册(不需要登录状态检验)
def login(request):
    """
    :param request: 请求体
    :return:        1 - 成功， 0 - 失败

    请求体包含包含 username，password
    """
    if request.method == 'POST':

        # 获取表单信息
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        if len(username) == 0 or len(password) == 0:
            result = {'result': 0, 'message': r'用户名与密码不允许为空!'}
            return JsonResponse(result)

        if not User.objects.filter(username=username, is_active=True).exists():
            result = {'result': 0, 'message': r'用户不存在!'}
            return JsonResponse(result)

        # 获取用户实体
        user = User.objects.get(username=username, is_active=True)

        if user.password != password:
            result = {'result': 0, 'message': r'用户名或者密码有误!'}
            return JsonResponse(result)

        # 需要加密的信息
        payload = {
            'user_id': user.id,
            'is_super_admin': user.is_super_admin
        }
        # 签发登录令牌
        token = sign_token(payload)
        result = {'result': 1, 'message': r"登录成功！", 'token': token}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)
