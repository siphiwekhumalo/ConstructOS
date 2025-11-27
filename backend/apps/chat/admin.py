from django.contrib import admin
from .models import ChatRoom, RoomMembership, Message, MessageReaction


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'room_type', 'created_by', 'created_at', 'is_archived']
    list_filter = ['room_type', 'is_archived']
    search_fields = ['name', 'description']


@admin.register(RoomMembership)
class RoomMembershipAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'room', 'role', 'joined_at']
    list_filter = ['role']
    search_fields = ['user_name', 'user_email']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender_name', 'room', 'message_type', 'created_at', 'is_deleted']
    list_filter = ['message_type', 'is_deleted']
    search_fields = ['content', 'sender_name']


@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'emoji', 'message', 'created_at']
