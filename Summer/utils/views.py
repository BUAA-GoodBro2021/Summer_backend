from django.forms import model_to_dict
from django.http import HttpResponse
from django.core.cache import cache
from django.shortcuts import render

from properties import production_base_url
from utils.Login_utils import *
from utils.Redis_utils import *
from utils.tasks import *


# 通过邮箱激活用户
def active(request, token):
    """
    :param request: 请求体
    :param token:   登录令牌
    :return:        各种情况的邮件主页渲染
    """
    # 校验令牌
    payload = check_token(token)

    # 邮件信息
    content = {'url': production_base_url}

    # 校验失败
    if payload is None:
        content["title"] = "操作失败"
        content["message"] = "链接失效啦！"
        return render(request, 'EmailContent-check.html', content)

    # 获取邮件中的信息
    user_id = payload.get('user_id')

    # 获取用户信息
    try:
        user = User.objects.get(id=user_id)
    except Exception:
        # 返回修改成功的界面
        content["title"] = "激活失败"
        content["message"] = "有其他好兄弟比你稍微快一点，使用相同的用户名激活邮箱啦，再去挑选一个你喜欢的用户名叭！"
        return render(request, 'EmailContent-check.html', content)

    # 获取到用户名
    username = user.username

    # 使用邮箱激活账号
    if 'email' in payload.keys():
        email = payload.get('email')

        # 激活用户 验证邮箱
        user.is_active = True
        user.email = email

        # TODO 设置随机头像
        # avatar_url = default_avatar_url_match + str(random.choice(range(1, 301))) + '.png'
        # user.avatar_url = avatar_url

        user.save()

        # 删除其他伪用户
        user_list = User.objects.filter(username=username, is_active=False)
        if user_list:
            user_list.delete()

        # TODO 发送站内信

        # 返回注册成功的界面
        content["title"] = "感谢注册"
        content["message"] = "注册Summer平台成功！"
        return render(request, 'EmailContent-check.html', content)

    # 重设密码
    if 'password' in payload.keys():
        password = payload.get('password')

        # 修改密码
        user.password = password
        user.save()

        # TODO 发送站内信

        # 返回修改成功的界面
        content["title"] = "修改成功"
        content["message"] = "修改密码成功！"
        return render(request, 'EmailContent-check.html', content)


"""""""""
测试路由部分
"""""""""


# 测试登录装饰器
@login_checker
def test_login_checker(request):
    print(request.user_id)
    return HttpResponse(request.user_id)


# 测试异步消息队列
@login_checker
def test_celery(request):

    # 通过装饰器获得id
    user_id = request.user_id

    # 获取信息
    user_key, user_dict = cache_get_by_id('user', 'user', user_id)

    # 修改信息，同步缓存
    user_dict['message_num'] += 1
    cache.set(user_key, user_dict)

    # 同步mysql
    celery_add_message_num.delay(user_id)

    return JsonResponse(user_dict)
