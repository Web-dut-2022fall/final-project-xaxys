from django.contrib.auth.models import User
from django.db.models import (Model, AutoField, TextField, DateTimeField, ForeignKey, CASCADE)

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class MessageModel(Model):
    id = AutoField(primary_key=True)
    user = ForeignKey(User, on_delete=CASCADE, verbose_name='user', related_name='from_user', db_index=True)
    recipient = ForeignKey(User, on_delete=CASCADE, verbose_name='recipient', related_name='to_user', db_index=True, null=True, blank=True)
    timestamp = DateTimeField('timestamp', auto_now_add=True, editable=False, db_index=True)
    body = TextField('body')

    def __str__(self):
        return str(self.id)

    def characters(self):
        """
        Toy function to count body characters.
        :return: body's char number
        """
        return len(self.body)

    def notify_ws_clients(self):
        """
        Inform client there is a new message.
        """
        notification = {
            'type': 'recieve_group_message',
            'message': '{}'.format(self.id)
        }

        channel_layer = get_channel_layer()

        user_id = "{}".format(self.user.id)
        recipient_id = "{}".format(self.recipient.id) if self.recipient else "0"

        if recipient_id != "0":
            async_to_sync(channel_layer.group_send)(user_id, notification)
        
        async_to_sync(channel_layer.group_send)(recipient_id, notification)

    def save(self, *args, **kwargs):
        """
        Trims white spaces, saves the message and notifies the recipient via WS
        if the message is new.
        """
        new = self.id
        self.body = self.body.strip()  # Trimming whitespaces from the body
        super(MessageModel, self).save(*args, **kwargs)
        if new is None:
            self.notify_ws_clients()

    # Meta
    class Meta:
        app_label = 'core'
        verbose_name = 'message'
        verbose_name_plural = 'messages'
        ordering = ('-timestamp',)
