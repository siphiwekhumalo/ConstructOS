"""
REST API views for chat functionality.
"""
from datetime import datetime, timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q

from .models import ChatRoom, RoomMembership, Message, MessageReaction, DirectMessageThread, DirectMessage
from .serializers import (
    ChatRoomSerializer, ChatRoomDetailSerializer,
    MessageSerializer, RoomMembershipSerializer,
    CreateRoomSerializer, SendMessageSerializer,
    DirectMessageThreadSerializer, DirectMessageSerializer,
    CreateDMThreadSerializer, SendDMSerializer
)


def get_user_context(request):
    """
    Extract user context from the request.
    Works with Azure AD authenticated users or provides demo defaults.
    """
    user = getattr(request, 'user', None)
    
    if user and hasattr(user, 'azure_ad_object_id') and user.azure_ad_object_id:
        return {
            'user_id': str(user.azure_ad_object_id),
            'user_name': user.get_full_name() or user.username,
            'user_email': user.email,
        }
    
    if user and hasattr(user, 'id') and user.id:
        return {
            'user_id': str(user.id),
            'user_name': user.get_full_name() if hasattr(user, 'get_full_name') else str(user),
            'user_email': user.email if hasattr(user, 'email') else '',
        }
    
    return {
        'user_id': 'demo-user',
        'user_name': 'Demo User',
        'user_email': 'demo@constructos.co.za',
    }


class ChatRoomViewSet(viewsets.ModelViewSet):
    """
    API endpoint for chat rooms.
    """
    queryset = ChatRoom.objects.filter(is_archived=False)
    serializer_class = ChatRoomSerializer
    permission_classes = [AllowAny]
    
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
        
        ctx = get_user_context(request)
        user_id = ctx['user_id']
        user_name = ctx['user_name']
        user_email = ctx['user_email']
        
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
        
        ctx = get_user_context(request)
        user_id = ctx['user_id']
        user_name = ctx['user_name']
        user_email = ctx['user_email']
        
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
        ctx = get_user_context(request)
        user_id = ctx['user_id']
        
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
        
        ctx = get_user_context(request)
        user_id = ctx['user_id']
        user_name = ctx['user_name']
        user_email = ctx['user_email']
        
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
    permission_classes = [AllowAny]
    
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
        ctx = get_user_context(request)
        user_id = ctx['user_id']
        
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
        ctx = get_user_context(request)
        user_id = ctx['user_id']
        
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
        
        ctx = get_user_context(request)
        user_id = ctx['user_id']
        user_name = ctx['user_name']
        
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


class DirectMessageThreadViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Direct Message threads.
    Handles DM conversations between two users.
    """
    serializer_class = DirectMessageThreadSerializer
    permission_classes = [AllowAny]
    
    def dispatch(self, request, *args, **kwargs):
        """Ensure user is authenticated before processing any request."""
        ctx = get_user_context(request)
        if not ctx.get('user_id'):
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        """Get threads for the current user."""
        ctx = get_user_context(self.request)
        user_id = ctx['user_id']
        
        return DirectMessageThread.objects.filter(
            Q(user1_id=user_id) | Q(user2_id=user_id)
        ).order_by('-updated_at')
    
    def create(self, request, *args, **kwargs):
        """
        Create or retrieve a DM thread with another user.
        If a thread already exists, returns the existing one.
        """
        serializer = CreateDMThreadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        ctx = get_user_context(request)
        current_user_id = ctx['user_id']
        current_user_name = ctx['user_name']
        current_user_email = ctx['user_email']
        
        target_user_id = serializer.validated_data['target_user_id']
        target_user_name = serializer.validated_data.get('target_user_name', '')
        target_user_email = serializer.validated_data.get('target_user_email', '')
        
        if current_user_id == target_user_id:
            return Response(
                {'error': 'Cannot create a DM thread with yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        thread, created = DirectMessageThread.get_or_create_thread(
            user1_id=current_user_id,
            user1_name=current_user_name,
            user1_email=current_user_email,
            user2_id=target_user_id,
            user2_name=target_user_name,
            user2_email=target_user_email,
        )
        
        output_serializer = DirectMessageThreadSerializer(thread, context={'request': request})
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(output_serializer.data, status=status_code)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages for a DM thread with pagination."""
        thread = self.get_object()
        
        ctx = get_user_context(request)
        user_id = ctx['user_id']
        
        if str(thread.user1_id) != str(user_id) and str(thread.user2_id) != str(user_id):
            return Response(
                {'error': 'Not a participant in this thread'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        limit = int(request.query_params.get('limit', 50))
        before = request.query_params.get('before')
        
        messages = thread.messages.filter(is_deleted=False)
        
        if before:
            messages = messages.filter(created_at__lt=before)
        
        messages = messages.order_by('-created_at')[:limit]
        messages = list(reversed(messages))
        
        serializer = DirectMessageSerializer(messages, many=True)
        return Response({
            'messages': serializer.data,
            'thread_id': str(thread.id),
            'channel_name': thread.channel_name,
        })
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Send a message in a DM thread."""
        thread = self.get_object()
        
        ctx = get_user_context(request)
        user_id = ctx['user_id']
        user_name = ctx['user_name']
        user_email = ctx['user_email']
        
        if str(thread.user1_id) != str(user_id) and str(thread.user2_id) != str(user_id):
            return Response(
                {'error': 'Not a participant in this thread'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = SendDMSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        message = DirectMessage.objects.create(
            thread=thread,
            sender_id=user_id,
            sender_name=user_name,
            sender_email=user_email,
            content=serializer.validated_data['content'],
            message_type=serializer.validated_data.get('message_type', 'text'),
        )
        
        thread.latest_message = message
        thread.save(update_fields=['latest_message', 'updated_at'])
        
        output_serializer = DirectMessageSerializer(message)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark all messages in the thread as read."""
        thread = self.get_object()
        
        ctx = get_user_context(request)
        user_id = ctx['user_id']
        
        now = datetime.now(timezone.utc)
        
        if str(thread.user1_id) == str(user_id):
            thread.user1_last_read_at = now
            thread.save(update_fields=['user1_last_read_at'])
        elif str(thread.user2_id) == str(user_id):
            thread.user2_last_read_at = now
            thread.save(update_fields=['user2_last_read_at'])
        else:
            return Response(
                {'error': 'Not a participant in this thread'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        thread.messages.filter(is_read=False).exclude(sender_id=user_id).update(
            is_read=True,
            read_at=now
        )
        
        return Response({'message': 'Messages marked as read'})
    
    @action(detail=False, methods=['get'])
    def with_user(self, request):
        """Get or check if a thread exists with a specific user."""
        target_user_id = request.query_params.get('user_id')
        
        if not target_user_id:
            return Response(
                {'error': 'user_id query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ctx = get_user_context(request)
        current_user_id = ctx['user_id']
        
        sorted_ids = sorted([str(current_user_id), str(target_user_id)])
        thread = DirectMessageThread.objects.filter(
            Q(user1_id=sorted_ids[0], user2_id=sorted_ids[1]) |
            Q(user1_id=sorted_ids[1], user2_id=sorted_ids[0])
        ).first()
        
        if thread:
            serializer = DirectMessageThreadSerializer(thread, context={'request': request})
            return Response(serializer.data)
        
        return Response({'exists': False, 'thread': None})
