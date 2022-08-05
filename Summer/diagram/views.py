from utils.Login_utils import *

from diagram.tasks import *

from django.core.cache import cache


# 获取绘图token
@login_checker
def create_token(request):
    # 获取表单信息
    try:
        project_id = request.POST.get('project_id', '')
        diagram_name = request.POST.get('diagram_name', '')
    except Exception:
        result = {'result': 0, 'message': '参数格式错误!'}
        return JsonResponse(result)

    diagram_list = Diagram.objects.filter(diagram_name=diagram_name)
    diagram_id_list = [x.id for x in diagram_list]
    project_to_diagram_list = ProjectToDiagram.objects.filter(project_id=project_id, diagram_id__in=diagram_id_list)
    if len(project_to_diagram_list) == 0:
        diagram = Diagram.objects.create(diagram_name=diagram_name, diagram_content=None)
        ProjectToDiagram.objects.create(project_id=project_id, diagram_id=diagram.id)
    else:
        diagram = Diagram.objects.get(id=project_to_diagram_list[0].diagram_id)

    # 签发令牌
    diagram_token = sign_token({
        'project_id': int(project_id),
        'diagram_id': diagram.id,
        'diagram_name': diagram.diagram_name
    })
    result = {'result': 1, 'message': '获取绘图token成功!', 'diagram_token': diagram_token}
    return JsonResponse(result)


# 解析绘图token
def parse_token(request):
    # 获取表单信息
    diagram_token = request.POST.get('diagram_token', '')
    result = {'result': 1, 'message': '解析绘图token成功!', 'payload': check_token(diagram_token)}
    return JsonResponse(result)


@login_checker
# 删除绘图
def delete_diagram(request):
    # 获取表单信息
    diagram_id = request.POST.get('diagram_id', '')

    diagram_key, diagram_dict = cache_get_by_id('diagram', 'diagram', diagram_id)

    cache.delete(diagram_key)

    # 同步mysql
    celery_delete_diagram(diagram_id)

    result = {'result': 1, 'message': r'删除绘图成功!'}
    return JsonResponse(result)


@login_checker
# 重命名绘图
def rename_diagram(request):
    # 获取表单信息
    diagram_id = request.POST.get('diagram_id', '')
    diagram_name = request.POST.get('diagram_name', '')

    if len(diagram_name) == 0:
        result = {'result': 0, 'message': r'绘图标题为空!'}
        return JsonResponse(result)

    if len(diagram_name) > 100:
        result = {'result': 0, 'message': r'绘图标题太长啦!'}
        return JsonResponse(result)

    diagram_key, diagram_dict = cache_get_by_id('diagram', 'diagram', diagram_id)

    # 修改信息，同步缓存
    diagram_dict['diagram_name'] = diagram_name
    cache.set(diagram_key, diagram_dict)

    # 同步mysql
    celery_rename_diagram(diagram_id, diagram_name)
    result = {'result': 1, 'message': r'重命名绘图成功!', 'diagram': diagram_dict}
    return JsonResponse(result)


# 列出绘图列表
@login_checker
def list_diagram(request):
    # 获取表单信息
    project_id = request.POST.get('project_id', '')

    project_to_diagram_list = ProjectToDiagram.objects.filter(project_id=project_id)

    diagram_list = []
    for every_project_to_diagram in project_to_diagram_list:
        diagram_key, diagram_dict = cache_get_by_id('diagram', 'diagram', every_project_to_diagram.diagram_id)
        diagram_list.append(diagram_dict)
    result = {'result': 1, 'message': '获取绘图列表成功!', 'diagram_list': diagram_list}
    return JsonResponse(result)


def update_diagram(request):
    # 获取表单信息
    diagram_id = request.POST.get('diagram_id', '')
    diagram_content = request.POST.get('diagram_content', '')

    diagram_key, diagram_dict = cache_get_by_id('diagram', 'diagram', diagram_id)

    diagram_dict['diagram_content'] = diagram_content
    cache.set(diagram_key, diagram_dict)

    celery_update_diagram.delay(diagram_id, diagram_content)
    result = {'result': 1, 'message': '绘图内容更新成功!', 'diagram_dict': diagram_dict}
    return JsonResponse(result)


def get_content(request):
    # 获取表单信息
    diagram_id = request.POST.get('diagram_id', '')

    diagram_key, diagram_dict = cache_get_by_id('diagram', 'diagram', diagram_id)

    result = {'result': 1, 'message': '绘图内容获取成功!', 'diagram_content': diagram_dict['diagram_content']}
    return JsonResponse(result)
