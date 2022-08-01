from Summer.celery import app
from team.models import Team
from project.models import Project


@app.task
def celery_create_project(team_id, project_id):
    team = Team.objects.get(id=team_id)
    project = Project.objects.get(id=project_id)
    team.add_project_num()
    # TODO 项目的文件数量+1
    # project.add_file_num()
    return team.to_dic(), project.to_dic()


@app.task
def celery_rename_project(project_id, project_name):
    project = Project.objects.get(id=project_id)
    project.project_name = project_name
    project.save()
    return project.to_dic()


@app.task
def celery_remove_project_to_bin(project_id):
    project = Project.objects.get(id=project_id)
    project.is_delete = 1
    project.save()
    return project.to_dic()
