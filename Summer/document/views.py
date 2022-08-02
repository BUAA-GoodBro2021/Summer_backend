from django.shortcuts import render

from django.core.cache import cache

from document.tasks import *
from utils.Login_utils import *
from document.models import *


def example(request):
    document_id = request.GET.get('id')
    return render(request, 'Websocket-example.html', {"document_id": document_id})


@login_checker
def create_document(request):
    # 获取用户信息
    user_id = request.user_id

    # 获取表单信息
    document_title = request.POST.get('document_title', '')
    project_id = request.POST.get('project_id', '')

    if len(document_title) == 0:
        result = {'result': 0, 'message': r'文档标题不允许为空!'}
        return JsonResponse(result)

    # 创建实体
    document = Document.objects.create(creator_id=user_id, document_title=document_title)
    ProjectToDocument.objects.create(project_id=project_id, document_id=document.id)

    # 获取缓存信息
    user_key, user_dict = cache_get_by_id('user', 'user', user_id)
    document_key, document_dict = cache_get_by_id('document', 'document', document.id)

    # 创建user与document的关系
    UserToDocument.objects.create(user_id=user_id, document_id=document.id)

    result = {'result': 1, 'message': r'创建文档成功!', 'user': user_dict, 'document': document_dict}
    return JsonResponse(result)


# 查看文档编辑者
@login_checker
def list_document_user(request):
    # 获取用户信息
    user_id = request.user_id

    # 获取表单信息
    document_id = request.POST.get('document_id', '')

    # 文档相关联信息
    user_to_document_list = UserToDocument.objects.filter(document_id=document_id)

    # 用户所有信息列表
    user_list = []

    for every_user_to_document in user_to_document_list:
        # 获取缓存
        user_key, user_dict = cache_get_by_id('user', 'user', every_user_to_document.user_id)
        user_list.append(user_dict)

    # 获取缓存信息
    user_key, user_dict = cache_get_by_id('user', 'user', user_id)
    document_key, document_dict = cache_get_by_id('document', 'document', document_id)

    result = {'result': 1, 'message': r'查询成功!', 'user': user_dict, 'document': document_dict,
              'user_list': user_list}
    return JsonResponse(result)


# 重命名文档
@login_checker
def rename_project(request):
    # 获取用户信息
    user_id = request.user_id

    # 获取表单信息
    document_id = request.POST.get('document_id', '')
    document_title = request.POST.get('document_title', '')
    if len(document_title) == 0:
        result = {'result': 0, 'message': r'文档标题不允许为空!'}
        return JsonResponse(result)

    # 获取缓存信息
    document_key, document_dict = cache_get_by_id('document', 'document', document_id)

    if user_id != document_dict['creator_id']:
        result = {'result': 0, 'message': r'您不是此文档创建者'}
        return JsonResponse(result)

    # 修改信息，同步缓存
    document_dict['document_title'] = document_title
    cache.set(document_key, document_dict)

    # 同步mysql
    celery_rename_document.delay(document_id, document_title)
    result = {'result': 1, 'message': r'重命名文档成功!', 'document': document_dict}
    return JsonResponse(result)


# 删除文档
@login_checker
def delete_document(request):
    # 获取表单信息
    document_id = request.POST.get('document_id', '')

    document_key, document_dict = cache_get_by_id('document', 'document', document_id)

    # 移除缓存中内容
    cache.delete(document_key)

    # 同步mysql
    celery_delete_document.delay(document_id)

    result = {'result': 1, 'message': r'删除文档成功!'}
    return JsonResponse(result)


@login_checker
def save_document(request):
    # 获取表单信息
    document_id = request.POST.get('document_id', '')

    document_key, document_dict = cache_get_by_id('document', 'document', document_id)

    document_content = document_dict['document_content']
    celery_save_document.delay(document_id, document_content)
    result = {'result': 1, 'message': r'保存文档成功!', 'document_dict': document_dict}
    return JsonResponse(result)
