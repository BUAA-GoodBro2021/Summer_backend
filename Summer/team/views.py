import random

from django.core.cache import cache
from team.tasks import *
from properties import *
from team.models import Team
from user.models import *
from utils.Login_utils import *


# 创建团队
@login_checker
def add_team(request):
    # 获取用户信息
    user_id = request.user_id

    # 获取表单信息
    team_name = request.POST.get('team_name', '')

    if len(team_name) == 0:
        result = {'result': 0, 'message': r'团队名称不允许为空!'}
        return JsonResponse(result)

    # 获取团队随机头像
    avatar_url = default_avatar_url_match + str(random.choice(range(1, 31))) + '.svg'

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
