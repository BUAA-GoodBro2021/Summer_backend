from django.db import models


# 用户实体
class User(models.Model):
    username = models.CharField('用户名', max_length=30)
    password = models.CharField('密码', max_length=32)
    email = models.EmailField()

    is_active = models.BooleanField('是否有效', default=False)
    is_super_admin = models.BooleanField('是否为超级管理员', default=False)

    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)
