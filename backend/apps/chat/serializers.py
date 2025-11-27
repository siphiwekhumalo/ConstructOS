"""
Serializers for chat models.
"""
from rest_framework import serializers
from .models import ChatRoom, RoomMembership, Message, MessageReaction


class MessageReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageReaction
        fields = ['id', 'user_id', 'user_name', 'emoji', 'created_at']
        read_only_fields = ['id', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    reactions = MessageReactionSerializer(many=True, read_only=True)
    reply_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'room', 'sender_id', 'sender_email', 'sender_name',
            'message_type', 'content', 'mentions',
            'attachment_url', 'attachment_name', 'attachment_type',
            'parent_message', 'is_edited', 'edited_at',
            'is_deleted', 'created_at', 'reactions', 'reply_count'
        ]
        read_only_fields = ['id', 'created_at', 'is_edited', 'edited_at', 'is_deleted']
    
    def get_reply_count(self, obj):
        return obj.replies.filter(is_deleted=False).count()


class RoomMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomMembership
        fields = [
            'id', 'room', 'user_id', 'user_email', 'user_name',
            'role', 'joined_at', 'last_read_at', 'is_muted'
        ]
        read_only_fields = ['id', 'joined_at']


class ChatRoomSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'name', 'description', 'room_type', 'project_id',
            'created_by', 'created_at', 'updated_at', 'is_archived',
            'member_count', 'unread_count', 'last_message'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_member_count(self, obj):
        return obj.memberships.count()
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if not request or not hasattr(request, 'user_id'):
            return 0
        
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            return 0
            
        membership = obj.memberships.filter(user_id=user_id).first()
        if not membership or not membership.last_read_at:
            return obj.messages.filter(is_deleted=False).count()
        
        return obj.messages.filter(
            is_deleted=False,
            created_at__gt=membership.last_read_at
        ).count()
    
    def get_last_message(self, obj):
        last_msg = obj.messages.filter(is_deleted=False).order_by('-created_at').first()
        if last_msg:
            return {
                'id': str(last_msg.id),
                'content': last_msg.content[:100],
                'sender_name': last_msg.sender_name,
                'created_at': last_msg.created_at.isoformat()
            }
        return None


class ChatRoomDetailSerializer(ChatRoomSerializer):
    memberships = RoomMembershipSerializer(many=True, read_only=True)
    
    class Meta(ChatRoomSerializer.Meta):
        fields = ChatRoomSerializer.Meta.fields + ['memberships']


class CreateRoomSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(required=False, allow_blank=True, default='')
    room_type = serializers.ChoiceField(choices=ChatRoom.ROOM_TYPES, default='public')
    project_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    member_ids = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )


class SendMessageSerializer(serializers.Serializer):
    content = serializers.CharField()
    message_type = serializers.ChoiceField(
        choices=Message.MESSAGE_TYPES, 
        default='text'
    )
    parent_message_id = serializers.UUIDField(required=False, allow_null=True)
    mentions = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
