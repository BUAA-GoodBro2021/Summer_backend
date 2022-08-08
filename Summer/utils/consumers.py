import datetime
import decimal
import json
import time

from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer
from asgiref.sync import async_to_sync
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Summer.settings')
django.setup()

from page.tasks import *
from utils.Redis_utils import *


class NEWEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        if isinstance(o, datetime.datetime):
            return str(o)
        super(NEWEncoder, self).default(o)


# 用户列表
USER_MAP = {}


class Consumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.page_id = None
        self.user = None

    def websocket_connect(self, message):
        # 获取url中的原型id，以此为键
        self.page_id = self.scope['url_route']['kwargs'].get('page_id')
        self.user = self.scope['url_route']['kwargs'].get('user')
        if self.page_id not in USER_MAP.keys():
            USER_MAP[self.page_id] = []
        USER_MAP[self.page_id].append(self.user)
        # 获取cache中的内容
        try:
            page_key, page_dict = cache_get_by_id('page', 'page', self.page_id)
        except Exception:
            return
        # 握手
        self.accept()
        # 同步添加组
        async_to_sync(self.channel_layer.group_add)(self.page_id, self.channel_name)
        print(self.groups)
        # 向客户端更新之前写好的内容
        page_dict['getWholePage'] = True
        self.send(self.json_dumps(page_dict))
        async_to_sync(self.channel_layer.group_send)(self.page_id, {
            'type': 'user.update', 'message': message
        })

    def websocket_receive(self, message):
        # 获取url中的原型id，以此为键
        self.page_id = self.scope['url_route']['kwargs'].get('page_id')
        self.user = self.scope['url_route']['kwargs'].get('user')
        # 如果是关闭请求，让移除所有用户
        if message.get('text') == 'DELETE!':
            async_to_sync(self.channel_layer.group_send)(self.page_id, {
                'type': 'remove.send', 'message': message
            })
            time.sleep(1)
            async_to_sync(self.channel_layer.group_send)(self.page_id, {
                'type': 'remove.user', 'message': message
            })
        else:
            async_to_sync(self.channel_layer.group_send)(self.page_id, {
                'type': 'content.update', 'message': message
            })
            page_new_dict = self.json_loads(message.get('text'))
            print(page_new_dict)
            # 优先更新缓存
            try:
                page_key, page_dict = cache_get_by_id('page', 'page', self.page_id)
            except Exception:
                return
            page_dict['page_name'] = page_new_dict['page_name']
            page_dict['page_height'] = page_new_dict['page_height']
            page_dict['page_width'] = page_new_dict['page_width']
            page_dict['element_list'] = page_new_dict['element_list']
            page_dict['num'] = page_new_dict['num']
            page_dict['is_preview'] = page_new_dict['is_preview']
            cache.set(page_key, page_dict)
            # 异步更新数据库
            page = Page.objects.get(id=self.page_id)
            page.page_name = page_dict['page_name']
            page.page_width = page_dict['page_width']
            page.page_height = page_dict['page_height']
            page.element_list = page_dict['element_list']
            page.num = page_dict['num']
            page.is_preview = page_dict['is_preview']
            page.save()

    def websocket_disconnect(self, message):
        # 获取url中的文档id，以此为键
        self.page_id = self.scope['url_route']['kwargs'].get('page_id')
        self.user = self.scope['url_route']['kwargs'].get('user')
        USER_MAP[self.page_id].remove(self.user)
        async_to_sync(self.channel_layer.group_send)(self.page_id, {
            'type': 'user.update', 'message': message
        })
        # 停止客户端
        async_to_sync(self.channel_layer.group_discard)(self.page_id, self.channel_name)
        raise StopConsumer()

    def content_update(self, event):
        # 获取发送信息，更新其他客户端
        text = event.get('message').get('text')
        self.send(text)

    def remove_send(self, event):
        # 发送移除广播
        self.send(self.json_dumps({"delete_flag": True}))

    def remove_user(self, event):
        # 移除组内全部成员
        self.close()

    def user_update(self, event):
        # 更新用户列表
        self.send(self.json_dumps(USER_MAP[self.page_id]))

    @staticmethod
    def json_dumps(obj):
        return json.dumps(obj, cls=NEWEncoder)

    @staticmethod
    def json_loads(obj):
        return json.loads(obj)
