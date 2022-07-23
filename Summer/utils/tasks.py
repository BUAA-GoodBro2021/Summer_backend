from Summer.celery import app
from user.models import User


@app.task
def celery_add_message_num(user_id):
    user = User.objects.get(id=user_id)
    user.add_message_num()
    return user


@app.task
def celery_activate_user(user_id, email):
    user = User.objects.get(id=user_id)
    user.is_active = True
    user.email = email
    user.save()
    return user


@app.task
def celery_change_password(user_id, password):
    user = User.objects.get(id=user_id)
    user.password = password
    return user
