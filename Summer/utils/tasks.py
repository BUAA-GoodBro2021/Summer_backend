from Summer.celery import app
from user.models import User


@app.task
def celery_add_message_num(user_id):
    return User.objects.get(id=user_id).add_message_num()
