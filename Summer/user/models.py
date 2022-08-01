from django.db import models


# 用户实体
class User(models.Model):
    # 注册系列
    username = models.CharField('用户名', max_length=30, default='')
    real_name = models.CharField('真实性名', max_length=30, default='')
    password = models.CharField('密码', max_length=32)
    email = models.EmailField()

    # 数量系列
    team_num = models.IntegerField('团队的数量', default=0)

    # 头像系列
    avatar_url = models.CharField('用户头像路径', max_length=128, default='')
    avatar = models.FileField('用户头像', upload_to='', default='')

    # 权限判断
    is_active = models.BooleanField('是否有效', default=False)

    # 实体属性
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

    def to_dic(self):
        return {
            'user_id': self.id,
            'username': self.username,
            'real_name': self.real_name,
            'email': self.email,

            'team_num': self.team_num,

            "avatar_url": self.avatar_url,

            'is_active': self.is_active,

            'created_time': self.created_time,
            'updated_time': self.updated_time,

        }

    # 团队的数量+1
    def add_team_num(self):
        self.team_num += 1
        self.save(update_fields=['team_num'])

    # 团队的数量+1
    def del_team_num(self):
        self.team_num -= 1
        self.save(update_fields=['team_num'])


# 用户与团队的关联表
class UserToTeam(models.Model):
    user_id = models.IntegerField('用户id', default=0)
    team_id = models.IntegerField('团队id', default=0)
    is_super_admin = models.IntegerField('是否是团队管理员', default=0)  # 0-普通成员    1-管理员
