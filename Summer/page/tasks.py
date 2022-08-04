from Summer.celery import app
from page.models import Page
from project.models import Project


@app.task
def celery_create_page(project_id):
    project = Project.objects.get(id=project_id)
    project.add_file_num()
    return project.to_dic()


@app.task
def celery_save_page(page_id, page_name, page_height, page_width, element_list, num):
    page = Page.objects.get(id=page_id)
    page.page_name = page_name
    page.page_height = page_height
    page.page_width = page_width
    page.element_list = element_list
    page.num = num
    page.save()
    return page.to_dic()


@app.task
def celery_rename_page(page_id, page_name):
    page = Page.objects.get(id=page_id)
    page.page_name = page_name
    page.save()
    return page.to_dic()


@app.task
def celery_delete_page(project_id, page_id):
    project = Project.objects.get(id=project_id)
    project.del_file_num()
    page = Page.objects.get(id=page_id)
    page.delete()
    return project.to_dic()