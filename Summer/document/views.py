from django.http import HttpResponse
from django.shortcuts import render

from django.core.cache import cache

from document.tasks import *
from utils.Login_utils import *
from document.models import *


def example(request):
    document_id = request.GET.get('id')
    return render(request, 'Websocket-example.html', {"document_id": document_id})


# 创建文档
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

    if len(document_title) > 100:
        result = {'result': 0, 'message': r'文档标题太长啦!'}
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
def rename_document(request):
    # 获取用户信息
    user_id = request.user_id

    # 获取表单信息
    document_id = request.POST.get('document_id', '')
    document_title = request.POST.get('document_title', '')
    if len(document_title) == 0:
        result = {'result': 0, 'message': r'文档标题不允许为空!'}
        return JsonResponse(result)

    if len(document_title) > 100:
        result = {'result': 0, 'message': r'文档标题太长啦!'}
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
    project_id = request.POST.get('project_id', '')
    document_id = request.POST.get('document_id', '')

    project_to_document_list = ProjectToDocument.objects.filter(project_id=project_id)

    document_list = []
    for every_project_to_document in project_to_document_list:
        if int(every_project_to_document.document_id) != int(document_id):
            document_key, document_dict = cache_get_by_id('document', 'document', every_project_to_document.document_id)
            document_list.append(document_dict)

    # 同步mysql
    celery_delete_document.delay(document_id)
    result = {'result': 1, 'message': r'删除文档成功!', 'document_list': document_list}
    return JsonResponse(result)


def save_document(request):
    # 获取表单信息
    document_id = request.POST.get('document_id', '')
    document_content = request.POST.get('document_content', '')

    document_key, document_dict = cache_get_by_id('document', 'document', document_id)

    document_dict['document_content'] = document_content

    cache.set(document_key, document_dict)
    celery_save_document.delay(document_id, document_content)
    result = {'result': 1, 'message': r'保存文档成功!', 'document_dict': document_dict}
    return JsonResponse(result)


# 获取文档token
@login_checker
def create_token(request):
    # 获取用户信息
    user_id = request.user_id

    # 获取表单信息
    try:
        project_id = int(request.POST.get('project_id', ''))
        document_title = request.POST.get('document_title', '')
    except:
        result = {'result': 0, 'message': '参数格式错误!'}
        return JsonResponse(result)

    try:
        document = Document.objects.get(document_title=str(project_id) + '-' + document_title)
    except Exception:
        document = Document.objects.create(document_title=str(project_id) + '-' + document_title, document_content='',
                                           creator_id=user_id)
        ProjectToDocument.objects.create(project_id=project_id, document_id=document.id)

    user_key, user_dict = cache_get_by_id('user', 'user', user_id)
    # 签发令牌
    document_token = sign_token({
        'project_id': project_id,
        'document_id': document.id,
        'document_title': document.document_title,
        'username': user_dict['username']
    })
    result = {'result': 1, 'message': '获取文档token成功!', 'document_token': document_token}
    return JsonResponse(result)


# 解析文档token
def parse_token(request):
    # 获取表单信息
    document_token = request.POST.get('document_token', '')
    result = {'result': 1, 'message': '解析文档token成功!', 'payload': check_token(document_token)}
    return JsonResponse(result)


# 列出文档列表
@login_checker
def list_document(request):
    # 获取表单信息
    project_id = request.POST.get('project_id', '')

    project_to_document_list = ProjectToDocument.objects.filter(project_id=project_id)

    document_list = []
    for every_project_to_document in project_to_document_list:
        document_key, document_dict = cache_get_by_id('document', 'document', every_project_to_document.document_id)
        document_list.append(document_dict)
    result = {'result': 1, 'message': '获取文档列表成功!', 'document_list': document_list}
    return JsonResponse(result)
