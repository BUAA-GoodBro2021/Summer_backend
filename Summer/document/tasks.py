from Summer.celery import app
from document.models import *


@app.task
def celery_rename_document(document_id, document_title):
    document = Document.objects.get(id=document_id)
    document.document_title = document_title
    document.save()
    return document.to_dic()


@app.task
def celery_delete_document(document_id):
    user_to_document_list = UserToDocument.objects.filter(document_id=document_id)
    for every_user_to_document in user_to_document_list:
        every_user_to_document.delete()
    project_to_document_list = ProjectToDocument.objects.filter(document_id=document_id)
    for every_project_to_document in project_to_document_list:
        every_project_to_document.delete()
    document = Document.objects.get(id=document_id)
    document.delete()
    return document.to_dic()


@app.task
def celery_save_document(document_id, document_content):
    document = Document.objects.get(id=document_id)
    document.document_content = document_content
    document.save()
    return document.to_dic()
