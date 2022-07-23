from django.http import JsonResponse, HttpResponse
from django.core.cache import cache
from utils.Login_utils import super_admin_checker
from utils.Redis_utils import cache_get_by_id


# 查询缓存信息
@super_admin_checker
def query(request):
    app_label = request.POST.get('app_label', '')
    model_name = request.POST.get('model_name', '')
    model_id = request.POST.get('model_id', 0)
    return JsonResponse(cache_get_by_id(app_label, model_name, model_id)[1])


# 清除所有缓存
@super_admin_checker
def clean_cache(request):
    cache.clear()
    return HttpResponse("清除所有缓存成功")
