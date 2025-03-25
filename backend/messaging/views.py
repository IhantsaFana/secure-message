from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Conversation, Message, KeyExchange
from .serializers import UserSerializer, ConversationSerializer, MessageSerializer, KeyExchangeSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only return conversations that the current user is part of
        return Conversation.objects.filter(participants=self.request.user)
    
    def create(self, request, *args, **kwargs):
        # Extract participant IDs from request data
        participant_ids = request.data.get('participant_ids', [])
        
        # Ensure the current user is included
        if request.user.id not in participant_ids:
            participant_ids.append(request.user.id)
        
        # Create the conversation
        conversation = Conversation.objects.create()
        
        # Add participants
        for user_id in participant_ids:
            try:
                user = User.objects.get(id=user_id)
                conversation.participants.add(user)
            except User.DoesNotExist:
                pass
        
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        messages = conversation.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only return messages from conversations the user is part of
        return Message.objects.filter(conversation__participants=self.request.user)
    
    def create(self, request, *args, **kwargs):
        # Check if the user is part of the conversation
        conversation_id = request.data.get('conversation')
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            if request.user not in conversation.participants.all():
                return Response(
                    {"detail": "You are not a participant in this conversation."},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Conversation.DoesNotExist:
            return Response(
                {"detail": "Conversation not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return super().create(request, *args, **kwargs)

class KeyExchangeViewSet(viewsets.ModelViewSet):
    serializer_class = KeyExchangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Return key exchanges for conversations the user is part of
        return KeyExchange.objects.filter(
            Q(conversation__participants=self.request.user) & Q(is_active=True)
        )
    
    def create(self, request, *args, **kwargs):
        # Check if the user is part of the conversation
        conversation_id = request.data.get('conversation')
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            if request.user not in conversation.participants.all():
                return Response(
                    {"detail": "You are not a participant in this conversation."},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Conversation.DoesNotExist:
            return Response(
                {"detail": "Conversation not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Deactivate any existing key exchanges for this user and conversation
        KeyExchange.objects.filter(
            user=request.user,
            conversation_id=conversation_id
        ).update(is_active=False)
        
        return super().create(request, *args, **kwargs)

