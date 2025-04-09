from django.urls import path
from .views import SendMessageView, InboxView

urlpatterns = [
    path('send/', SendMessageView.as_view(), name='send-message'),
    path('inbox/', InboxView.as_view(), name='inbox'),
]
