from django.db import models

from django.db import models


# 用户实体
class Team(models.Model):

    team_name = models.CharField('团队名称', max_length=30, default='')

    # 数量系列
    user_num = models.IntegerField('成员的数量', default=0)

    # 头像系列
    avatar_url = models.CharField('团队头像路径', max_length=128, default='')

    # 实体属性
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

    def to_dic(self):
        return {
            'team_id': self.id,
            'team_name': self.team_name,

            'user_num': self.user_num,

            "avatar_url": self.avatar_url,

            'created_time': self.created_time,
            'updated_time': self.updated_time,

        }

    # 团队人员的数量+1
    def add_user_num(self):
        self.user_num += 1
        self.save(update_fields=['user_num'])

    # 团队人员的数量+1
    def del_user_num(self):
        self.user_num -= 1
        self.save(update_fields=['user_num'])
