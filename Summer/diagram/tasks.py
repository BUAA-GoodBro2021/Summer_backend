from Summer.celery import app
from diagram.models import *


@app.task
def celery_rename_diagram(diagram_id, diagram_name):
    diagram = Diagram.objects.get(id=diagram_id)
    diagram.diagram_name = diagram_name
    diagram.save()
    return diagram.to_dic()


@app.task
def celery_delete_diagram(diagram_id):
    diagram = Diagram.objects.get(id=diagram_id)
    diagram.delete()
    return diagram.to_dic()


@app.task
def celery_update_diagram(diagram_id, diagram_content):
    diagram = Diagram.objects.get(id=diagram_id)
    diagram.diagram_content = diagram_content
    diagram.save()
    return diagram.to_dic()
