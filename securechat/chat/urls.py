from django.urls import path
from .views import SendEncryptedMessageView, ReceivedMessagesView

urlpatterns = [
    path('send/', SendEncryptedMessageView.as_view(), name='send_encrypted_message'),
    path('inbox/', ReceivedMessagesView.as_view(), name='received_encrypted_messages'),
]
