from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer
from asgiref.sync import async_to_sync


class Consumer(WebsocketConsumer):
    content = ''

    def websocket_connect(self, message):
        self.accept()
        document_id = self.scope['url_route']['kwargs'].get('document_id')
        async_to_sync(self.channel_layer.group_add)(document_id, self.channel_name)

    def websocket_receive(self, message):
        document_id = self.scope['url_route']['kwargs'].get('document_id')
        async_to_sync(self.channel_layer.group_send)(document_id, {'type': 'document.update', 'message': message})

    def websocket_disconnect(self, message):
        document_id = self.scope['url_route']['kwargs'].get('document_id')
        async_to_sync(self.channel_layer.group_discard)(document_id, self.channel_name)
        raise StopConsumer()

    def document_update(self, event):
        text = event.get('message').get('text')
        self.content = text
        self.send(text)
