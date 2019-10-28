from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from .models import Message
from django.contrib.auth import get_user_model

# from django.db.models.signals import post_save

User = get_user_model()


class ChatConsumer(WebsocketConsumer):

    def fetch_messages(self, data):
        author = User.objects.get(username=data['from']).pk
        to = User.objects.get(username=data['to']).pk
      #  print(author,to)
        messages = Message.last_10_messages(author,to)
        content = {
            'command': 'messages',
            'messages': sorted(self.messages_to_json(messages), key=lambda x: x['id'])
        }
       # print(content)

        self.send_message(content)

    def new_message(self, data):
        author = data['from']
        to = data['to']
        msg = data['message']
        author_user = User.objects.filter(username=author)[0]
        to_user = User.objects.filter(username=to)[0]
        message = Message.objects.create(
            author=author_user,
            to=to_user,
            content=msg)
        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }

        return self.send_chat_message(content)

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def forwarded(self, data):
        id = data['id']
        to = data['to']
        msg = Message.objects.get(id=id)
        msg.to = User.objects.filter(username=to)[0]
        content = {
            'command': 'forwarded',
            'from': data['from'],
            'message': self.message_to_json(msg)
        }

        return self.send_chat_message(content)


    def message_to_json(self, message):
        return {
            'id': message.id,
            'author': message.author.username,
            'to': message.to.username,
            'content': message.content,
            'timestamp': str(message.timestamp)
        }

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message,
        'forward': forwarded
    }

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self, message):
        # for i in message:
        #     print(message[i])
        self.send(text_data=json.dumps(message))

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))

    # def checkDatabase(self, **kwargs):
    #     messages = Message.last_1_message()
    #     message = messages[0]
    #     a = {
    #         'id': message.id,
    #         'author': message.author.username,
    #         'to': message.to.username,
    #         'content': message.content,
    #         'timestamp': str(message.timestamp)
    #     }
    #     self.send_chat_message(a)

#
# trigger = ChatConsumer(scope=Message)
#
# post_save.connect(trigger.checkDatabase, sender=Message)
