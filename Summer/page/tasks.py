from Summer.celery import app
from page.models import Page
from project.models import Project


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
def celery_change_preview(page_id_list, is_preview):
    for page_id in page_id_list:
        Page.objects.filter(id=page_id).update(is_preview=int(is_preview))
    return page_id_list


@app.task
def celery_delete_page(page_id):
    page = Page.objects.get(id=page_id)
    page.delete()
    return page.to_dic()

