from django.http import JsonResponse

from team.models import TeamToProject
from user.models import UserToTeam
from utils.Login_utils import login_checker
from utils.Redis_utils import cache_get_by_id


# 文档中心的查看
@login_checker
def list_team_document(request):
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

