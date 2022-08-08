from django.http import JsonResponse

from document.views import show_tree
from team.models import TeamToProject, Team
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
    # 项目的所有文件夹信息列表
    project_folder_id_list = []
    for every_team_to_project in team_to_project_list:
        # 修改信息，同步缓存
        project_key, project_dict = cache_get_by_id('project', 'project', every_team_to_project.project_id)
        # 只展示未删除的项目
        if project_dict['is_delete'] == 1:
            project_folder_id_list.append(project_dict['project_folder_id'])

    result = {'result': 1, 'message': r'查询成功!', 'document_list': show_tree(team_id=team_id)}
    return JsonResponse(result)
