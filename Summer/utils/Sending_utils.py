"""
Django Sending Utils
"""
import os
import platform

from django.core.mail import EmailMessage
from django.template import loader

from key import *
from Login_utils import sign_token


# 发送真实邮件
def send_email(payload, email, title):
    # 验证路由
    url = sign_token(payload)  # 加密生成字符串
    if platform.system() == "Linux":
        url = os.path.join("https://summer.super2021.com/api/utils/", url)
    else:
        url = os.path.join("http://127.0.0.1/api/utils/", url)

    # 定义邮件内容
    data = {'url': url}
    email_title = email_body = ''

    if title == 'active':
        email_title = r"欢迎注册Summer平台"
        email_body = loader.render_to_string('EmailContent-register.html', data)
    elif title == 'find':
        email_title = r"Summer平台重设密码"
        email_body = loader.render_to_string('EmailContent-find.html', data)
    try:
        msg = EmailMessage(email_title, email_body, EMAIL_HOST_USER, [email])
        msg.content_subtype = 'html'
        send_status = msg.send()
        return send_status
    except Exception as e:
        return 0
