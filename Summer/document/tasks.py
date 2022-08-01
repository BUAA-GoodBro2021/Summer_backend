from Summer.celery import app
from document.models import Document


@app.task
def celery_delete_document(document_id):
    document = Document.objects.get(id=document_id)
    document.delete()
    return document.to_dic()
