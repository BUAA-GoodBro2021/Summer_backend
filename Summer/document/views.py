from django.core.cache import cache

from document.tasks import *
from utils.Login_utils import *
from document.models import *


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
    # 获取表单信息
    project_id = int(request.POST.get('project_id', 0))
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

    # if user_id != document_dict['creator_id']:
    #     result = {'result': 0, 'message': r'您不是此文档创建者'}
    #     return JsonResponse(result)

    # 修改信息，同步缓存
    document_dict['document_title'] = document_title
    cache.set(document_key, document_dict)

    # 同步mysql
    celery_rename_document.delay(document_id, document_title)

    # 获取项目的所有文档信息
    project_to_document_list = ProjectToDocument.objects.filter(project_id=project_id)

    document_list = []
    for every_project_to_document in project_to_document_list:
        document_key, document_dict = cache_get_by_id('document', 'document', every_project_to_document.document_id)
        document_list.append(document_dict)

    result = {'result': 1, 'message': r'重命名文档成功!', 'document_list': document_list}
    return JsonResponse(result)


# 删除文档
@login_checker
def delete_document(request):
    # 获取表单信息
    project_id = int(request.POST.get('project_id', 0))
    document_id = request.POST.get('document_id', '')

    project_to_document_list = ProjectToDocument.objects.filter(project_id=project_id)

    document_list = []
    for every_project_to_document in project_to_document_list:
        if int(every_project_to_document.document_id) != int(document_id):
            document_key, document_dict = cache_get_by_id('document', 'document', every_project_to_document.document_id)
            document_list.append(document_dict)

    user_to_document_list = UserToDocument.objects.filter(document_id=document_id)
    for every_user_to_document in user_to_document_list:
        every_user_to_document.delete()
    project_to_document_list = ProjectToDocument.objects.filter(document_id=document_id)
    for every_project_to_document in project_to_document_list:
        every_project_to_document.delete()

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


# 编辑文档
@login_checker
def edit_document(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    project_id = int(request.POST.get('project_id', 0))
    document_id = request.POST.get('document_id', '')

    document_key, document_dict = cache_get_by_id('document', 'document', document_id)

    user_key, user_dict = cache_get_by_id('user', 'user', user_id)
    # 签发令牌
    document_token = sign_token_forever({
        'project_id': int(project_id),
        'document_id': int(document_dict['document_id']),
        'document_title': document_dict['document_title'],
        'username': user_dict['username']
    })
    result = {'result': 1, 'message': '获取文档token成功!', 'document_token': document_token}
    return JsonResponse(result)


# 获取文档token
@login_checker
def create_token(request):
    # 获取用户信息
    user_id = request.user_id

    # 获取表单信息
    try:
        project_id = int(request.POST.get('project_id', 0))
        document_title = request.POST.get('document_title', '')
    except Exception:
        result = {'result': 0, 'message': '参数格式错误!'}
        return JsonResponse(result)

    user_key, user_dict = cache_get_by_id('user', 'user', user_id)

    try:
        document = Document.objects.get(document_title=document_title)
    except Exception:
        document = Document.objects.create(document_title=document_title, document_content='',
                                           creator_id=user_id, creator_name=user_dict['username'],
                                           project_id=project_id)
        ProjectToDocument.objects.create(project_id=project_id, document_id=document.id)

    # 签发令牌
    document_token = sign_token_forever({
        'project_id': int(project_id),
        'document_id': int(document.id),
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
    project_id = int(request.POST.get('project_id', 0))

    project_to_document_list = ProjectToDocument.objects.filter(project_id=project_id)

    document_list = []
    for every_project_to_document in project_to_document_list:
        document_key, document_dict = cache_get_by_id('document', 'document', every_project_to_document.document_id)
        document_list.append(document_dict)
    result = {'result': 1, 'message': '获取文档列表成功!', 'document_list': document_list}
    return JsonResponse(result)


# 展示树结构
def show_project_tree(project_id):
    project_to_document_list = ProjectToDocument.objects.filter(project_id=project_id)
    document_id_list = [x.document_id for x in project_to_document_list]
    # 核心是filter(parent=None) 查到最顶层的那个parent节点
    departs = Document.objects.filter(parent=None, id__in=document_id_list)
    data = recurse_display(departs)
    return data


# 展示树结构中所有id列表
def show_project_tree_id(project_id, document_id=0):
    # 核心是filter(parent=None) 查到最顶层的那个parent节点
    if document_id == 0:
        departs = Document.objects.filter(parent=None, project_id=project_id)
    else:
        departs = Document.objects.filter(parent_id=document_id, project_id=project_id)
    data = recurse_display_id(departs)
    return data


# 复制文件树
def copy_project_tree(creator_id, old_project_id, new_project_id, document_id=0):
    # 核心是filter(parent=None) 查到最顶层的那个parent节点
    if document_id == 0:
        departs = Document.objects.filter(parent=None, project_id=old_project_id)
    else:
        departs = Document.objects.filter(parent_id=document_id, project_id=old_project_id)
    data = recurse_display_copy(creator_id, new_project_id, document_id, departs)
    return data


# 列出树形结构列表
@login_checker
def list_tree_document(request):
    # 获取表单信息
    project_id = int(request.POST.get('project_id', 0))
    result = {'result': 1, 'message': '查询树形结构列表成功', 'tree_project_list': show_project_tree(project_id)}
    return JsonResponse(result)


# 创建文件夹
@login_checker
def create_tree_folder(request):
    # 获取用户信息
    user_id = request.user_id

    # 获取表单信息
    folder_title = request.POST.get('folder_title', '')
    project_id = int(request.POST.get('project_id', 0))
    parent_id = int(request.POST.get('parent_id', 0))

    # 获取父级文件夹
    try:
        parent_folder = Document.objects.get(id=parent_id)
    except Exception:
        parent_folder = None

    if len(folder_title) == 0:
        result = {'result': 0, 'message': r'文件夹标题不允许为空!'}
        return JsonResponse(result)

    if len(folder_title) > 100:
        result = {'result': 0, 'message': r'文件夹标题太长啦!'}
        return JsonResponse(result)
    # 获取缓存信息
    user_key, user_dict = cache_get_by_id('user', 'user', user_id)

    # 创建实体
    folder = Document.objects.create(creator_id=user_id, creator_name=user_dict['username'], project_id=project_id,
                                     document_title=folder_title, is_folder_or_file=1, parent=parent_folder)

    ProjectToDocument.objects.create(project_id=project_id, document_id=folder.id)

    # 获取缓存信息
    folder_key, folder_dict = cache_get_by_id('document', 'document', folder.id)

    result = {'result': 1, 'message': r'创建文件夹成功!', 'folder': folder_dict}
    return JsonResponse(result)


# 获取文档token
@login_checker
def create_tree_token(request):
    # 获取用户信息
    user_id = request.user_id

    # 获取表单信息
    try:
        project_id = int(request.POST.get('project_id', 0))
        parent_id = int(request.POST.get('parent_id', 0))
        document_title = request.POST.get('document_title', '')
    except Exception:
        result = {'result': 0, 'message': '参数格式错误!'}
        return JsonResponse(result)

    # 判断标题长度
    if len(document_title) == 0:
        result = {'result': 0, 'message': r'文档标题不允许为空!'}
        return JsonResponse(result)

    if len(document_title) > 100:
        result = {'result': 0, 'message': r'文档标题太长啦!'}
        return JsonResponse(result)

    # 获取父级文件夹
    try:
        parent_folder = Document.objects.get(id=parent_id)
    except Exception:
        parent_folder = None

    user_key, user_dict = cache_get_by_id('user', 'user', user_id)

    document = Document.objects.create(document_title=document_title, document_content='',
                                       creator_id=user_id, creator_name=user_dict['username'],
                                       project_id=project_id, parent=parent_folder)
    ProjectToDocument.objects.create(project_id=project_id, document_id=document.id)

    # 签发令牌
    document_token = sign_token_forever({
        'project_id': int(project_id),
        'document_id': int(document.id),
        'document_title': document.document_title,
        'username': user_dict['username']
    })
    result = {'result': 1, 'message': '获取文档token成功!', 'document_token': document_token}
    return JsonResponse(result)


# 删除文件夹或者文件
@login_checker
def delete_tree_document(request):
    # 获取表单信息
    project_id = int(request.POST.get('project_id', 0))
    document_id = int(request.POST.get('document_id', 0))

    # 获取到该目录的子集id列表(包含自身id)
    document_id_list = show_project_tree_id(project_id, document_id)
    document_id_list.append(document_id)

    # 获取文件夹或者文件的关联表(自身与子集)
    project_to_document_list = ProjectToDocument.objects.filter(document_id__in=document_id_list)

    # 删除实体
    Document.objects.filter(id__in=document_id_list).delete()

    # 删除关系(用户)
    UserToDocument.objects.filter(document_id__in=document_id_list).delete()

    # 删除关系(项目)
    project_to_document_list.delete()

    result = {'result': 1, 'message': r'删除文档成功!', 'document_list': show_project_tree(project_id)}
    return JsonResponse(result)


# 重命名文档或者文件夹
@login_checker
def rename_tree_document(request):
    # 获取表单信息
    project_id = int(request.POST.get('project_id', 0))
    document_id = request.POST.get('document_id', 0)
    document_title = request.POST.get('document_title', '')

    if len(document_title) == 0:
        result = {'result': 0, 'message': r'文档标题不允许为空!'}
        return JsonResponse(result)

    if len(document_title) > 100:
        result = {'result': 0, 'message': r'文档标题太长啦!'}
        return JsonResponse(result)
    # 获取缓存信息
    document_key, document_dict = cache_get_by_id('document', 'document', document_id)

    # 修改信息，同步缓存
    document_dict['document_title'] = document_title
    cache.set(document_key, document_dict)

    # 同步mysql
    celery_rename_document.delay(document_id, document_title)

    result = {'result': 1, 'message': r'重命名文档成功!', 'document_list': show_project_tree(project_id)}
    return JsonResponse(result)
