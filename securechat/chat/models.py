from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class EncryptedMessage(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    encrypted_message = models.TextField()
    encrypted_aes_key = models.TextField()
    iv = models.CharField(max_length=32)  # En base64
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message from {self.sender} to {self.recipient} at {self.created_at}'
