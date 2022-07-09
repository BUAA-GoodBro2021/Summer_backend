"""
邮件验证相关工具类
"""
import os
import platform
from random import Random

from django.core.mail import EmailMessage
from django.template import loader

from properties import *
from utils.Login_utils import *


# 生成随机字符串
def create_code(random_length=6):
    """
    :param random_length:   随机字符串长度
    :return:                随机字符串
    """
    code = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(random_length):
        code += chars[random.randint(0, length)]
    return code


# 发送真实邮件
def send_email(payload, email, mail_type):
    """
    :param payload:     个人信息字典
    :param email:       个人邮件
    :param mail_type:   邮件类型(register，find)
    :return:            1 - 成功    其余 - 失败
    """
    # 生成验证路由
    url = sign_token(payload)  # 加密生成字符串(其实就是登录令牌)
    if platform.system() == "Linux":
        url = production_base_url + "/api/utils/email/" + url
    else:
        url = local_base_url + "/api/utils/email/" + url

    # 定义邮件内容
    content = {'url': url}
    # 定义邮件的标题和内容
    email_title = email_body = ''

    # 根据不同类型发送不同的邮件样式
    if mail_type == 'register':
        email_title = r"欢迎注册Summer平台"
        email_body = loader.render_to_string('EmailContent-register.html', content)
    elif mail_type == 'find':
        email_title = r"Summer平台重设密码"
        email_body = loader.render_to_string('EmailContent-find.html', content)
    try:
        msg = EmailMessage(email_title, email_body, EMAIL_HOST_USER, [email])
        msg.content_subtype = 'html'
        send_status = msg.send()
        return send_status
    except Exception as e:
        return 0
