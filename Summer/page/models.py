from django.db import models


class Page(models.Model):
    page_name = models.CharField('页面名称', max_length=100, default='')
    page_height = models.DecimalField('页面高度', max_digits=10, decimal_places=2, default=0.0)
    page_width = models.DecimalField('页面宽度', max_digits=10, decimal_places=2, default=0.0)
    element_list = models.TextField('页面样式', default='')
    num = models.IntegerField('页面特征值', default=0)
    is_preview = models.IntegerField('是否预览', default=0)

    # 实体属性
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

    def to_dic(self):
        return {
            'page_id': self.id,
            'page_name': self.page_name,
            'page_height': self.page_height,
            'page_width': self.page_width,

            'element_list': self.element_list,
            'num': int(self.num),
            'is_preview': int(self.is_preview),
            'created_time': self.created_time,
            'updated_time': self.updated_time,
        }


# 用户的素材库
class UserToPage(models.Model):
    user_id = models.IntegerField('用户id', default=0)
    page_id = models.IntegerField('页面id', default=0)


# 项目的模板
class UserModel(models.Model):
    user_id = models.IntegerField('用户id', default=0)
    model_name = models.CharField('页面名称', max_length=100, default='')
    is_public = models.IntegerField('是否是共有的', default=0)

    def to_dic(self):
        return {
            'model_id': self.id,
            'user_id': self.user_id,
            'model_name': self.model_name,
            'is_public': self.is_public,
        }


# 模板对页面
class ModelToPage(models.Model):
    model_id = models.IntegerField('模板id', default=0)
    page_id = models.IntegerField('页面id', default=0)
