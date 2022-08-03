from page.models import Page
from project.models import *
from team.models import TeamToProject
from user.models import UserToTeam
from utils.Login_utils import *
from utils.Redis_utils import *
from page.tasks import *


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
