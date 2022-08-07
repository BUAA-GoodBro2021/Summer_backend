from django.db import models


# 文档实体
class Document(models.Model):
    creator_id = models.IntegerField('创建者id', default=0)
    project_id = models.IntegerField('项目id', default=0)
    creator_name = models.CharField('创建者名称', max_length=100, default='')
    document_title = models.CharField('文档标题', max_length=100, default='')
    document_content = models.TextField('文档内容', default='')

    # 实体属性
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

    def to_dic(self):
        return {
            'document_id': self.id,
            'creator_id': self.creator_id,
            'creator_name': self.creator_name,
            'project_id': self.project_id,

            'document_title': self.document_title,
            'document_content': self.document_content,

            'created_time': self.created_time,
            'updated_time': self.updated_time,
        }


# 用户与文档关联表
class UserToDocument(models.Model):
    user_id = models.IntegerField('用户id', default=0)
    document_id = models.IntegerField('文档id', default=0)


# 项目与文档关联表
class ProjectToDocument(models.Model):
    project_id = models.IntegerField('项目id', default=0)
    document_id = models.IntegerField('文档id', default=0)
