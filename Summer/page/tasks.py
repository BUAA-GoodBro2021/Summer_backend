from Summer.celery import app
from team.models import Team
from project.models import Project
from user.models import UserToProjectStar


@app.task
def celery_create_page(project_id):
    project = Project.objects.get(id=project_id)
    project.add_file_num()
    return project.to_dic()
