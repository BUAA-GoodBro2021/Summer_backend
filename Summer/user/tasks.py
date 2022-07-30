from Summer.celery import app
from user.models import User


@app.task
def celery_change_avatar(user_id, avatar_url):
    user = User.objects.get(id=user_id)
    user.avatar_url = avatar_url
    user.save()
    return user
