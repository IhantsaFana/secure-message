from rest_framework import serializers
from .models import EncryptedMessage

class EncryptedMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EncryptedMessage
        fields = ['id', 'sender', 'recipient', 'encrypted_message', 'encrypted_aes_key', 'iv', 'created_at']
        read_only_fields = ['sender', 'created_at']
