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
