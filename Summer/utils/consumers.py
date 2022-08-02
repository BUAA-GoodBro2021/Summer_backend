import threading

from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer
from asgiref.sync import async_to_sync

from utils.Redis_utils import *


class Consumer(WebsocketConsumer):
    def websocket_connect(self, message):
        # 获取url中的文档id，以此为键
        document_id = self.scope['url_route']['kwargs'].get('document_id')
        # 获取cache中内容
        try:
            document_key, document_dict = cache_get_by_id('document', 'document', document_id)
        except Exception:
            return
        # 握手
        self.accept()
        # 将客户端添加置对应的document_id的组中
        async_to_sync(self.channel_layer.group_add)(document_id, self.channel_name)
        # 向客户端更新之前写好的内容
        self.send(document_dict['document_content'])
        timer = threading.Timer(2, self.send(document_dict['document_content']))
        timer.start()
        print(timer)

    def websocket_receive(self, message):
        # 获取url中的文档id，以此为键
        document_id = self.scope['url_route']['kwargs'].get('document_id')
        # 服务端收到更新信息，更新客户端
        async_to_sync(self.channel_layer.group_send)(document_id, {
            'type': 'document.update', 'message': message
        })
        # 获取cache中内容
        try:
            document_key, document_dict = cache_get_by_id('document', 'document', document_id)
        except Exception:
            return
        # 更新cache
        document_dict['document_content'] = message.get('text')
        cache.set(document_key, document_dict)

    def websocket_disconnect(self, message):
        # 获取url中的文档id，以此为键
        document_id = self.scope['url_route']['kwargs'].get('document_id')
        # 停止客户端
        async_to_sync(self.channel_layer.group_discard)(document_id, self.channel_name)
        raise StopConsumer()

    def document_update(self, event):
        # 获取发送信息，更新其他客户端
        text = event.get('message').get('text')
        self.send(text)

