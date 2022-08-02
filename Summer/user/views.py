"""
用户相关的函数式响应
"""
from django.core.cache import cache

from user.models import *
from user.tasks import *
from utils.File_utils import *
from utils.Sending_utils import *


# 用户注册
def register(request):
    """
    :param request: 请求体
    :return:        1 - 成功， 0 - 失败

    请求体包含包含 username，password1，password2，email
    """
    if request.method == 'POST':

        # 获取表单信息
        username = request.POST.get('username', '')
        real_name = request.POST.get('real_name', '')
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if len(username) == 0 or len(real_name) == 0 or len(password1) == 0 or len(password2) == 0:
            result = {'result': 0, 'message': r'用户名, 真实姓名与密码不允许为空!'}
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
        user = User.objects.create(username=username, real_name=real_name, password=hash_encode(password1),
                                   is_active=False)

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


# 用户注册
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

        if user.password != hash_encode(password):
            result = {'result': 0, 'message': r'用户名或者密码有误!'}
            return JsonResponse(result)

        # 需要加密的信息
        payload = {
            'user_id': user.id,
        }
        # 签发登录令牌
        token = sign_token(payload, exp=3600 * 24 * 600)

        # 获取缓存信息
        user_key, user_dict = cache_get_by_id('user', 'user', user.id)

        result = {'result': 1, 'message': r"登录成功！", 'token': token, 'user': user_dict}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 找回密码
def find_password(request):
    if request.method == 'POST':
        # 获取表单信息
        username = request.POST.get('username', '')
        # 是否存在该用户
        if not User.objects.filter(username=username).exists():
            result = {'result': 0, 'message': r'用户名不存在!'}
            return JsonResponse(result)
        # 获取该用户实体
        user = User.objects.get(username=username)
        # 获取密码
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if len(password1) == 0 or len(password2) == 0:
            result = {'result': 0, 'message': r'用户名与密码不允许为空!'}
            return JsonResponse(result)

        if password1 != password2:
            result = {'result': 0, 'message': r'两次密码不一致!'}
            return JsonResponse(result)

        email = user.email
        # 需要加密的信息
        payload = {
            'user_id': user.id,
            'password': hash_encode(password1),
        }
        # 发送邮件
        send_result = send_email(payload, email, 'find')
        if not send_result:
            result = {'result': 0, 'message': r'发送失败!请检查邮箱格式'}
            return JsonResponse(result)
        else:
            result = {'result': 1, 'message': r'发送成功!请及时在邮箱中完成修改密码的确认.'}
            return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 上传头像
@login_checker
def upload_avatar(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取用户上传的头像并保存
    avatar = request.FILES.get("avatar", None)
    # 获取文件尾缀并修改名称
    suffix = '.' + (avatar.name.split("."))[-1]
    avatar.name = str(user_id) + suffix
    # 保存至media
    user = User.objects.get(id=user_id)
    user.avatar = avatar
    user.save()

    # 获取上传结果
    upload_result = upload_image(avatar, "avatar-summer", user_id)

    if upload_result['result'] == 0:
        return JsonResponse(upload_result)

    # 获取图片路由
    avatar_url = upload_result['image_url']
    # 获取信息
    user_key, user_dict = cache_get_by_id('user', 'user', user_id)
    # 修改信息，同步缓存
    user_dict['avatar_url'] = avatar_url
    cache.set(user_key, user_dict)
    # 同步mysql
    celery_change_avatar.delay(user_id, avatar_url)

    result = {'result': 1, 'message': r"上传成功！", 'user': user_dict}
    return JsonResponse(result)


# 查看用户的团队列表
@login_checker
def list_team(request):
    # 获取用户信息
    user_id = request.user_id
    # 用户所有关联团队的信息
    user_to_team_list = UserToTeam.objects.filter(user_id=user_id)
    # 团队信息
    team_list = []
    for every_user_to_team in user_to_team_list:
        # 获取缓存信息
        team_key, team_dict = cache_get_by_id('team', 'team', every_user_to_team.team_id)
        team_list.append(team_dict)
    user_key, user_dict = cache_get_by_id('user', 'user', user_id)

    result = {'result': 1, 'message': r"查询团队成功成功！", 'user': user_dict, 'team_list': team_list}
    return JsonResponse(result)


# 查看用户的星标列表
@login_checker
def list_star(request):
    # 获取用户信息
    user_id = request.user_id
    # 用户所有关联团队的信息
    user_to_project_star_list = UserToProjectStar.objects.filter(user_id=user_id, is_delete=0)
    # 团队信息
    project_list = []
    for every_user_to_project_star_list in user_to_project_star_list:
        # 获取缓存信息
        project_key, project_dict = cache_get_by_id('project', 'project', every_user_to_project_star_list.project_id)
        project_list.append(project_dict)
    user_key, user_dict = cache_get_by_id('user', 'user', user_id)

    result = {'result': 1, 'message': r"查询星标项目成功成功！", 'user': user_dict, 'project_list': project_list}
    return JsonResponse(result)
