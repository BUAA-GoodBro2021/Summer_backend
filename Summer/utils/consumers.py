import datetime
import decimal
import json

from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer
from asgiref.sync import async_to_sync

from page.tasks import *
from utils.Redis_utils import *


class NEWEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        if isinstance(o, datetime.datetime):
            return str(o)
        super(NEWEncoder, self).default(o)


class Consumer(WebsocketConsumer):
    def websocket_connect(self, message):
        # 获取url中的原型id，以此为键
        page_id = self.scope['url_route']['kwargs'].get('page_id')
        # 获取cache中的内容
        try:
            page_key, page_dict = cache_get_by_id('page', 'page', page_id)
        except Exception:
            return
        # 握手
        self.accept()
        # 同步添加组
        async_to_sync(self.channel_layer.group_add)(page_id, self.channel_name)
        # 向客户端更新之前写好的内容
        self.send(self.json_dumps(page_dict))

    def websocket_receive(self, message):
        # 获取url中的原型id，以此为键
        page_id = self.scope['url_route']['kwargs'].get('page_id')
        async_to_sync(self.channel_layer.group_send)(page_id, {
            'type': 'content.update', 'message': message
        })
        page_new_dict = self.json_loads(message.get('text'))
        # 优先更新缓存
        try:
            page_key, page_dict = cache_get_by_id('page', 'page', page_id)
        except Exception:
            return
        page_dict['page_name'] = page_new_dict['page_name']
        page_dict['page_height'] = page_new_dict['page_height']
        page_dict['page_width'] = page_new_dict['page_width']
        page_dict['element_list'] = page_new_dict['element_list']
        page_dict['num'] = page_new_dict['num']

        cache.set(page_key, page_dict)
        # 异步更新数据库
        celery_save_page(
            page_id,
            page_dict['page_name'],
            page_dict['page_height'],
            page_dict['page_width'],
            page_dict['element_list'],
            page_dict['num']
        )

    def websocket_disconnect(self, message):
        # 获取url中的文档id，以此为键
        page_id = self.scope['url_route']['kwargs'].get('page_id')
        # 停止客户端
        async_to_sync(self.channel_layer.group_discard)(page_id, self.channel_name)
        raise StopConsumer()

    def content_update(self, event):
        # 获取发送信息，更新其他客户端
        text = event.get('message').get('text')
        self.send(text)

    @staticmethod
    def json_dumps(obj):
        return json.dumps(obj, cls=NEWEncoder)

    @staticmethod
    def json_loads(obj):
        return json.loads(obj)
