from Summer.celery import app
from user.models import User


@app.task
def celery_add_message_num(user_id):
    user = User.objects.get(id=user_id)
    user.add_message_num()
    return user.to_dic()


@app.task
def celery_activate_user(user_id, email, avatar_url):
    user = User.objects.get(id=user_id)
    user.is_active = True
    user.email = email
    user.avatar_url = avatar_url
    user.save()
    # 删除其他伪用户
    user_list = User.objects.filter(username=user.username, is_active=False)
    if user_list:
        user_list.delete()
    return user.to_dic()


@app.task
def celery_change_password(user_id, password):
    user = User.objects.get(id=user_id)
    user.password = password
    user.save()
    return user.to_dic()
