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
    team_id = request.POST.get('team_id', '')
    project_name = request.POST.get('project_name', '')

    # 判断权限
    if not UserToTeam.objects.filter(user_id=user_id, team_id=team_id).exists():
        result = {'result': 0, 'message': r'你不属于该团队, 请联系该团队的管理员申请加入!'}
        return JsonResponse(result)

    # 创建一个项目对象
    project = Project.objects.create(project_name=project_name)
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
    cache.set(user_key, user_dict)
    # project_dict['file_num'] += 1
    # cache.set(project_key, project_key)

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
    team_id = request.POST.get('team_id', '')
    project_id = request.POST.get('project_id', '')
    project_name = request.POST.get('project_name', '')

    # 判断权限
    if not UserToTeam.objects.filter(user_id=user_id, team_id=team_id).exists():
        result = {'result': 0, 'message': r'你不属于该团队, 请联系该团队的管理员申请加入!'}
        return JsonResponse(result)

    # 修改信息，同步缓存
    user_key, user_dict = cache_get_by_id('user', 'user', user_id)
    project_key, project_dict = cache_get_by_id('project', 'project', project_id)

    project_dict['project_name'] = project_name
    cache.set(project_key, project_key)

    # 同步mysql
    celery_rename_project.delay(project_id, project_name)

    result = {'result': 1, 'message': r'重命名项目成功!', 'user': user_dict, 'project': project_dict}
    return JsonResponse(result)
