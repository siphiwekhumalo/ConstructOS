"""
WebSocket consumers for real-time chat functionality.
"""
import json
import logging
from datetime import datetime, timezone
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.cache import cache

from .models import ChatRoom, RoomMembership, Message, TypingIndicator, DirectMessageThread, DirectMessage

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for chat rooms.
    Handles real-time messaging, typing indicators, and presence.
    """
    
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        self.user_id = self.scope.get('user_id', 'anonymous')
        self.user_name = self.scope.get('user_name', 'Anonymous')
        self.user_email = self.scope.get('user_email', '')
        
        room_exists = await self.check_room_exists()
        if not room_exists:
            await self.close(code=4004)
            return
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        await self.update_presence(online=True)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user_id': self.user_id,
                'user_name': self.user_name,
            }
        )
        
        logger.info(f"User {self.user_name} connected to room {self.room_id}")
    
    async def disconnect(self, close_code):
        await self.update_presence(online=False)
        await self.clear_typing()
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'user_id': self.user_id,
                'user_name': self.user_name,
            }
        )
        
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        logger.info(f"User {self.user_name} disconnected from room {self.room_id}")
    
    async def receive_json(self, content):
        """Handle incoming WebSocket messages."""
        message_type = content.get('type', '')
        
        handlers = {
            'chat_message': self.handle_chat_message,
            'typing_start': self.handle_typing_start,
            'typing_stop': self.handle_typing_stop,
            'mark_read': self.handle_mark_read,
            'reaction_add': self.handle_reaction_add,
            'reaction_remove': self.handle_reaction_remove,
        }
        
        handler = handlers.get(message_type)
        if handler:
            await handler(content)
        else:
            await self.send_json({
                'type': 'error',
                'message': f'Unknown message type: {message_type}'
            })
    
    async def handle_chat_message(self, content):
        """Process and broadcast a new chat message."""
        message_content = content.get('content', '').strip()
        if not message_content:
            return
        
        message = await self.save_message(
            content=message_content,
            message_type=content.get('message_type', 'text'),
            parent_id=content.get('parent_message_id'),
            mentions=content.get('mentions', [])
        )
        
        if message:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message_broadcast',
                    'message': {
                        'id': str(message.id),
                        'room_id': str(self.room_id),
                        'sender_id': self.user_id,
                        'sender_name': self.user_name,
                        'sender_email': self.user_email,
                        'content': message.content,
                        'message_type': message.message_type,
                        'mentions': message.mentions,
                        'parent_message_id': str(message.parent_message_id) if message.parent_message else None,
                        'created_at': message.created_at.isoformat(),
                    }
                }
            )
    
    async def handle_typing_start(self, content):
        """User started typing."""
        await self.set_typing(True)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_broadcast',
                'user_id': self.user_id,
                'user_name': self.user_name,
                'is_typing': True,
            }
        )
    
    async def handle_typing_stop(self, content):
        """User stopped typing."""
        await self.clear_typing()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_broadcast',
                'user_id': self.user_id,
                'user_name': self.user_name,
                'is_typing': False,
            }
        )
    
    async def handle_mark_read(self, content):
        """Mark messages as read up to a certain point."""
        await self.update_last_read()
    
    async def handle_reaction_add(self, content):
        """Add a reaction to a message."""
        message_id = content.get('message_id')
        emoji = content.get('emoji')
        
        if message_id and emoji:
            await self.add_reaction(message_id, emoji)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'reaction_broadcast',
                    'message_id': message_id,
                    'user_id': self.user_id,
                    'user_name': self.user_name,
                    'emoji': emoji,
                    'action': 'add',
                }
            )
    
    async def handle_reaction_remove(self, content):
        """Remove a reaction from a message."""
        message_id = content.get('message_id')
        emoji = content.get('emoji')
        
        if message_id and emoji:
            await self.remove_reaction(message_id, emoji)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'reaction_broadcast',
                    'message_id': message_id,
                    'user_id': self.user_id,
                    'user_name': self.user_name,
                    'emoji': emoji,
                    'action': 'remove',
                }
            )
    
    async def chat_message_broadcast(self, event):
        """Send chat message to WebSocket."""
        await self.send_json({
            'type': 'new_message',
            'message': event['message']
        })
    
    async def typing_broadcast(self, event):
        """Send typing indicator to WebSocket."""
        if event['user_id'] != self.user_id:
            await self.send_json({
                'type': 'typing',
                'user_id': event['user_id'],
                'user_name': event['user_name'],
                'is_typing': event['is_typing'],
            })
    
    async def reaction_broadcast(self, event):
        """Send reaction update to WebSocket."""
        await self.send_json({
            'type': 'reaction',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
            'user_name': event['user_name'],
            'emoji': event['emoji'],
            'action': event['action'],
        })
    
    async def user_joined(self, event):
        """Notify room that a user joined."""
        if event['user_id'] != self.user_id:
            await self.send_json({
                'type': 'user_presence',
                'user_id': event['user_id'],
                'user_name': event['user_name'],
                'status': 'online',
            })
    
    async def user_left(self, event):
        """Notify room that a user left."""
        if event['user_id'] != self.user_id:
            await self.send_json({
                'type': 'user_presence',
                'user_id': event['user_id'],
                'user_name': event['user_name'],
                'status': 'offline',
            })
    
    @database_sync_to_async
    def check_room_exists(self):
        return ChatRoom.objects.filter(id=self.room_id, is_archived=False).exists()
    
    @database_sync_to_async
    def save_message(self, content, message_type='text', parent_id=None, mentions=None):
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            
            parent_message = None
            if parent_id:
                try:
                    parent_message = Message.objects.get(id=parent_id, room=room)
                except Message.DoesNotExist:
                    pass
            
            message = Message.objects.create(
                room=room,
                sender_id=self.user_id,
                sender_email=self.user_email,
                sender_name=self.user_name,
                message_type=message_type,
                content=content,
                mentions=mentions or [],
                parent_message=parent_message,
            )
            
            room.updated_at = datetime.now(timezone.utc)
            room.save(update_fields=['updated_at'])
            
            return message
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            return None
    
    @database_sync_to_async
    def add_reaction(self, message_id, emoji):
        from .models import MessageReaction
        try:
            message = Message.objects.get(id=message_id)
            MessageReaction.objects.get_or_create(
                message=message,
                user_id=self.user_id,
                emoji=emoji,
                defaults={'user_name': self.user_name}
            )
        except Exception as e:
            logger.error(f"Error adding reaction: {e}")
    
    @database_sync_to_async
    def remove_reaction(self, message_id, emoji):
        from .models import MessageReaction
        try:
            MessageReaction.objects.filter(
                message_id=message_id,
                user_id=self.user_id,
                emoji=emoji
            ).delete()
        except Exception as e:
            logger.error(f"Error removing reaction: {e}")
    
    @database_sync_to_async
    def update_last_read(self):
        try:
            RoomMembership.objects.filter(
                room_id=self.room_id,
                user_id=self.user_id
            ).update(last_read_at=datetime.now(timezone.utc))
        except Exception as e:
            logger.error(f"Error updating last read: {e}")
    
    @database_sync_to_async
    def set_typing(self, is_typing):
        if is_typing:
            TypingIndicator.objects.update_or_create(
                room_id=self.room_id,
                user_id=self.user_id,
                defaults={'user_name': self.user_name}
            )
        else:
            TypingIndicator.objects.filter(
                room_id=self.room_id,
                user_id=self.user_id
            ).delete()
    
    @database_sync_to_async
    def clear_typing(self):
        TypingIndicator.objects.filter(
            room_id=self.room_id,
            user_id=self.user_id
        ).delete()
    
    async def update_presence(self, online=True):
        """Update user presence in cache."""
        cache_key = f'presence_{self.room_id}_{self.user_id}'
        if online:
            cache.set(cache_key, {
                'user_id': self.user_id,
                'user_name': self.user_name,
                'online': True
            }, timeout=300)
        else:
            cache.delete(cache_key)


class DirectMessageConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for Direct Messages.
    Uses private channel naming: dm_{sorted_user_ids}
    """
    
    async def connect(self):
        self.thread_id = self.scope['url_route']['kwargs']['thread_id']
        
        self.user_id = self.scope.get('user_id')
        self.user_name = self.scope.get('user_name', 'Anonymous')
        self.user_email = self.scope.get('user_email', '')
        
        if not self.user_id or self.user_id == 'anonymous':
            logger.warning(f"Unauthenticated DM WebSocket connection rejected for thread {self.thread_id}")
            await self.close(code=4001)
            return
        
        thread_info = await self.get_thread_info()
        if not thread_info:
            logger.warning(f"DM thread {self.thread_id} not found")
            await self.close(code=4004)
            return
        
        if str(self.user_id) not in [str(thread_info['user1_id']), str(thread_info['user2_id'])]:
            logger.warning(f"User {self.user_id} is not a participant of DM thread {self.thread_id}")
            await self.close(code=4003)
            return
        
        self.dm_group_name = thread_info['channel_name']
        
        await self.channel_layer.group_add(
            self.dm_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        logger.info(f"User {self.user_name} ({self.user_id}) connected to DM thread {self.thread_id}")
    
    async def disconnect(self, close_code):
        if hasattr(self, 'dm_group_name'):
            await self.channel_layer.group_discard(
                self.dm_group_name,
                self.channel_name
            )
        
        logger.info(f"User {self.user_name} disconnected from DM thread {self.thread_id}")
    
    async def receive_json(self, content):
        """Handle incoming WebSocket messages."""
        message_type = content.get('type', '')
        
        handlers = {
            'dm_message': self.handle_dm_message,
            'typing_start': self.handle_typing_start,
            'typing_stop': self.handle_typing_stop,
            'mark_read': self.handle_mark_read,
        }
        
        handler = handlers.get(message_type)
        if handler:
            await handler(content)
        else:
            await self.send_json({
                'type': 'error',
                'message': f'Unknown message type: {message_type}'
            })
    
    async def handle_dm_message(self, content):
        """Process and broadcast a new DM."""
        message_content = content.get('content', '').strip()
        if not message_content:
            return
        
        message = await self.save_dm(
            content=message_content,
            message_type=content.get('message_type', 'text'),
        )
        
        if message:
            await self.channel_layer.group_send(
                self.dm_group_name,
                {
                    'type': 'dm_message_broadcast',
                    'message': {
                        'id': str(message.id),
                        'thread_id': str(self.thread_id),
                        'sender_id': self.user_id,
                        'sender_name': self.user_name,
                        'sender_email': self.user_email,
                        'content': message.content,
                        'message_type': message.message_type,
                        'created_at': message.created_at.isoformat(),
                    }
                }
            )
    
    async def handle_typing_start(self, content):
        """User started typing."""
        await self.channel_layer.group_send(
            self.dm_group_name,
            {
                'type': 'typing_broadcast',
                'user_id': self.user_id,
                'user_name': self.user_name,
                'is_typing': True,
            }
        )
    
    async def handle_typing_stop(self, content):
        """User stopped typing."""
        await self.channel_layer.group_send(
            self.dm_group_name,
            {
                'type': 'typing_broadcast',
                'user_id': self.user_id,
                'user_name': self.user_name,
                'is_typing': False,
            }
        )
    
    async def handle_mark_read(self, content):
        """Mark messages as read."""
        await self.update_read_status()
    
    async def dm_message_broadcast(self, event):
        """Send DM to WebSocket."""
        await self.send_json({
            'type': 'new_dm',
            'message': event['message']
        })
    
    async def typing_broadcast(self, event):
        """Send typing indicator to WebSocket."""
        if event['user_id'] != self.user_id:
            await self.send_json({
                'type': 'typing',
                'user_id': event['user_id'],
                'user_name': event['user_name'],
                'is_typing': event['is_typing'],
            })
    
    @database_sync_to_async
    def get_thread_info(self):
        """Get thread info and channel name."""
        try:
            thread = DirectMessageThread.objects.get(id=self.thread_id)
            return {
                'user1_id': thread.user1_id,
                'user2_id': thread.user2_id,
                'channel_name': thread.channel_name,
            }
        except DirectMessageThread.DoesNotExist:
            return None
    
    @database_sync_to_async
    def save_dm(self, content, message_type='text'):
        """Save a DM to the database."""
        try:
            thread = DirectMessageThread.objects.get(id=self.thread_id)
            
            message = DirectMessage.objects.create(
                thread=thread,
                sender_id=self.user_id,
                sender_email=self.user_email,
                sender_name=self.user_name,
                message_type=message_type,
                content=content,
            )
            
            thread.latest_message = message
            thread.save(update_fields=['latest_message', 'updated_at'])
            
            return message
        except Exception as e:
            logger.error(f"Error saving DM: {e}")
            return None
    
    @database_sync_to_async
    def update_read_status(self):
        """Update read status for current user."""
        try:
            thread = DirectMessageThread.objects.get(id=self.thread_id)
            now = datetime.now(timezone.utc)
            
            if str(thread.user1_id) == str(self.user_id):
                thread.user1_last_read_at = now
                thread.save(update_fields=['user1_last_read_at'])
            elif str(thread.user2_id) == str(self.user_id):
                thread.user2_last_read_at = now
                thread.save(update_fields=['user2_last_read_at'])
            
            thread.messages.filter(is_read=False).exclude(sender_id=self.user_id).update(
                is_read=True,
                read_at=now
            )
        except Exception as e:
            logger.error(f"Error updating read status: {e}")
