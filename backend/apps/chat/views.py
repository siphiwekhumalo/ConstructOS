"""
REST API views for chat functionality.
"""
from datetime import datetime, timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from .models import ChatRoom, RoomMembership, Message, MessageReaction
from .serializers import (
    ChatRoomSerializer, ChatRoomDetailSerializer,
    MessageSerializer, RoomMembershipSerializer,
    CreateRoomSerializer, SendMessageSerializer
)


class ChatRoomViewSet(viewsets.ModelViewSet):
    """
    API endpoint for chat rooms.
    """
    queryset = ChatRoom.objects.filter(is_archived=False)
    serializer_class = ChatRoomSerializer
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChatRoomDetailSerializer
        return ChatRoomSerializer
    
    def get_queryset(self):
        queryset = ChatRoom.objects.filter(is_archived=False)
        
        room_type = self.request.query_params.get('type')
        if room_type:
            queryset = queryset.filter(room_type=room_type)
        
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset.order_by('-updated_at')
    
    def create(self, request, *args, **kwargs):
        serializer = CreateRoomSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = getattr(request, 'user_id', 'system')
        user_name = getattr(request, 'user_name', 'System')
        user_email = getattr(request, 'user_email', '')
        
        room = ChatRoom.objects.create(
            name=serializer.validated_data['name'],
            description=serializer.validated_data.get('description', ''),
            room_type=serializer.validated_data.get('room_type', 'public'),
            project_id=serializer.validated_data.get('project_id'),
            created_by=user_name,
        )
        
        RoomMembership.objects.create(
            room=room,
            user_id=user_id,
            user_email=user_email,
            user_name=user_name,
            role='owner',
        )
        
        for member_id in serializer.validated_data.get('member_ids', []):
            if member_id != user_id:
                RoomMembership.objects.create(
                    room=room,
                    user_id=member_id,
                    role='member',
                )
        
        output_serializer = ChatRoomSerializer(room, context={'request': request})
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a chat room."""
        room = self.get_object()
        
        user_id = getattr(request, 'user_id', 'anonymous')
        user_name = getattr(request, 'user_name', 'Anonymous')
        user_email = getattr(request, 'user_email', '')
        
        membership, created = RoomMembership.objects.get_or_create(
            room=room,
            user_id=user_id,
            defaults={
                'user_email': user_email,
                'user_name': user_name,
                'role': 'member',
            }
        )
        
        if not created:
            return Response({'message': 'Already a member'}, status=status.HTTP_200_OK)
        
        return Response(
            RoomMembershipSerializer(membership).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a chat room."""
        room = self.get_object()
        user_id = getattr(request, 'user_id', None)
        
        if not user_id:
            return Response(
                {'error': 'User not authenticated'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        membership = RoomMembership.objects.filter(
            room=room,
            user_id=user_id
        ).first()
        
        if not membership:
            return Response(
                {'error': 'Not a member of this room'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if membership.role == 'owner':
            other_admins = room.memberships.filter(role__in=['owner', 'admin']).exclude(user_id=user_id)
            if not other_admins.exists():
                return Response(
                    {'error': 'Cannot leave room as the only owner. Transfer ownership first.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        membership.delete()
        return Response({'message': 'Left room successfully'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages for a room with pagination."""
        room = self.get_object()
        
        before = request.query_params.get('before')
        limit = min(int(request.query_params.get('limit', 50)), 100)
        
        messages = room.messages.filter(is_deleted=False)
        
        if before:
            messages = messages.filter(created_at__lt=before)
        
        messages = messages.order_by('-created_at')[:limit]
        messages = list(reversed(messages))
        
        serializer = MessageSerializer(messages, many=True)
        return Response({
            'messages': serializer.data,
            'has_more': len(messages) == limit,
        })
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message to the room (REST fallback for WebSocket)."""
        room = self.get_object()
        
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = getattr(request, 'user_id', 'anonymous')
        user_name = getattr(request, 'user_name', 'Anonymous')
        user_email = getattr(request, 'user_email', '')
        
        parent_message = None
        parent_id = serializer.validated_data.get('parent_message_id')
        if parent_id:
            parent_message = Message.objects.filter(id=parent_id, room=room).first()
        
        message = Message.objects.create(
            room=room,
            sender_id=user_id,
            sender_email=user_email,
            sender_name=user_name,
            message_type=serializer.validated_data.get('message_type', 'text'),
            content=serializer.validated_data['content'],
            mentions=serializer.validated_data.get('mentions', []),
            parent_message=parent_message,
        )
        
        room.updated_at = datetime.now(timezone.utc)
        room.save(update_fields=['updated_at'])
        
        return Response(
            MessageSerializer(message).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get room members."""
        room = self.get_object()
        memberships = room.memberships.all()
        serializer = RoomMembershipSerializer(memberships, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a chat room."""
        room = self.get_object()
        room.is_archived = True
        room.save(update_fields=['is_archived'])
        return Response({'message': 'Room archived'}, status=status.HTTP_200_OK)


class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for messages.
    """
    queryset = Message.objects.filter(is_deleted=False)
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        queryset = Message.objects.filter(is_deleted=False)
        
        room_id = self.request.query_params.get('room_id')
        if room_id:
            queryset = queryset.filter(room_id=room_id)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def edit(self, request, pk=None):
        """Edit a message."""
        message = self.get_object()
        user_id = getattr(request, 'user_id', None)
        
        if message.sender_id != user_id:
            return Response(
                {'error': 'Cannot edit message from another user'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_content = request.data.get('content')
        if not new_content:
            return Response(
                {'error': 'Content is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        message.content = new_content
        message.is_edited = True
        message.edited_at = datetime.now(timezone.utc)
        message.save(update_fields=['content', 'is_edited', 'edited_at'])
        
        return Response(MessageSerializer(message).data)
    
    @action(detail=True, methods=['delete'])
    def soft_delete(self, request, pk=None):
        """Soft delete a message."""
        message = self.get_object()
        user_id = getattr(request, 'user_id', None)
        
        if message.sender_id != user_id:
            return Response(
                {'error': 'Cannot delete message from another user'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        message.is_deleted = True
        message.deleted_at = datetime.now(timezone.utc)
        message.save(update_fields=['is_deleted', 'deleted_at'])
        
        return Response({'message': 'Message deleted'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def replies(self, request, pk=None):
        """Get replies to a message (thread)."""
        message = self.get_object()
        replies = message.replies.filter(is_deleted=False).order_by('created_at')
        serializer = MessageSerializer(replies, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def react(self, request, pk=None):
        """Add a reaction to a message."""
        message = self.get_object()
        emoji = request.data.get('emoji')
        
        if not emoji:
            return Response(
                {'error': 'Emoji is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_id = getattr(request, 'user_id', 'anonymous')
        user_name = getattr(request, 'user_name', 'Anonymous')
        
        reaction, created = MessageReaction.objects.get_or_create(
            message=message,
            user_id=user_id,
            emoji=emoji,
            defaults={'user_name': user_name}
        )
        
        if not created:
            reaction.delete()
            return Response({'message': 'Reaction removed'}, status=status.HTTP_200_OK)
        
        return Response({'message': 'Reaction added'}, status=status.HTTP_201_CREATED)
