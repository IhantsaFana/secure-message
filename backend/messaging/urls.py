from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'conversations', views.ConversationViewSet, basename='conversation')
router.register(r'messages', views.MessageViewSet, basename='message')
router.register(r'key-exchanges', views.KeyExchangeViewSet, basename='keyexchange')

urlpatterns = [
    path('', include(router.urls)),
]

