from Summer.celery import app
from user.models import User


@app.task
def celery_add_team_num(user_id):
    user = User.objects.get(id=user_id)
    user.add_team_num()
    return user.to_dic()
