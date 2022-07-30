from django.db import models


# 用户实体
class User(models.Model):
    # 注册系列
    username = models.CharField('用户名', max_length=30)
    password = models.CharField('密码', max_length=32)
    email = models.EmailField()

    # 数量系列
    message_num = models.IntegerField('站内信的数量', default=0)

    # 头像系列
    avatar_url = models.CharField('用户头像路径', max_length=128, default='')
    avatar = models.FileField('用户头像', upload_to='', default='')

    # 权限判断
    is_active = models.BooleanField('是否有效', default=False)
    is_super_admin = models.BooleanField('是否为超级管理员', default=False)

    # 实体属性
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

    def to_dic(self):
        return {
            'user_id': self.id,
            'username': self.username,
            'email': self.email,

            'message_num': self.message_num,

            "avatar_url": self.avatar_url,

            'is_active': self.is_active,
            'is_super_admin': self.is_super_admin,

            'created_time': self.created_time,
            'updated_time': self.updated_time,

        }

    # 站内信+1
    def add_message_num(self):
        self.message_num += 1
        self.save(update_fields=['message_num'])
