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


class DirectMessageThread(models.Model):
    """
    Represents a private conversation between exactly two users.
    This is the DM equivalent of a ChatRoom.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user1_id = models.CharField(max_length=255, db_index=True)
    user1_name = models.CharField(max_length=255, blank=True)
    user1_email = models.EmailField(blank=True)
    
    user2_id = models.CharField(max_length=255, db_index=True)
    user2_name = models.CharField(max_length=255, blank=True)
    user2_email = models.EmailField(blank=True)
    
    latest_message = models.ForeignKey(
        'DirectMessage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+'
    )
    
    user1_last_read_at = models.DateTimeField(null=True, blank=True)
    user2_last_read_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_dm_threads'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user1_id', 'user2_id']),
            models.Index(fields=['user2_id', 'user1_id']),
        ]
    
    def __str__(self):
        return f"DM: {self.user1_name} <-> {self.user2_name}"
    
    @classmethod
    def get_channel_name(cls, user_id_1: str, user_id_2: str) -> str:
        """
        Generate a consistent channel name for a DM between two users.
        Always sorts the IDs to ensure the same channel regardless of order.
        """
        sorted_ids = sorted([str(user_id_1), str(user_id_2)])
        return f"dm_{sorted_ids[0]}_{sorted_ids[1]}"
    
    @property
    def channel_name(self) -> str:
        """Get the WebSocket channel name for this thread."""
        return self.get_channel_name(self.user1_id, self.user2_id)
    
    @classmethod
    def get_or_create_thread(cls, user1_id: str, user1_name: str, user1_email: str,
                             user2_id: str, user2_name: str, user2_email: str):
        """
        Get existing thread or create a new one between two users.
        Always stores users in sorted order (by ID) for consistency.
        """
        sorted_ids = sorted([str(user1_id), str(user2_id)])
        
        thread = cls.objects.filter(
            user1_id=sorted_ids[0], 
            user2_id=sorted_ids[1]
        ).first()
        
        if thread:
            return thread, False
        
        if str(user1_id) == sorted_ids[0]:
            first_name, first_email = user1_name, user1_email
            second_name, second_email = user2_name, user2_email
        else:
            first_name, first_email = user2_name, user2_email
            second_name, second_email = user1_name, user1_email
        
        thread = cls.objects.create(
            user1_id=sorted_ids[0],
            user1_name=first_name,
            user1_email=first_email,
            user2_id=sorted_ids[1],
            user2_name=second_name,
            user2_email=second_email,
        )
        
        return thread, True
    
    def get_other_user(self, current_user_id: str) -> dict:
        """Get the other participant's info given the current user."""
        if str(self.user1_id) == str(current_user_id):
            return {
                'user_id': self.user2_id,
                'user_name': self.user2_name,
                'user_email': self.user2_email,
            }
        return {
            'user_id': self.user1_id,
            'user_name': self.user1_name,
            'user_email': self.user1_email,
        }
    
    def get_unread_count(self, user_id: str) -> int:
        """Get unread message count for a user."""
        if str(user_id) == str(self.user1_id):
            last_read = self.user1_last_read_at
        else:
            last_read = self.user2_last_read_at
        
        if not last_read:
            return self.messages.count()
        
        return self.messages.filter(created_at__gt=last_read).exclude(sender_id=user_id).count()


class DirectMessage(models.Model):
    """
    A message in a direct message thread.
    """
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('file', 'File'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread = models.ForeignKey(DirectMessageThread, on_delete=models.CASCADE, related_name='messages')
    
    sender_id = models.CharField(max_length=255, db_index=True)
    sender_name = models.CharField(max_length=255, blank=True)
    sender_email = models.EmailField(blank=True)
    
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    content = models.TextField()
    
    attachment_url = models.URLField(blank=True, null=True)
    attachment_name = models.CharField(max_length=255, blank=True)
    attachment_type = models.CharField(max_length=100, blank=True)
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_dm_messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['thread', 'created_at']),
            models.Index(fields=['sender_id']),
        ]
    
    def __str__(self):
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{self.sender_name}: {preview}"
