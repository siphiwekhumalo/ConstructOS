"""
Chat models for real-time messaging in ConstructOS.
Provides Slack-like messaging with rooms, memberships, and messages.
"""
import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model


class ChatRoom(models.Model):
    """
    A chat room/channel for team communication.
    Can be project-specific, department-specific, or general.
    """
    ROOM_TYPES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('direct', 'Direct Message'),
        ('project', 'Project'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='public')
    
    project_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    
    created_by = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_archived = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'chat_rooms'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['room_type']),
            models.Index(fields=['is_archived']),
        ]
    
    def __str__(self):
        return f"#{self.name}"


class RoomMembership(models.Model):
    """
    Tracks user membership in chat rooms with roles.
    """
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='memberships')
    user_id = models.CharField(max_length=255, db_index=True)
    user_email = models.EmailField(blank=True)
    user_name = models.CharField(max_length=255, blank=True)
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    
    joined_at = models.DateTimeField(auto_now_add=True)
    last_read_at = models.DateTimeField(null=True, blank=True)
    
    is_muted = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'chat_room_memberships'
        unique_together = ['room', 'user_id']
        indexes = [
            models.Index(fields=['user_id', 'room']),
        ]
    
    def __str__(self):
        return f"{self.user_name} in {self.room.name}"


class Message(models.Model):
    """
    A message in a chat room.
    Supports text, mentions, and attachments.
    """
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('system', 'System'),
        ('file', 'File'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    
    sender_id = models.CharField(max_length=255, db_index=True)
    sender_email = models.EmailField(blank=True)
    sender_name = models.CharField(max_length=255, blank=True)
    
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    content = models.TextField()
    
    mentions = models.JSONField(default=list, blank=True)
    
    attachment_url = models.URLField(blank=True, null=True)
    attachment_name = models.CharField(max_length=255, blank=True)
    attachment_type = models.CharField(max_length=100, blank=True)
    
    parent_message = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='replies'
    )
    
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['room', 'created_at']),
            models.Index(fields=['sender_id']),
            models.Index(fields=['parent_message']),
        ]
    
    def __str__(self):
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{self.sender_name}: {preview}"


class MessageReaction(models.Model):
    """
    Emoji reactions on messages.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    user_id = models.CharField(max_length=255)
    user_name = models.CharField(max_length=255, blank=True)
    emoji = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_message_reactions'
        unique_together = ['message', 'user_id', 'emoji']
    
    def __str__(self):
        return f"{self.user_name} reacted {self.emoji}"


class TypingIndicator(models.Model):
    """
    Tracks users currently typing in a room.
    Uses in-memory or cache, not persisted long-term.
    """
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='typing_users')
    user_id = models.CharField(max_length=255)
    user_name = models.CharField(max_length=255, blank=True)
    started_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_typing_indicators'
        unique_together = ['room', 'user_id']
