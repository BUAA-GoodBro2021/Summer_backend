from diagram.models import *
from utils.Login_utils import *


# 创建绘图
@login_checker
def create_diagram(request):
    # 获取用户信息
    user_id = request.user_id

    # 获取表单信息
    diagram_name = request.POST.get('diagram_name', '')
    project_id = request.POST.get('project_id', '')

    if len(diagram_name) == 0:
        result = {'result': 0, 'message': r'绘图标题不允许为空!'}
        return JsonResponse(result)

    # 创建实体
    diagram = Diagram.objects.create(creator_id=user_id, diagram_name=diagram_name)
    ProjectToDiagram.objects.create(project_id=project_id, diagram_id=diagram.id)

    # 获取缓存信息
    user_key, user_dict = cache_get_by_id('user', 'user', user_id)
    diagram_key, diagram_dict = cache_get_by_id('diagram', 'diagram', diagram.id)
    result = {'result': 1, 'message': r'创建绘图成功!', 'user': user_dict, 'diagram': diagram_dict}
    return JsonResponse(result)


# 获取绘图token
@login_checker
def create_token(request):
    # 获取表单信息
    diagram_id = request.POST.get('diagram_id', '')

    diagram_key, diagram_dict = cache_get_by_id('diagram', 'diagram', diagram_id)
    project_to_diagram = ProjectToDiagram.objects.get(diagram_id=diagram_id)
    # 签发令牌
    diagram_token = sign_token({
        'project_id': project_to_diagram.project_id,
        'diagram_name': diagram_dict['diagram_name']
    })
    result = {'result': 1, 'diagram_token': diagram_token}
    return JsonResponse(result)


# 解析绘图token
def parse_token(request):
    # 获取表单信息
    diagram_token = request.POST.get('diagram_token', '')
    result = {'result': 1, 'payload': check_token(diagram_token)}
    return JsonResponse(result)
