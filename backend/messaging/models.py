from django.db import models
from django.contrib.auth.models import User

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation {self.id}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    # Store the encrypted message - we don't decrypt on the server
    encrypted_content = models.TextField()
    # Store the encryption mode used
    encryption_mode = models.CharField(max_length=10)
    # Store the IV (Initialization Vector) used for encryption
    iv = models.CharField(max_length=64, blank=True, null=True)
    # Store the HMAC for message authentication
    hmac = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.username} at {self.created_at}"

class KeyExchange(models.Model):
    """
    Model to store public keys for Diffie-Hellman key exchange
    In a real application, this would be more sophisticated
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='key_exchanges')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='key_exchanges')
    # Store the public key for Diff  on_delete=models.CASCADE, related_name='key_exchanges')
    # Store the public key for Diffie-Hellman key exchange
    public_key = models.TextField()
    # Timestamp for key rotation policies
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'conversation')

    def __str__(self):
        return f"Key exchange for {self.user.username} in conversation {self.conversation.id}"

