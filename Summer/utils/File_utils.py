import os

from Summer.settings import BASE_DIR
from utils.Bucket_utils import Bucket
from utils.Sending_utils import create_code


# 上传图片
def upload_image(image, bucket_name, model_id, is_audit=False, image_size=1024 * 1024):
    """
    上传图片(图片必须已经保存在media中)

    :param image:           图片的File对象
    :param bucket_name:     存储桶的名称
    :param model_id:        存储的标号
    :param is_audit:        是否需要进行图片检测
    :param image_size:      图片大小
    :return:                是否成功    1-成功    0-失败
    """
    # 获取用户上传的头像并检验是否符合要求
    if not image:
        result = {'result': 0, 'message': r"请上传图片！"}
        return result

    if image.size > image_size:
        result = {'result': 0, 'message': r"图片不能超过1M！"}
        return result

    # 获取文件尾缀并修改名称
    suffix = '.' + image.name.split(".")[-1]
    image.name = str(model_id) + suffix

    # 常见对象存储的对象
    bucket = Bucket()

    # 如果需要审核
    if is_audit:
        # 先生成一个随机 Key 保存在桶中进行审核
        key = create_code()

        upload_result = bucket.upload_file(bucket_name, key + suffix, image.name)

        # 上传审核
        if upload_result == -1:
            result = {'result': 0, 'message': r"上传失败！"}
            os.remove(os.path.join(BASE_DIR, "media/" + image.name))
            return result

        # 审核
        audit_dic = bucket.image_audit(bucket_name, key + suffix)

        # 审核不通过
        if audit_dic.get("result") != 0:
            result = {'result': 0, 'message': r"审核失败！", 'label': audit_dic.get("label")}
            # 删除审核对象
            bucket.delete_object(bucket_name, key + suffix)
            # 删除本地对象
            os.remove(os.path.join(BASE_DIR, "media/" + image.name))

            # TODO 站内信
            # title = "头像审核失败！"
            # content = "亲爱的" + user.username + ' 你好呀!\n头像好像带有一点' + audit_dic.get("label") + '呢！'
            # create_message(user_id, title, content)

            return result

        # 删除审核对象
        bucket.delete_object(bucket_name, key + suffix)

    # 要删除以前的图片
    try:
        bucket.delete_object(bucket_name, str(model_id) + ".png")
    except Exception:
        pass
    try:
        bucket.delete_object(bucket_name, str(model_id) + ".jpg")
    except Exception:
        pass
    try:
        bucket.delete_object(bucket_name, str(model_id) + ".jpeg")
    except Exception:
        pass

    # 上传是否成功
    upload_result = bucket.upload_file(bucket_name, str(model_id) + suffix, image.name)
    if upload_result == -1:
        os.remove(os.path.join(BASE_DIR, "media/" + image.name))
        result = {'result': 0, 'message': r"上传失败！"}
        return result

    # 上传是否可以获取路径
    image_url = bucket.query_object(bucket_name, str(model_id) + suffix)
    if not image_url:
        os.remove(os.path.join(BASE_DIR, "media/" + image.name))
        result = {'result': 0, 'message': r"上传失败！！"}
        return result

    # 删除本地文件
    os.remove(os.path.join(BASE_DIR, "media/" + image.name))

    # 上传成功并返回图片路径
    result = {'result': 1, 'message': r"上传成功！", 'image_url': image_url}
    return result


# 获取文件内容
def read_file(model_type):
    f = open(os.getcwd() + '/document_models/model' + str(model_type) + '.txt', encoding="utf-8mb4")
    txt = f.read()
    f.close()
    return txt
