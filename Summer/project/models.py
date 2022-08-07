from django.db import models


class Project(models.Model):
    project_name = models.CharField('项目名称', max_length=100, default='')
    project_description = models.CharField('项目简介', max_length=1000, default='')

    # 头像系列
    avatar_url = models.CharField('项目头像路径', max_length=128, default='')

    # 判断是否删除
    is_delete = models.IntegerField('是否删除', default=0)  # 0-未删除   1-伪删除

    # 实体属性
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

    def to_dic(self):
        return {
            'project_id': self.id,
            'project_name': self.project_name,
            'project_description': self.project_description,

            'avatar_url': self.avatar_url,

            'is_delete': self.is_delete,

            'created_time': self.created_time,
            'updated_time': self.updated_time,

        }


# 项目与页面的关联表
class ProjectToPage(models.Model):
    project_id = models.IntegerField('项目id', default=0)
    page_id = models.IntegerField('页面id', default=0)
