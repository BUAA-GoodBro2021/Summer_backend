from Summer.settings import BASE_DIR
from page.models import *
from project.models import *
from team.models import TeamToProject
from user.models import UserToTeam, User
from utils.Bucket_utils import Bucket
from utils.Login_utils import *
from utils.Redis_utils import *
from page.tasks import *
from django.shortcuts import render


def example(request):
    page_id = request.GET.get('id')
    return render(request, 'Websocket-example.html', {"page_id": page_id})


# 权限判断
def check_authority(user_id, team_id, project_id, page_id):
    if not UserToTeam.objects.filter(user_id=user_id, team_id=team_id).exists():
        result = {'result': 0, 'message': r'你不属于该团队, 请联系该团队的管理员申请加入!'}
        return JsonResponse(result)

    if not TeamToProject.objects.filter(team_id=team_id, project_id=project_id).exists():
        result = {'result': 0, 'message': r'你没有权限编辑该文档，请申请加入该文档对应的团队!'}
        return JsonResponse(result)

    if not ProjectToPage.objects.filter(project_id=project_id, page_id=page_id).exists():
        result = {'result': 0, 'message': r'该页面不属于该项目的管理范围之中，请确认后再重试!'}
        return JsonResponse(result)


# 创建页面
@login_checker
def create_page(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    team_id = request.POST.get('team_id', 0)
    project_id = request.POST.get('project_id', 0)
    page_name = request.POST.get('page_name', '')
    page_height = request.POST.get('page_height', 0.0)
    page_width = request.POST.get('page_width', 0.0)

    # 判断权限
    if not UserToTeam.objects.filter(user_id=user_id, team_id=team_id).exists():
        result = {'result': 0, 'message': r'你不属于该团队, 请联系该团队的管理员申请加入!'}
        return JsonResponse(result)

    if not TeamToProject.objects.filter(team_id=team_id, project_id=project_id).exists():
        result = {'result': 0, 'message': r'你没有权限编辑该文档，请申请加入该文档对应的团队!'}
        return JsonResponse(result)

    if len(page_name) == 0:
        result = {'result': 0, 'message': r'原型设计页面名称不能为空!'}
        return JsonResponse(result)

    if len(page_name) > 100:
        result = {'result': 0, 'message': r'原型设计页面名称太长啦!'}
        return JsonResponse(result)

    # 创建实体
    page = Page.objects.create(page_name=page_name, page_height=page_height, page_width=page_width)

    # 创建项目与页面直接的关系
    ProjectToPage.objects.create(project_id=project_id, page_id=page.id)


    # 获取缓存
    page_key, page_dict = cache_get_by_id('page', 'page', page.id)

    # 获取得到该项目的所有页面信息
    project_to_page_list = ProjectToPage.objects.filter(project_id=project_id)

    page_list = []

    for every_project_to_page in project_to_page_list:
        # 获取缓存
        page_key, page_dict = cache_get_by_id('page', 'page', every_project_to_page.page_id)
        page_dict['element_list'] = page_dict['element_list'].split("|")
        page_list.append(page_dict)

    result = {'result': 1, 'message': r'创建页面成功!', 'page': page_dict, 'page_list': page_list}
    return JsonResponse(result)


# 获取项目的所有页面属性
@login_checker
def list_project_all(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    team_id = request.POST.get('team_id', 0)
    project_id = request.POST.get('project_id', 0)

    # 判断权限
    if not UserToTeam.objects.filter(user_id=user_id, team_id=team_id).exists():
        result = {'result': 0, 'message': r'你不属于该团队, 请联系该团队的管理员申请加入!'}
        return JsonResponse(result)

    if not TeamToProject.objects.filter(team_id=team_id, project_id=project_id).exists():
        result = {'result': 0, 'message': r'你没有权限编辑该文档，请申请加入该文档对应的团队!'}
        return JsonResponse(result)

    project_to_page_list = ProjectToPage.objects.filter(project_id=project_id)

    page_list = []

    for every_project_to_page in project_to_page_list:
        # 获取缓存
        page_key, page_dict = cache_get_by_id('page', 'page', every_project_to_page.page_id)
        page_dict['element_list'] = page_dict['element_list'].split("|")
        page_list.append(page_dict)

    result = {'result': 1, 'message': r'获取项目的所有页面属性成功!', 'page_list': page_list}
    return JsonResponse(result)


@login_checker
def list_preview_all(request):
    # 获取表单信息
    project_id = request.POST.get('project_id', 0)

    project_to_page_list = ProjectToPage.objects.filter(project_id=project_id)

    page_list = []

    for every_project_to_page in project_to_page_list:
        # 获取缓存
        page_key, page_dict = cache_get_by_id('page', 'page', every_project_to_page.page_id)
        if page_dict['is_preview'] == 1:
            page_dict['element_list'] = page_dict['element_list'].split("|")
            page_list.append(page_dict)

    result = {'result': 1, 'message': r'获取项目的所有页面属性成功!', 'page_list': page_list}
    return JsonResponse(result)


# 获取某个页面的详细元素
@login_checker
def list_page_detail(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    team_id = request.POST.get('team_id', 0)
    project_id = request.POST.get('project_id', 0)
    page_id = request.POST.get('page_id', 0)

    # 判断权限
    check_authority(user_id, team_id, project_id, page_id)

    # 获取缓存
    page_key, page_dict = cache_get_by_id('page', 'page', page_id)
    page_dict['element_list'] = page_dict['element_list'].split("|")
    result = {'result': 1, 'message': r'成功获取某个页面的详细元素', 'page': page_dict}

    return JsonResponse(result)


# 获取预览页面详细元素
@login_checker
def list_preview_detail(request):
    # 获取表单信息
    page_id = request.POST.get('page_id', 0)

    # 获取缓存
    page_key, page_dict = cache_get_by_id('page', 'page', page_id)
    page_dict['element_list'] = page_dict['element_list'].split("|")
    result = {'result': 1, 'message': r'成功获取某个页面的详细元素', 'page': page_dict}

    return JsonResponse(result)


# 请求保存页面  后端记得判断解锁
@login_checker
def edit_save(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    team_id = request.POST.get('team_id', 0)
    project_id = request.POST.get('project_id', 0)
    page_id = request.POST.get('page_id', 0)
    page_name = request.POST.get('page_name', '')
    page_height = request.POST.get('page_height', 0.0)
    page_width = request.POST.get('page_width', 0.0)
    element_list = request.POST.get('element_list', '')
    num = int(request.POST.get('num', 0))

    # 判断权限
    check_authority(user_id, team_id, project_id, page_id)

    if len(page_name) == 0:
        result = {'result': 0, 'message': r'原型设计页面名称不能为空!'}
        return JsonResponse(result)

    if len(page_name) > 100:
        result = {'result': 0, 'message': r'原型设计页面名称太长啦!'}
        return JsonResponse(result)

    # 获取缓存
    page_key, page_dict = cache_get_by_id('page', 'page', page_id)
    # 同步缓存
    page_dict['page_name'] = page_name
    page_dict['page_height'] = page_height
    page_dict['page_width'] = page_width
    page_dict['element_list'] = element_list
    page_dict['num'] = num
    cache.set(page_key, page_dict)

    # 同步mysql(celery好像不支持3个参数以上)
    # celery_save_page.delay(page_id, page_name, page_height, page_width, element_list, num)
    page = Page.objects.get(id=page_id)
    page.page_name = page_name
    page.page_height = page_height
    page.page_width = page_width
    page.element_list = element_list
    page.num = num
    page.save()

    # 获取得到该项目的所有页面信息
    project_to_page_list = ProjectToPage.objects.filter(project_id=project_id)

    page_list = []

    for every_project_to_page in project_to_page_list:
        # 获取缓存
        page_key, page_dict = cache_get_by_id('page', 'page', every_project_to_page.page_id)
        page_dict['element_list'] = page_dict['element_list'].split("|")
        page_list.append(page_dict)

    result = {'result': 1, 'message': r'保存成功', 'page_list': page_list}
    return JsonResponse(result)


# 上传图片
@login_checker
def upload_img(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取用户上传的头像并保存
    image = request.FILES.get("file", None)
    # 获取文件尾缀并修改名称
    suffix = '.' + (image.name.split("."))[-1]
    image.name = str(int(time.time() * 1000000)) + suffix

    # 保存至media
    user = User.objects.get(id=user_id)
    user.avatar = image
    user.save()

    # 获取用户上传的头像并检验是否符合要求
    if not image:
        result = {'result': 0, 'message': r"请上传图片！"}
        return result

    if image.size > 1024 * 1024 * 5:
        result = {'result': 0, 'message': r"图片不能超过1M！"}
        return result

    # 常见对象存储的对象
    bucket = Bucket()

    # 上传是否成功
    upload_result = bucket.upload_file("summer-design", image.name, image.name)
    if upload_result == -1:
        os.remove(os.path.join(BASE_DIR, "media/" + image.name))
        result = {'result': 0, 'message': r"上传失败！"}
        return result

    # 上传是否可以获取路径
    image_url = bucket.query_object("summer-design", image.name)
    if not image_url:
        os.remove(os.path.join(BASE_DIR, "media/" + image.name))
        result = {'result': 0, 'message': r"上传失败!！"}
        return result

    # 删除本地文件
    os.remove(os.path.join(BASE_DIR, "media/" + image.name))

    # 上传成功并返回图片路径
    result = {'result': 1, 'message': r"上传成功！", 'image_url': image_url}
    return JsonResponse(result)


# 删除某个页面
@login_checker
def delete_page(request):
    # 获取用户信息
    user_id = request.user_id
    # 获取表单信息
    team_id = request.POST.get('team_id', 0)
    project_id = request.POST.get('project_id', 0)
    page_id = request.POST.get('page_id', 0)

    # 判断权限
    check_authority(user_id, team_id, project_id, page_id)

    # 删除项目与页面直接的关系
    ProjectToPage.objects.get(project_id=project_id, page_id=page_id).delete()
    celery_delete_page.delay(page_id)
    result = {'result': 1, 'message': r'删除页面成功!'}
    return JsonResponse(result)


# 获取当前页面内容
@login_checker
def get_current(request):
    # 获取表单信息
    page_id = request.POST.get('page_id', 0)

    page_key, page_dict = cache_get_by_id('page', 'page', page_id)
    result = {'result': 1, 'message': r'获取页面成功!', 'page': page_dict}
    return JsonResponse(result)


# 更改页面预览状态
@login_checker
def change_preview(request):
    # 获取表单信息
    page_id = request.POST.get('page_id', 0)
    is_preview = request.POST.get('is_preview', 0)

    try:
        project_to_page = ProjectToPage.objects.get(id=page_id)
    except Exception:
        result = {'result': 1, 'message': '没有此页面!'}
        return JsonResponse(result)

    project_to_page_list = ProjectToPage.objects.filter(project_id=project_to_page.project_id)
    page_id_list = []
    for every_project_to_page in project_to_page_list:
        page_id = every_project_to_page.page_id
        page_key, page_dict = cache_get_by_id('page', 'page', page_id)
        page_dict['is_preview'] = int(is_preview)
        cache.set(page_key, page_dict)
        page_id_list.append(page_id)
    celery_change_preview.delay(page_id_list, is_preview)

    result = {'result': 1, 'message': r'修改页面预览状态成功!'}
    return JsonResponse(result)
