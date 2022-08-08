from django.core.cache import cache

from document.tasks import *
from project.models import Project
from utils.File_utils import read_file
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
    document_id = request.POST.get('document_id', '')

    document_key, document_dict = cache_get_by_id('document', 'document', document_id)

    user_key, user_dict = cache_get_by_id('user', 'user', user_id)
    # 签发令牌
    document_token = sign_token_forever({
        'document_id': int(document_dict['document_id']),
        'document_title': document_dict['document_title'],
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


# 展示树结构
def show_tree(parent_id=0, team_id=0, exc=None):
    # 如果是根节点
    if parent_id == 0:
        document_queryset = Document.objects.filter(parent=None, team_id=team_id)
    # 非根节点
    else:
        document_queryset = Document.objects.filter(parent_id=parent_id)

    # 是否需要去除节点
    if exc:
        document_queryset.exclude(id__in=exc)

    document_id_list = [x.id for x in document_queryset]
    # 核心是filter(parent=None) 查到最顶层的那个parent节点
    departs = Document.objects.filter(id__in=document_id_list)
    data = recurse_display(departs, exc=exc)
    return data


# 展示树结构中所有id列表
def show_tree_id(parent_id=0, team_id=0):
    # 如果是根节点
    if parent_id == 0:
        document_queryset = Document.objects.filter(parent=None, team_id=team_id)
    else:
        document_queryset = Document.objects.filter(parent_id=parent_id)
    data = recurse_display_id(document_queryset)
    return data


# 复制项目文件树
def copy_tree(creator_id, parent_id=0, new_folder_id=0):
    departs = Document.objects.filter(parent_id=parent_id)
    recurse_display_copy(creator_id, departs, parent_id, new_folder_id)


# 列出项目的树形结构列表
@login_checker
def list_project_tree_document(request):
    # 获取表单信息
    project_id = int(request.POST.get('project_id', 0))
    project = Project.objects.get(id=project_id)
    folder_id = project.project_folder_id

    # 获取实体
    folder_key, folder_dict = cache_get_by_id('document', 'document', folder_id)
    children = show_tree(project.project_folder_id)
    if len(children) > 0:
        folder_dict.update({'children': children})
    else:
        folder_dict.update({'children': []})
    result = {'result': 1, 'message': '查询树形结构列表成功', 'tree_project_list': folder_dict}
    return JsonResponse(result)


# 创建文件夹
@login_checker
def create_tree_folder(request):
    # 获取用户信息
    user_id = request.user_id

    # 获取表单信息
    folder_title = request.POST.get('folder_title', '')
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
    folder = Document.objects.create(creator_id=user_id, creator_name=user_dict['username'],
                                     document_title=folder_title, document_type=1, parent=parent_folder)

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
        model_type = request.POST.get('model_type', '')
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

    if model_type == '':
        document_content = ''
    else:
        try:
            document_content = read_file(int(model_type))
        except Exception:
            document_content = ""

    document = Document.objects.create(document_title=document_title, document_content=document_content,
                                       creator_id=user_id, creator_name=user_dict['username'],
                                       parent=parent_folder)

    # 签发令牌
    document_token = sign_token_forever({
        'document_id': int(document.id),
        'document_title': document.document_title,
        'username': user_dict['username'],
        'document_content': document_content
    })

    # 获取缓存信息
    document_key, document_dict = cache_get_by_id('document', 'document', document.id)

    result = {'result': 1, 'message': '获取文档token成功!', 'document_token': document_token, 'document': document_dict}
    return JsonResponse(result)


# 删除文件夹或者文件
@login_checker
def delete_tree_document(request):
    # 获取表单信息
    document_id = int(request.POST.get('document_id', 0))

    # 获取到该目录的子集id列表(包含自身id)
    document_id_list = show_tree_id(parent_id=document_id)
    document_id_list.append(document_id)

    # 删除实体
    Document.objects.filter(id__in=document_id_list).delete()

    result = {'result': 1, 'message': r'删除文档成功!'}
    return JsonResponse(result)


# 重命名文档或者文件夹
@login_checker
def rename_tree_document(request):
    # 获取表单信息
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
    # celery_rename_document.delay(document_id, document_title)
    document = Document.objects.get(id=document_id)
    document.document_title = document_title
    document.save()

    result = {'result': 1, 'message': r'重命名文档成功!'}
    return JsonResponse(result)


# 移动文档或者文件夹
@login_checker
def move_tree_document(request):
    # 获取表单信息
    document_id = request.POST.get('document_id', 0)
    new_parent_id = request.POST.get('new_parent_id', 0)

    try:
        document = Document.objects.get(id=document_id)
    except Exception:
        result = {'result': 0, 'message': r'该文档不存在!'}
        return JsonResponse(result)
    document.parent_id = new_parent_id
    document.save()

    result = {'result': 1, 'message': r'移动成功!'}
    return JsonResponse(result)
