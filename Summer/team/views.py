import random

from django.core.cache import cache
from team.tasks import *
from properties import *
from team.models import Team, TeamToProject
from user.models import *
from utils.Login_utils import *


# 创建团队
@login_checker
def create_team(request):
    # 获取用户信息
    user_id = request.user_id

    # 获取表单信息
    team_name = request.POST.get('team_name', '')

    if Team.objects.filter(team_name=team_name).exists():
        result = {'result': 0, 'message': r'该团队已存在, 请换一个不一样的团队名称!'}
        return JsonResponse(result)

    if len(team_name) == 0:
        result = {'result': 0, 'message': r'团队名称不允许为空!'}
        return JsonResponse(result)

    if len(team_name) > 100:
        result = {'result': 0, 'message': r'团队名称太长啦!'}
        return JsonResponse(result)

    # 获取团队随机头像
    avatar_url = default_cover_1_url_match + str(random.choice(range(1, 31))) + '.svg'

    # 创建团队实体
    team = Team.objects.create(team_name=team_name, avatar_url=avatar_url)

    # 获取缓存信息
    user_key, user_dict = cache_get_by_id('user', 'user', user_id)
    team_key, team_dict = cache_get_by_id('team', 'team', team.id)

    # 创建user与team的关系(创建者默认管理员)
    UserToTeam.objects.create(user_id=user_id, team_id=team.id, is_super_admin=1)

    # 用户的团队数+1
    # 修改信息，同步缓存
    user_dict['team_num'] += 1
    cache.set(user_key, user_dict)

    # 同步mysql
    celery_add_team_num.delay(user_id)

    result = {'result': 1, 'message': r'创建团队成功!', 'user': user_dict, 'team': team_dict}

    return JsonResponse(result)


# 查看团队信息(团队的基本信息和成员的基本信息)
@login_checker
def list_team_user(request):
    # 获取用户信息
    user_id = request.user_id

    # 获取表单信息
    team_id = request.POST.get('team_id', '')

    # 判断权限
    if not UserToTeam.objects.filter(user_id=user_id, team_id=team_id).exists():
        result = {'result': 0, 'message': r'你不属于该团队, 请联系该团队的管理员申请加入!'}
        return JsonResponse(result)

    # 团队所有关联信息
    user_to_team_list = UserToTeam.objects.filter(team_id=team_id)

    # 用户的所有信息列表
    user_list = []
    # 自己是不是超管
    is_super_admin = 0

    for every_user_to_team in user_to_team_list:
        # 获取缓存
        user_key, user_dict = cache_get_by_id('user', 'user', every_user_to_team.user_id)
        # 添加身份
        user_dict['is_super_admin'] = every_user_to_team.is_super_admin
        # 加入用户信息列表
        user_list.append(user_dict)
        # 添加权限修饰符
        if user_id == every_user_to_team.user_id:
            is_super_admin = every_user_to_team.is_super_admin

    # 获取缓存信息
    user_key, user_dict = cache_get_by_id('user', 'user', user_id)
    team_key, team_dict = cache_get_by_id('team', 'team', team_id)
    result = {'result': 1, 'message': r'查询成功!', 'user': user_dict, 'is_super_admin': is_super_admin,
              'team': team_dict, 'user_list': user_list}
    return JsonResponse(result)


# 查看团队中的所有项目信息
@login_checker
def list_team_project(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    team_id = request.POST.get('team_id', '')

    # 判断权限
    if not UserToTeam.objects.filter(user_id=user_id, team_id=team_id).exists():
        result = {'result': 0, 'message': r'你不属于该团队, 请联系该团队的管理员申请加入!'}
        return JsonResponse(result)

    # 团队所有关联信息
    team_to_project_list = TeamToProject.objects.filter(team_id=team_id)
    # 项目的所有信息列表
    project_list = []

    for every_team_to_project in team_to_project_list:
        # 修改信息，同步缓存
        project_key, project_dict = cache_get_by_id('project', 'project', every_team_to_project.project_id)
        # 只展示未删除的项目
        if project_dict['is_delete'] == 0:
            project_list.append(project_dict)

    # 获取缓存信息
    user_key, user_dict = cache_get_by_id('user', 'user', user_id)
    team_key, team_dict = cache_get_by_id('team', 'team', team_id)
    result = {'result': 1, 'message': r'查询成功!', 'user': user_dict, 'team': team_dict, 'project_list': project_list}
    return JsonResponse(result)


# 查看团队中的回收站内的项目信息
@login_checker
def list_team_bin(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    team_id = request.POST.get('team_id', '')
    # 判断权限
    if not UserToTeam.objects.filter(user_id=user_id, team_id=team_id).exists():
        result = {'result': 0, 'message': r'你不属于该团队, 请联系该团队的管理员申请加入!'}
        return JsonResponse(result)
        # 团队所有关联信息
    team_to_project_list = TeamToProject.objects.filter(team_id=team_id)
    # 项目的所有信息列表
    project_list = []

    for every_team_to_project in team_to_project_list:
        # 修改信息，同步缓存
        project_key, project_dict = cache_get_by_id('project', 'project', every_team_to_project.project_id)
        # 只展示未删除的项目
        if project_dict['is_delete'] == 1:
            project_list.append(project_dict)

    # 获取缓存信息
    user_key, user_dict = cache_get_by_id('user', 'user', user_id)
    team_key, team_dict = cache_get_by_id('team', 'team', team_id)
    result = {'result': 1, 'message': r'查询成功!', 'user': user_dict, 'team': team_dict, 'project_list': project_list}
    return JsonResponse(result)


# 分享邀请码
@login_checker
def invite_user(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    team_id = request.POST.get('team_id', '')
    # 判断权限
    if not UserToTeam.objects.filter(user_id=user_id, team_id=team_id).exists():
        result = {'result': 0, 'message': r'你不属于该团队, 请联系该团队的管理员申请加入!'}
        return JsonResponse(result)

    # 需要加密的信息
    payload = {
        'user_id': user_id,
        'team_id': team_id,
    }
    # 签发邀请码
    invitation_code = sign_token(payload, exp=3600 * 24 * 3)

    result = {'result': 1, 'message': r'邀请码生成成功, 有效期为3天!', 'invitation_code': invitation_code}
    return JsonResponse(result)


# 使用邀请码加入团队
@login_checker
def join_team(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    invitation_code = request.POST.get('invitation_code', '')
    # 校验邀请码
    payload = check_token(invitation_code)
    # 校验失败
    if payload is None:
        result = {'result': 0, 'message': r'邀请码错误或过期, 请联系该团队的管理员重新获取邀请码!'}
        return JsonResponse(result)

    # 获取邀请码信息
    team_id = payload['team_id']

    if UserToTeam.objects.filter(user_id=user_id, team_id=team_id).exists():
        result = {'result': 0, 'message': r'你已经在该团队啦, 不要重复加入!'}
        return JsonResponse(result)

    # 创建关系
    UserToTeam.objects.create(user_id=user_id, team_id=team_id)

    # 获取缓存信息
    user_key, user_dict = cache_get_by_id('user', 'user', user_id)
    team_key, team_dict = cache_get_by_id('team', 'team', team_id)

    # 用户的团队数+1, 团队人数+1
    # 修改信息，同步缓存
    user_dict['team_num'] += 1
    team_dict['user_num'] += 1
    cache.set(user_key, user_dict)
    cache.set(team_key, team_dict)

    # 同步mysql
    celery_join_team.delay(user_id, team_id)

    result = {'result': 1, 'message': r'加入团队成功!', 'user': user_dict}
    return JsonResponse(result)


# 将普通成员移除
@login_checker
def remove_user(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    team_id = request.POST.get('team_id', '')
    set_user_id = request.POST.get('set_user_id', '')

    # 判断权限
    if not UserToTeam.objects.filter(user_id=user_id, team_id=team_id, is_super_admin=1).exists():
        result = {'result': 0, 'message': r'你不属于该团队或者没有权限, 请联系该团队的管理员申请加入或者提高权限!'}
        return JsonResponse(result)

    # 该成员是否存在于组织内部
    try:
        set_user_to_team = UserToTeam.objects.get(user_id=set_user_id, team_id=team_id)
    except Exception:
        result = {'result': 0, 'message': r'该成员不在团队内部!'}
        return JsonResponse(result)

    # 检查将要操作的用户是不是为管理员
    if set_user_to_team.is_super_admin == 1:
        result = {'result': 0, 'message': r'该成员已经为管理员, 无法移除!'}
        return JsonResponse(result)

    # 关系表修正
    set_user_to_team.delete()

    # 获取缓存信息
    user_key, user_dict = cache_get_by_id('user', 'user', user_id)
    team_key, team_dict = cache_get_by_id('team', 'team', team_id)

    # 用户的团队数-1, 团队人数-1
    # 修改信息，同步缓存
    user_dict['team_num'] -= 1
    team_dict['user_num'] -= 1
    cache.set(user_key, user_dict)
    cache.set(team_key, team_dict)

    # 同步mysql
    celery_remove_user.delay(user_id, team_id)

    result = {'result': 1, 'message': r'移除该成员成功!', 'user': user_dict}
    return JsonResponse(result)


# 将普通成员变为管理员
@login_checker
def set_super_admin(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    team_id = request.POST.get('team_id', '')
    set_user_id = request.POST.get('set_user_id', '')

    # 判断权限
    if not UserToTeam.objects.filter(user_id=user_id, team_id=team_id, is_super_admin=1).exists():
        result = {'result': 0, 'message': r'你不属于该团队或者没有权限, 请联系该团队的管理员申请加入或者提高权限!'}
        return JsonResponse(result)

    # 该成员是否存在于组织内部
    try:
        set_user_to_team = UserToTeam.objects.get(user_id=set_user_id, team_id=team_id)
    except Exception:
        result = {'result': 0, 'message': r'该成员不在团队内部!'}
        return JsonResponse(result)

    # 检查将要操作的用户是不是为管理员
    if set_user_to_team.is_super_admin == 1:
        result = {'result': 0, 'message': r'该成员已经为管理员, 请勿重复设置!'}
        return JsonResponse(result)

    set_user_to_team.is_super_admin = 1
    set_user_to_team.save()

    # 获取缓存信息
    user_key, user_dict = cache_get_by_id('user', 'user', user_id)
    result = {'result': 1, 'message': r'设置为管理员成功!', 'user': user_dict}
    return JsonResponse(result)
