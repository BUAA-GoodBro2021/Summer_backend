from django.db import models


# 绘图实体
class Diagram(models.Model):
    diagram_name = models.CharField('绘图名称', max_length=100, default='')
    diagram_content = models.TextField('绘图内容', null=True)

    # 实体属性
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

    def to_dic(self):
        return {
            'diagram_id': self.id,

            'diagram_name': self.diagram_name,
            'diagram_content': self.diagram_content,

            'created_time': self.created_time,
            'updated_time': self.updated_time,
        }


# 项目与绘图关系表
class ProjectToDiagram(models.Model):
    project_id = models.IntegerField('项目id', default=0)
    diagram_id = models.IntegerField('绘图id', default=0)
