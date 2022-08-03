from page.models import *
from project.models import *
from team.models import TeamToProject
from user.models import UserToTeam
from utils.Login_utils import *
from utils.Redis_utils import *
from page.tasks import *


# 权限判断
def check_authority(user_id, team_id, project_id, page_id):
    if not UserToTeam.objects.filter(user_id=user_id, team_id=team_id).exists():
        result = {'result': 0, 'message': r'你不属于该团队, 请联系该团队的管理员申请加入!'}
        return JsonResponse(result)

    if not TeamToProject.objects.filter(team_id=team_id, project_id=project_id).exists():
        result = {'result': 0, 'message': r'你没有权限编辑该文档，请申请加入该文档对应的团队!'}
        return JsonResponse(result)

    if not ProjectToPage.objects.filter(project_id=project_id, page_id=page_id).exists():
        result = {'result': 0, 'message': r'该页面不属于该项目的管理范围之中，请确认后再重试!'}
        return JsonResponse(result)


# 展示项目中的所有页面
@login_checker
def create_page(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    team_id = request.POST.get('team_id', 0)
    project_id = request.POST.get('project_id', 0)
    page_name = request.POST.get('page_name', '')
    page_height = request.POST.get('page_height', 0.0)
    page_width = request.POST.get('page_width', 0.0)

    # 判断权限
    if not UserToTeam.objects.filter(user_id=user_id, team_id=team_id).exists():
        result = {'result': 0, 'message': r'你不属于该团队, 请联系该团队的管理员申请加入!'}
        return JsonResponse(result)

    if not TeamToProject.objects.filter(team_id=team_id, project_id=project_id).exists():
        result = {'result': 0, 'message': r'你没有权限编辑该文档，请申请加入该文档对应的团队!'}
        return JsonResponse(result)

    # 创建实体
    page = Page.objects.create(page_name=page_name, page_height=page_height, page_width=page_width)

    # 创建项目与页面直接的关系
    ProjectToPage.objects.create(project_id=project_id, page_id=page.id)

    # 项目的文件数量+1
    celery_create_page.delay(project_id)

    # 获取缓存
    page_key, page_dict = cache_get_by_id_simple('project', 'project', page.id)

    result = {'result': 1, 'message': r'创建页面成功!', 'page': page_dict}
    return JsonResponse(result)


# 获取项目的所有页面属性
@login_checker
def list_project_all(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    team_id = request.POST.get('team_id', 0)
    project_id = request.POST.get('project_id', 0)

    # 判断权限
    if not UserToTeam.objects.filter(user_id=user_id, team_id=team_id).exists():
        result = {'result': 0, 'message': r'你不属于该团队, 请联系该团队的管理员申请加入!'}
        return JsonResponse(result)

    if not TeamToProject.objects.filter(team_id=team_id, project_id=project_id).exists():
        result = {'result': 0, 'message': r'你没有权限编辑该文档，请申请加入该文档对应的团队!'}
        return JsonResponse(result)

    project_to_page_list = ProjectToPage.objects.filter(project_id=project_id)

    page_list = []

    for every_project_to_page in project_to_page_list:
        # 获取缓存
        page_key, page_dict = cache_get_by_id_simple('project', 'project', every_project_to_page.page_id)
        page_list.append(page_dict)

    result = {'result': 1, 'message': r'获取项目的所有页面属性成功!', 'page': page_list}
    return JsonResponse(result)


# 获取某个页面的详细元素
@login_checker
def list_page_detail(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    team_id = request.POST.get('team_id', 0)
    project_id = request.POST.get('project_id', 0)
    page_id = request.POST.get('page_id', 0)

    # 判断权限
    check_authority(user_id, team_id, project_id, page_id)

    # 获取缓存
    page_key, result = cache_get_by_id_detail('project', 'project', page_id)

    result['element_list'] = list(result['element_list'])
    result['result'] = 0
    result['message'] = '成功获取某个页面的详细元素'

    return JsonResponse(result)


# 请求编辑页面
@login_checker
def edit_request(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    team_id = request.POST.get('team_id', 0)
    project_id = request.POST.get('project_id', 0)
    page_id = request.POST.get('page_id', 0)

    # 判断权限
    check_authority(user_id, team_id, project_id, page_id)

    # TODO 仅仅支持单人编辑
    try:
        user_to_page = UserToPage.objects.get(page_id=page_id)
    except Exception:
        # 如果没有人在编辑
        # 创建编辑关系(加锁)
        UserToPage.objects.create(user_id=user_id, page_id=page_id)
        result = {'result': 1, 'message': r'没有人在编辑, 快去编辑叭!', 'free': 0, 'editor': None}
        return JsonResponse(result)

    # 如果有人在编辑
    # 查询是谁在编辑
    user_key, user_dict = cache_get_by_id('user', 'user', user_to_page.user_id)
    result = {'result': 0, 'message': r'有人在编辑, 稍等一下叭!', 'free': 1, 'editor': user_dict['username']}
    return JsonResponse(result)


# 请求保存页面  后端记得判断解锁
@login_checker
def edit_save(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    team_id = request.POST.get('team_id', 0)
    project_id = request.POST.get('project_id', 0)
    page_id = request.POST.get('page_id', 0)
    element_list = request.POST.get('element_list', '')
    num = request.POST.get('num', 0)

    # 判断权限
    check_authority(user_id, team_id, project_id, page_id)

    # 获取缓存
    page_key, page_dict = cache_get_by_id_detail('project', 'project', page_id)
    # 同步缓存
    element_list = str(element_list)
    page_dict['element_list'] = str(element_list)
    page_dict['num'] = num
    cache.set(page_key, page_dict)

    # 同步mysql(celery好像不支持3个参数以上)
    page = Page.objects.get(id=page_id)
    page.element_list = element_list
    page.num = num
    page.save()

    # 释放锁
    UserToPage.objects.get(page_id=page_id).delete()

    result = {'result': 1, 'message': r'保存成功'}
    return JsonResponse(result)
