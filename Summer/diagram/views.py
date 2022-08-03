from utils.Login_utils import *

from diagram.tasks import *

from django.core.cache import cache


# 创建绘图
def create_diagram(request):
    # 获取表单信息
    diagram_name = request.POST.get('diagram_name', '')
    project_id = request.POST.get('project_id', '')

    diagram = Diagram.objects.filter(diagram_name=diagram_name)
    if len(diagram) != 0:
        result = {'result': 0, 'message': r'绘图名称重复!'}
        return JsonResponse(result)

    if len(diagram_name) == 0:
        result = {'result': 0, 'message': r'绘图标题不允许为空!'}
        return JsonResponse(result)

    # 创建实体
    diagram = Diagram.objects.create(diagram_name=diagram_name)
    ProjectToDiagram.objects.create(project_id=project_id, diagram_id=diagram.id)

    # 获取缓存信息
    diagram_key, diagram_dict = cache_get_by_id('diagram', 'diagram', diagram.id)
    result = {'result': 1, 'message': r'创建绘图成功!', 'diagram': diagram_dict}
    return JsonResponse(result)


# 获取绘图token
@login_checker
def create_token(request):
    # 获取表单信息
    project_id = request.POST.get('project_id', '')

    diagram = Diagram.objects.create(diagram_name=str(project_id) + '-' + '未命名')

    ProjectToDiagram.objects.create(project_id=project_id, diagram_id=diagram.id)
    # 签发令牌
    diagram_token = sign_token({
        'project_id': project_id,
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


# 重命名绘图
def rename_diagram(request):
    # 获取表单信息
    diagram_old_name = request.POST.get('diagram_old_name', '')
    diagram_new_name = request.POST.get('diagram_new_name', '')

    try:
        diagram = Diagram.objects.get(diagram_name=diagram_old_name)
    except Exception:
        result = {'result': 0, 'message': r'不存在此绘图!', 'diagram_name': diagram_old_name}
        return JsonResponse(result)

    diagram_key, diagram_dict = cache_get_by_id('diagram', 'diagram', diagram.id)

    # 修改信息，同步缓存
    diagram_dict['diagram_name'] = diagram_new_name
    cache.set(diagram_key, diagram_dict)

    # 同步mysql
    celery_rename_diagram.delay(diagram.id, diagram_new_name)
    result = {'result': 1, 'message': r'重命名绘图成功!', 'diagram': diagram_dict}
    return JsonResponse(result)


# 删除绘图
def delete_diagram(request):
    # 获取表单信息
    diagram_name = request.POST.get('diagram_name', '')

    try:
        diagram = Diagram.objects.get(diagram_name=diagram_name)
    except Exception:
        result = {'result': 0, 'message': r'不存在此绘图!', 'diagram_name': diagram_name}
        return JsonResponse(result)

    diagram_key, diagram_dict = cache_get_by_id('diagram', 'diagram', diagram.id)

    cache.delete(diagram_key)

    # 同步mysql
    celery_delete_diagram.delay(diagram.id)

    result = {'result': 1, 'message': r'删除绘图成功!'}
    return JsonResponse(result)
