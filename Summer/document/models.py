from django.db import models

# 文档实体
from utils.Redis_utils import cache_get_by_id


class Document(models.Model):
    creator_id = models.IntegerField('创建者id', default=0)
    project_id = models.IntegerField('项目id', default=0)
    creator_name = models.CharField('创建者名称', max_length=100, default='')
    document_title = models.CharField('文档标题', max_length=100, default='')
    document_content = models.TextField('文档内容', default='')

    is_folder_or_file = models.IntegerField('文件或者文件夹', default=0)  # 0-文件 1-文件

    parent = models.ForeignKey('Document',
                               on_delete=models.CASCADE,
                               null=True, blank=True,
                               # db_constraint=False,
                               related_name='children',
                               verbose_name="父级文件夹")

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

            'is_folder_or_file': self.is_folder_or_file,
            'parent_id': self.parent_id,

            'created_time': self.created_time,
            'updated_time': self.updated_time,
        }


def recurse_display(data):
    """递归展示"""
    display_list = []
    for item in data:
        # 本身字典信息
        item_key, item_dict = cache_get_by_id('document', 'document', item.id)
        # 孩子信息
        children = item.children.all()
        if len(children) > 0:
            item_dict.update({'children': recurse_display(children)})
        else:
            item_dict.update({'children': []})
        display_list.append(item_dict)
    return display_list


def recurse_display_copy(creator_id, project_id, parent_id, old_document_query_set):
    """递归复制树"""
    # 创建新项目与新文件之间的关系
    for every_old_document_query_set in old_document_query_set:
        # 获取旧实体
        old_document_key, old_document_dict = cache_get_by_id('document', 'document', every_old_document_query_set.id)

        # 创建副本实体
        new_document = Document.objects.create(creator_id=creator_id,
                                               creator_name=old_document_dict['creator_name'],
                                               document_title=old_document_dict['document_title'],
                                               document_content=old_document_dict['document_content'],
                                               is_folder_or_file=old_document_dict['is_folder_or_file'],
                                               project_id=project_id)
        if parent_id == 0:
            new_document.parent = None
        else:
            new_document.parent_id = parent_id
        new_document.save()

        # 创建关系
        ProjectToDocument.objects.create(project_id=project_id, document_id=new_document.id)

        # 孩子信息
        children = every_old_document_query_set.children.all()
        if len(children) > 0:
            recurse_display_copy(creator_id, project_id, new_document.id, children)


def recurse_display_id(data):
    """递归展示"""
    display_list = []
    for item in data:
        display_list.append(item.id)
        children = item.children.all()
        if len(children) > 0:
            display_list.extend(recurse_display_id(children))
    return display_list


# 用户与文档关联表
class UserToDocument(models.Model):
    user_id = models.IntegerField('用户id', default=0)
    document_id = models.IntegerField('文档id', default=0)


# 项目与文档关联表
class ProjectToDocument(models.Model):
    project_id = models.IntegerField('项目id', default=0)
    document_id = models.IntegerField('文档id', default=0)
