from django.db import models


class Project(models.Model):
    create_id = models.IntegerField('项目创建者id', default=0)
    create_name = models.CharField('项目创建者姓名', max_length=1000, default='')
    project_name = models.CharField('项目名称', max_length=100, default='')
    project_description = models.CharField('项目简介', max_length=1000, default='')

    project_folder_id = models.IntegerField('项目文件夹id', default=0)
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
            'create_id': self.create_id,
            'create_name': self.create_name,
            'project_name': self.project_name,
            'project_description': self.project_description,
            'project_folder_id': self.project_folder_id,

            'avatar_url': self.avatar_url,

            'is_delete': self.is_delete,

            'created_time': self.created_time,
            'updated_time': self.updated_time,

        }


# 项目与页面的关联表
class ProjectToPage(models.Model):
    project_id = models.IntegerField('项目id', default=0)
    page_id = models.IntegerField('页面id', default=0)
