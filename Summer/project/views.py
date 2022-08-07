import random

from django.core.cache import cache

from diagram.models import *
from document.models import *
from document.views import copy_tree
from page.models import *
from project.tasks import *

from project.models import *
from properties import *
from team.models import TeamToProject
from user.models import *
from utils.Login_utils import *


# 新建一个项目
@login_checker
def create_project(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    team_id = request.POST.get('team_id', 0)
    project_name = request.POST.get('project_name', '')
    project_description = request.POST.get('project_description', '')

    # 判断权限
    if not UserToTeam.objects.filter(user_id=user_id, team_id=team_id).exists():
        result = {'result': 0, 'message': r'你不属于该团队, 请联系该团队的管理员申请加入!'}
        return JsonResponse(result)

    if len(project_name) == 0:
        result = {'result': 0, 'message': r'项目名称不能为空!'}
        return JsonResponse(result)

    if len(project_name) > 100:
        result = {'result': 0, 'message': r'项目名称太长啦!'}
        return JsonResponse(result)

    # 获取项目随机头像
    avatar_url = default_cover_2_url_match + str(random.choice(range(0, 31))) + '.svg'

    # 获取缓存信息
    user_key, user_dict = cache_get_by_id('user', 'user', user_id)

    # 创建一个项目对象
    project = Project.objects.create(project_name=project_name, project_description=project_description,
                                     avatar_url=avatar_url, create_id=user_id, create_name=user_dict['username'])
    # 创建团队与项目的关系
    TeamToProject.objects.create(team_id=team_id, project_id=project.id)

    team_key, team_dict = cache_get_by_id('team', 'team', team_id)
    project_key, project_dict = cache_get_by_id('project', 'project', project.id)

    # 修改信息，同步缓存
    team_dict['project_num'] += 1
    cache.set(team_key, team_dict)

    # 同步mysql
    celery_create_project.delay(team_id)

    result = {'result': 1, 'message': r'创建项目成功!', 'user': user_dict, 'project': project_dict}
    return JsonResponse(result)


# 重命名一个项目
@login_checker
def rename_project(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    team_id = request.POST.get('team_id', 0)
    project_id = request.POST.get('project_id', 0)
    project_name = request.POST.get('project_name', '')
    project_description = request.POST.get('project_description', '')

    if len(project_name) == 0:
        result = {'result': 0, 'message': r'项目名称不允许为空!'}
        return JsonResponse(result)

    if len(project_name) > 100:
        result = {'result': 0, 'message': r'项目名称太长啦!'}
        return JsonResponse(result)

    # 判断权限
    if not UserToTeam.objects.filter(user_id=user_id, team_id=team_id).exists():
        result = {'result': 0, 'message': r'你不属于该团队, 请联系该团队的管理员申请加入!'}
        return JsonResponse(result)

    if not TeamToProject.objects.filter(team_id=team_id, project_id=project_id).exists():
        result = {'result': 0, 'message': r'你没有权限编辑该项目，请申请加入该文档对应的团队!'}
        return JsonResponse(result)

    # 修改信息，同步缓存
    user_key, user_dict = cache_get_by_id('user', 'user', user_id)
    project_key, project_dict = cache_get_by_id('project', 'project', project_id)

    project_dict['project_name'] = project_name
    project_dict['project_description'] = project_description
    cache.set(project_key, project_dict)

    # 同步mysql(celery好像不支持三个参数)
    project = Project.objects.get(id=project_id)
    project.project_name = project_name
    project.project_description = project_name
    project.save()

    result = {'result': 1, 'message': r'修改项目信息成功!', 'user': user_dict, 'project': project_dict}
    return JsonResponse(result)


# 将项目放入回收站
@login_checker
def remove_project_to_bin(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    team_id = request.POST.get('team_id', '')
    project_id = int(request.POST.get('project_id', 0))

    # 判断权限
    if not UserToTeam.objects.filter(user_id=user_id, team_id=team_id).exists():
        result = {'result': 0, 'message': r'你不属于该团队, 请联系该团队的管理员申请加入!'}
        return JsonResponse(result)

    if not TeamToProject.objects.filter(team_id=team_id, project_id=project_id).exists():
        result = {'result': 0, 'message': r'你没有权限编辑该项目，请申请加入该文档对应的团队!'}
        return JsonResponse(result)

    # 修改信息，同步缓存
    project_key, project_dict = cache_get_by_id('project', 'project', project_id)

    # 是否已经在回收站里面
    if project_dict['is_delete'] == 1:
        result = {'result': 0, 'message': r'该项目已经添加至回收站，请勿重复添加!'}
        return JsonResponse(result)

    project_dict['is_delete'] = 1
    cache.set(project_key, project_dict)

    # 同步mysql
    celery_remove_project_to_bin.delay(user_id, project_id)

    user_key, user_dict = cache_get_by_id('user', 'user', user_id)
    result = {'result': 1, 'message': r'将项目放入回收站成功!', 'user': user_dict}
    return JsonResponse(result)


# 将回收站中的项目恢复
@login_checker
def recover_project_from_bin(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    team_id = request.POST.get('team_id', '')
    project_id = int(request.POST.get('project_id', 0))

    # 判断权限
    if not UserToTeam.objects.filter(user_id=user_id, team_id=team_id).exists():
        result = {'result': 0, 'message': r'你不属于该团队, 请联系该团队的管理员申请加入!'}
        return JsonResponse(result)

    if not TeamToProject.objects.filter(team_id=team_id, project_id=project_id).exists():
        result = {'result': 0, 'message': r'你没有权限编辑该项目，请申请加入该文档对应的团队!'}
        return JsonResponse(result)

    # 修改信息，同步缓存
    project_key, project_dict = cache_get_by_id('project', 'project', project_id)

    # 是否已经在回收站里面
    if project_dict['is_delete'] == 0:
        result = {'result': 0, 'message': r'该项目已经恢复，请勿重复恢复!'}
        return JsonResponse(result)

    project_dict['is_delete'] = 0
    cache.set(project_key, project_dict)

    # 同步mysql
    celery_recover_project_from_bin.delay(user_id, project_id)

    user_key, user_dict = cache_get_by_id('user', 'user', user_id)
    result = {'result': 1, 'message': r'将回收站恢复成功!', 'user': user_dict}
    return JsonResponse(result)


# 设置星标项目
@login_checker
def add_star_project(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    project_id = int(request.POST.get('project_id', 0))
    # 如果已经设置为星标项目了
    if UserToProjectStar.objects.filter(user_id=user_id, project_id=project_id).exists():
        result = {'result': 0, 'message': r'已经设置为星标，请勿重复设置!'}
        return JsonResponse(result)
    # 创建关联
    UserToProjectStar.objects.create(user_id=user_id, project_id=project_id)
    user_key, user_dict = cache_get_by_id('user', 'user', user_id)
    result = {'result': 1, 'message': r'设置星标成功!', 'user': user_dict}
    return JsonResponse(result)


# 取消设置星标项目
@login_checker
def del_star_project(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    project_id = int(request.POST.get('project_id', 0))
    # 如果已经设置为星标项目了
    if not UserToProjectStar.objects.filter(user_id=user_id, project_id=project_id).exists():
        result = {'result': 0, 'message': r'已经取消星标，请勿重复取消!'}
        return JsonResponse(result)
    # 删除关联
    UserToProjectStar.objects.filter(user_id=user_id, project_id=project_id).delete()
    user_key, user_dict = cache_get_by_id('user', 'user', user_id)
    result = {'result': 1, 'message': r'取消星标成功!', 'user': user_dict}
    return JsonResponse(result)


# 删除项目
@login_checker
def delete_project(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    team_id = request.POST.get('team_id', '')
    project_id = int(request.POST.get('project_id', 0))

    # 判断权限
    if not UserToTeam.objects.filter(user_id=user_id, team_id=team_id).exists():
        result = {'result': 0, 'message': r'你不属于该团队, 请联系该团队的管理员申请加入!'}
        return JsonResponse(result)

    if not TeamToProject.objects.filter(team_id=team_id, project_id=project_id).exists():
        result = {'result': 0, 'message': r'你没有权限编辑该项目，请申请加入该文档对应的团队!'}
        return JsonResponse(result)

    # 该函数实现了文件夹级别的删除
    # 列出三大文档信息
    project_to_page_list = ProjectToPage.objects.filter(project_id=project_id)
    project_to_document_list = ProjectToDocument.objects.filter(project_id=project_id)
    project_to_diagram_list = ProjectToDiagram.objects.filter(project_id=project_id)

    page_id_list = [x.page_id for x in project_to_page_list]
    document_id_list = [x.document_id for x in project_to_document_list]
    diagram_id_list = [x.diagram_id for x in project_to_diagram_list]

    # 如果有人正在编辑页面, 不允许删除
    if UserToPage.objects.filter(page_id__in=page_id_list).exists():
        result = {'result': 0, 'message': r'有人正在编辑界面，不允许删除!'}
        return JsonResponse(result)

    # 如果有人正在编辑文档, 不允许删除
    if UserToDocument.objects.filter(document_id__in=document_id_list).exists():
        result = {'result': 0, 'message': r'有人正在编辑文档，不允许删除!'}
        return JsonResponse(result)

    # 删除实体
    Page.objects.filter(id__in=page_id_list).delete()
    Document.objects.filter(id__in=document_id_list).delete()
    Diagram.objects.filter(id__in=diagram_id_list).delete()

    # 删除关系(用户)
    UserToPage.objects.filter(page_id__in=page_id_list).delete()
    UserToDocument.objects.filter(document_id__in=document_id_list).delete()
    # UserToProjectStar.objects.filter(project_id=project_id).delete()

    # 删除关系(项目)
    project_to_page_list.delete()
    project_to_document_list.delete()
    project_to_diagram_list.delete()

    # 删除实体
    Project.objects.get(id=project_id).delete()

    # 处理团队
    team_to_project = TeamToProject.objects.get(project_id=project_id)
    Team.objects.get(id=team_to_project.team_id).del_project_num()
    team_to_project.delete()

    result = {'result': 1, 'message': r'删除项目成功!'}
    return JsonResponse(result)


# 复制项目
@login_checker
def copy_project(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    team_id = request.POST.get('team_id', '')
    old_project_id = int(request.POST.get('old_project_id', 0))

    # 判断权限
    if not UserToTeam.objects.filter(user_id=user_id, team_id=team_id).exists():
        result = {'result': 0, 'message': r'你不属于该团队, 请联系该团队的管理员申请加入!'}
        return JsonResponse(result)

    if not TeamToProject.objects.filter(team_id=team_id, project_id=old_project_id).exists():
        result = {'result': 0, 'message': r'你没有权限编辑该项目，请申请加入该文档对应的团队!'}
        return JsonResponse(result)

    # 列出三大文档信息
    project_to_page_list = ProjectToPage.objects.filter(project_id=old_project_id)
    # project_to_document_list = ProjectToDocument.objects.filter(project_id=old_project_id)
    project_to_diagram_list = ProjectToDiagram.objects.filter(project_id=old_project_id)

    page_id_list = [x.page_id for x in project_to_page_list]
    # document_id_list = [x.document_id for x in project_to_document_list]
    diagram_id_list = [x.diagram_id for x in project_to_diagram_list]

    old_project_key, old_project_dict = cache_get_by_id('project', 'project', old_project_id)

    # 获取项目随机头像
    avatar_url = default_cover_2_url_match + str(random.choice(range(0, 31))) + '.svg'

    # 获取缓存信息
    user_key, user_dict = cache_get_by_id('user', 'user', user_id)

    # 创建一个项目对象
    new_project = Project.objects.create(project_name=old_project_dict['project_name'] + '-副本',
                                         project_description=old_project_dict['project_name'],
                                         avatar_url=avatar_url, create_id=user_id, create_name=user_dict['username'])
    # 创建团队与项目的关系
    TeamToProject.objects.create(team_id=team_id, project_id=new_project.id)

    # 团队项目输+1
    celery_create_project.delay(team_id)

    # 支持文件夹操作
    # 创建副本与三大文档的信息
    for every_page_id in page_id_list:
        # 获取旧实体
        old_page_key, old_page_dict = cache_get_by_id('page', 'page', every_page_id)
        # 创建副本实体
        new_page = Page.objects.create(page_name=old_page_dict['page_name'],
                                       page_height=old_page_dict['page_height'],
                                       page_width=old_page_dict['page_width'],
                                       element_list=old_page_dict['element_list'], num=old_page_dict['num'])
        # 创建关系
        ProjectToPage.objects.create(project_id=new_project.id, page_id=new_page.id)

    # for every_document_id in document_id_list:
    #     # 获取旧实体
    #     old_document_key, old_document_dict = cache_get_by_id('document', 'document', every_document_id)
    #     # 创建副本实体
    #     new_document = Document.objects.create(creator_id=old_document_dict['creator_id'],
    #                                            creator_name=old_document_dict['creator_name'],
    #                                            document_title=old_document_dict['document_title'],
    #                                            document_content=old_document_dict['document_content'],
    #                                            project_id=old_document_dict['project_id'])
    #     # 创建关系
    #     ProjectToDocument.objects.create(project_id=new_project.id, document_id=new_document.id)

    copy_tree(user_id, old_project_id, new_project.id, document_id=0)

    for every_diagram_id in diagram_id_list:
        # 获取旧实体
        old_diagram_key, old_diagram_dict = cache_get_by_id('diagram', 'diagram', every_diagram_id)
        # 创建副本实体
        new_diagram = Diagram.objects.create(diagram_name=old_diagram_dict['diagram_name'],
                                             diagram_content=old_diagram_dict['diagram_content'])

        # 创建关系
        ProjectToDiagram.objects.create(project_id=new_project.id, diagram_id=new_diagram.id)

    new_project_key, new_project_dict = cache_get_by_id('project', 'project', new_project.id)
    result = {'result': 1, 'message': r'复制项目成功!', 'new_project': new_project_dict}
    return JsonResponse(result)


# 复制文件中的项目信息
@login_checker
def copy_project_tree_document(request):
    # 获取用户信息
    user_id = request.user_id
    old_project_id = int(request.POST.get('old_project_id', 0))
    new_project = Project.objects.create(create_id=user_id)

    copy_tree(user_id, old_project_id, new_project.id, document_id=0)

    return JsonResponse({'result': 1, 'message': r'OK'})
