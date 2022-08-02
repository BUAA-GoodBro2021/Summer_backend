from django.db import models


class Project(models.Model):
    project_name = models.CharField('项目名称', max_length=30, default='')
    project_description = models.CharField('项目简介', max_length=30, default='')
    # 数量系列
    file_num = models.IntegerField('文件的数量', default=0)

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

            'file_num': self.file_num,

            'is_delete': self.is_delete,

            'created_time': self.created_time,
            'updated_time': self.updated_time,

        }

    # 项目中文件的数量+1
    def add_file_num(self):
        self.file_num += 1
        self.save(update_fields=['file_num'])

    # 项目中文件的数量-1
    def del_file_num(self):
        self.file_num -= 1
        self.save(update_fields=['file_num'])
