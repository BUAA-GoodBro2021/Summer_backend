from django.core.cache import cache
from project.tasks import *

from project.models import Project
from team.models import TeamToProject
from user.models import *
from utils.Login_utils import *


# 新建一个项目
@login_checker
def create_project(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    team_id = request.POST.get('team_id', 0)
    project_name = request.POST.get('project_name', '')
    project_description = request.POST.get('project_description', '')

    # 判断权限
    if not UserToTeam.objects.filter(user_id=user_id, team_id=team_id).exists():
        result = {'result': 0, 'message': r'你不属于该团队, 请联系该团队的管理员申请加入!'}
        return JsonResponse(result)

    # 创建一个项目对象
    project = Project.objects.create(project_name=project_name, project_description=project_description)
    # 创建团队与项目的关系
    TeamToProject.objects.create(team_id=team_id, project_id=project.id)

    # TODO 创建一个原型设计界面

    # TODO 创建原型设计界面与项目之间的关系

    # 获取缓存信息
    user_key, user_dict = cache_get_by_id('user', 'user', user_id)
    team_key, team_dict = cache_get_by_id('team', 'team', team_id)
    project_key, project_dict = cache_get_by_id('project', 'project', project.id)

    # 修改信息，同步缓存(TODO 项目的文件数量+1, 团队的项目数量+1)
    team_dict['project_num'] += 1
    cache.set(team_key, team_dict)
    # project_dict['file_num'] += 1
    # cache.set(project_key, project_dict)

    # 同步mysql(TODO 项目的文件数量+1, 团队的项目数量+1)
    celery_create_project.delay(team_id, project.id)

    # TODO 返回值应该包含生成的原型设计界面的信息
    result = {'result': 1, 'message': r'创建项目成功!', 'user': user_dict, 'project': project_dict}
    return JsonResponse(result)


# 重命名一个项目
@login_checker
def rename_project(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    team_id = request.POST.get('team_id', 0)
    project_id = request.POST.get('project_id', 0)
    project_name = request.POST.get('project_name', '')
    project_description = request.POST.get('project_description', '')

    # 判断权限
    if not UserToTeam.objects.filter(user_id=user_id, team_id=team_id).exists():
        result = {'result': 0, 'message': r'你不属于该团队, 请联系该团队的管理员申请加入!'}
        return JsonResponse(result)

    # 修改信息，同步缓存
    user_key, user_dict = cache_get_by_id('user', 'user', user_id)
    project_key, project_dict = cache_get_by_id('project', 'project', project_id)

    project_dict['project_name'] = project_name
    project_dict['project_description'] = project_description
    cache.set(project_key, project_dict)

    # 同步mysql
    celery_rename_project.delay(project_id, project_name, project_description)

    result = {'result': 1, 'message': r'修改项目信息成功!', 'user': user_dict, 'project': project_dict}
    return JsonResponse(result)


# 将项目放入回收站
@login_checker
def remove_project_to_bin(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    team_id = request.POST.get('team_id', '')
    project_id = request.POST.get('project_id', '')

    # 判断权限
    if not UserToTeam.objects.filter(user_id=user_id, team_id=team_id).exists():
        result = {'result': 0, 'message': r'你不属于该团队, 请联系该团队的管理员申请加入!'}
        return JsonResponse(result)

    # 修改信息，同步缓存
    project_key, project_dict = cache_get_by_id('project', 'project', project_id)

    # 是否已经在回收站里面
    if project_dict['is_delete'] == 1:
        result = {'result': 0, 'message': r'该项目已经添加至回收站，请勿重复添加!'}
        return JsonResponse(result)

    project_dict['is_delete'] = 1
    cache.set(project_key, project_dict)

    # 同步mysql
    celery_remove_project_to_bin.delay(user_id, project_id)

    user_key, user_dict = cache_get_by_id('user', 'user', user_id)
    result = {'result': 1, 'message': r'将项目放入回收站成功!', 'user': user_dict}
    return JsonResponse(result)


# 将回收站中的项目恢复
@login_checker
def recover_project_from_bin(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    project_id = request.POST.get('project_id', '')

    # 修改信息，同步缓存
    project_key, project_dict = cache_get_by_id('project', 'project', project_id)

    # 是否已经在回收站里面
    if project_dict['is_delete'] == 0:
        result = {'result': 0, 'message': r'该项目已经恢复，请勿重复恢复!'}
        return JsonResponse(result)

    project_dict['is_delete'] = 0
    cache.set(project_key, project_dict)

    # 同步mysql
    celery_recover_project_from_bin.delay(user_id, project_id)

    user_key, user_dict = cache_get_by_id('user', 'user', user_id)
    result = {'result': 1, 'message': r'将回收站恢复成功!', 'user': user_dict}
    return JsonResponse(result)


# 设置星标项目
@login_checker
def add_star_project(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    project_id = request.POST.get('project_id', '')
    # 如果已经设置为星标项目了
    if UserToProjectStar.objects.filter(user_id=user_id, project_id=project_id).exists():
        result = {'result': 0, 'message': r'已经设置为星标，请勿重复设置!'}
        return JsonResponse(result)
    # 创建关联
    UserToProjectStar.objects.create(user_id=user_id, project_id=project_id)
    user_key, user_dict = cache_get_by_id('user', 'user', user_id)
    result = {'result': 1, 'message': r'设置星标成功!', 'user': user_dict}
    return JsonResponse(result)


# 取消设置星标项目
@login_checker
def del_star_project(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    project_id = request.POST.get('project_id', '')
    # 如果已经设置为星标项目了
    if not UserToProjectStar.objects.filter(user_id=user_id, project_id=project_id).exists():
        result = {'result': 0, 'message': r'已经取消星标，请勿重复取消!'}
        return JsonResponse(result)
    # 删除关联
    UserToProjectStar.objects.filter(user_id=user_id, project_id=project_id).delete()
    user_key, user_dict = cache_get_by_id('user', 'user', user_id)
    result = {'result': 1, 'message': r'取消星标成功!', 'user': user_dict}
    return JsonResponse(result)
