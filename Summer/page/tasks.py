from Summer.celery import app
from page.models import Page, UserModel


@app.task
def celery_save_page(page_id, page_dict):
    page = Page.objects.get(id=page_id)
    page.page_name = page_dict['page_name']
    page.page_width = page_dict['page_width']
    page.page_height = page_dict['page_height']
    page.element_list = page_dict['element_list']
    page.num = page_dict['num']
    page.is_preview = page_dict['is_preview']
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
        print(page_id)
    return page_id_list


@app.task
def celery_delete_page(page_id):
    page = Page.objects.get(id=page_id)
    page.delete()
    return page.to_dic()


@app.task
def celery_change_public(model_id, is_public):
    model = UserModel.objects.get(id=model_id)
    model.is_public = int(is_public)
    model.save()
    return model.to_dic()

