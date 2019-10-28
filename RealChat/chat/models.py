from django.contrib.auth import get_user_model
from django.db import models

user = get_user_model()


# Create your models here.
class Message(models.Model):
    author = models.ForeignKey(user, related_name='author_messages', on_delete=models.CASCADE)
    to = models.ForeignKey(user, related_name='to_message', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author.username

    def last_10_messages(author, to):
        a = Message.objects.order_by('-timestamp').filter(author_id=author, to_id=to)
        b = Message.objects.order_by('-timestamp').filter(author_id=to, to_id=author)
        return a.union(b).order_by('-id')[:20]
