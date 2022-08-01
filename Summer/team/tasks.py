from Summer.celery import app
from team.models import Team
from user.models import User


@app.task
def celery_add_team_num(user_id):
    user = User.objects.get(id=user_id)
    user.add_team_num()
    return user.to_dic()


@app.task
def celery_join_team(user_id, team_id):
    user = User.objects.get(id=user_id)
    team = Team.objects.get(id=team_id)
    user.add_team_num()
    team.add_user_num()
    return user.to_dic(), team.to_dic()


@app.task
def celery_remove_user(user_id, team_id):
    user = User.objects.get(id=user_id)
    team = Team.objects.get(id=team_id)
    user.del_team_num()
    team.del_user_num()
    return user.to_dic(), team.to_dic()
