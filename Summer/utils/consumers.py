from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer


class Consumer(WebsocketConsumer):
    def websocket_connect(self, message):
        self.accept()

    def websocket_receive(self, message):
        pass

    def websocket_disconnect(self, message):
        raise StopConsumer()
