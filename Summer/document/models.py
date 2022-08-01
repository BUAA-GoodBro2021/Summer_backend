from django.db import models


# 文档实体
class Document(models.Model):
    document_title = models.CharField('文档标题', max_length=30, default='')
    document_content = models.TextField('文档内容', default='')

    # 实体属性
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

    def to_dic(self):
        return {
            'document_id': self.id,
            'document_title': self.document_title,
            'document_content': self.document_content,

            'created_time': self.created_time,
            'updated_time': self.updated_time,
        }
