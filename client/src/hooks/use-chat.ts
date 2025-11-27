import { useState, useEffect, useCallback, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export interface ChatRoom {
  id: string;
  name: string;
  description: string;
  room_type: 'public' | 'private' | 'direct' | 'project';
  project_id: string | null;
  created_by: string;
  created_at: string;
  updated_at: string;
  is_archived: boolean;
  member_count: number;
  unread_count: number;
  last_message: {
    id: string;
    content: string;
    sender_name: string;
    created_at: string;
  } | null;
}

export interface Message {
  id: string;
  room_id?: string;
  sender_id: string;
  sender_email: string;
  sender_name: string;
  message_type: 'text' | 'system' | 'file';
  content: string;
  mentions: string[];
  attachment_url: string | null;
  attachment_name: string | null;
  parent_message: string | null;
  is_edited: boolean;
  edited_at: string | null;
  created_at: string;
  reactions: MessageReaction[];
  reply_count: number;
}

export interface MessageReaction {
  id: string;
  user_id: string;
  user_name: string;
  emoji: string;
  created_at: string;
}

export interface TypingUser {
  user_id: string;
  user_name: string;
  is_typing: boolean;
}

export interface UserPresence {
  user_id: string;
  user_name: string;
  status: 'online' | 'offline';
}

export interface DirectMessageThread {
  id: string;
  user1_id: string;
  user1_name: string;
  user1_email: string;
  user2_id: string;
  user2_name: string;
  user2_email: string;
  created_at: string;
  updated_at: string;
  channel_name: string;
  other_user: {
    user_id: string;
    user_name: string;
    user_email: string;
  } | null;
  unread_count: number;
  last_message: {
    id: string;
    content: string;
    sender_name: string;
    created_at: string;
  } | null;
}

export interface DirectMessage {
  id: string;
  thread: string;
  sender_id: string;
  sender_name: string;
  sender_email: string;
  message_type: 'text' | 'file' | 'system';
  content: string;
  is_read: boolean;
  read_at: string | null;
  is_edited: boolean;
  edited_at: string | null;
  is_deleted: boolean;
  created_at: string;
}

interface WebSocketMessage {
  type: string;
  message?: Message;
  user_id?: string;
  user_name?: string;
  is_typing?: boolean;
  status?: string;
  emoji?: string;
  action?: string;
  message_id?: string;
}

export function useChatRooms() {
  return useQuery<ChatRoom[]>({
    queryKey: ['chat-rooms'],
    queryFn: async () => {
      const response = await fetch('/api/v1/chat/rooms/');
      if (!response.ok) throw new Error('Failed to fetch rooms');
      const data = await response.json();
      return data.results || data;
    },
    staleTime: 30000,
  });
}

export function useChatRoom(roomId: string | null) {
  return useQuery<ChatRoom>({
    queryKey: ['chat-room', roomId],
    queryFn: async () => {
      if (!roomId) throw new Error('No room ID');
      const response = await fetch(`/api/v1/chat/rooms/${roomId}/`);
      if (!response.ok) throw new Error('Failed to fetch room');
      return response.json();
    },
    enabled: !!roomId,
  });
}

export function useMessages(roomId: string | null) {
  return useQuery<{ messages: Message[]; has_more: boolean }>({
    queryKey: ['chat-messages', roomId],
    queryFn: async () => {
      if (!roomId) throw new Error('No room ID');
      const response = await fetch(`/api/v1/chat/rooms/${roomId}/messages/`);
      if (!response.ok) throw new Error('Failed to fetch messages');
      return response.json();
    },
    enabled: !!roomId,
    staleTime: 10000,
  });
}

export function useCreateRoom() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: { 
      name: string; 
      description?: string; 
      room_type?: string;
      project_id?: string;
    }) => {
      const response = await fetch('/api/v1/chat/rooms/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error('Failed to create room');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chat-rooms'] });
    },
  });
}

export function useJoinRoom() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (roomId: string) => {
      const response = await fetch(`/api/v1/chat/rooms/${roomId}/join/`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to join room');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chat-rooms'] });
    },
  });
}

export function useChatWebSocket(
  roomId: string | null,
  userId: string,
  userName: string,
  userEmail: string
) {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [typingUsers, setTypingUsers] = useState<TypingUser[]>([]);
  const [onlineUsers, setOnlineUsers] = useState<Set<string>>(new Set<string>());
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const queryClient = useQueryClient();

  const connect = useCallback(() => {
    if (!roomId) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const params = new URLSearchParams({
      user_id: userId,
      user_name: userName,
      user_email: userEmail,
    });
    const wsUrl = `${protocol}//${window.location.host}/ws/chat/${roomId}/?${params}`;

    console.log('[Chat] Connecting to WebSocket:', wsUrl);

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('[Chat] WebSocket connected');
      setIsConnected(true);
    };

    ws.onclose = (event) => {
      console.log('[Chat] WebSocket closed:', event.code);
      setIsConnected(false);
      
      if (event.code !== 1000) {
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('[Chat] Attempting to reconnect...');
          connect();
        }, 3000);
      }
    };

    ws.onerror = (error) => {
      console.error('[Chat] WebSocket error:', error);
    };

    ws.onmessage = (event) => {
      try {
        const data: WebSocketMessage = JSON.parse(event.data);
        console.log('[Chat] Received:', data);

        switch (data.type) {
          case 'new_message':
            if (data.message) {
              setMessages((prev) => [...prev, data.message!]);
              queryClient.invalidateQueries({ queryKey: ['chat-rooms'] });
            }
            break;

          case 'typing':
            if (data.user_id && data.user_name !== undefined) {
              setTypingUsers((prev) => {
                const filtered = prev.filter((u) => u.user_id !== data.user_id);
                if (data.is_typing) {
                  return [...filtered, { 
                    user_id: data.user_id!, 
                    user_name: data.user_name!, 
                    is_typing: true 
                  }];
                }
                return filtered;
              });
            }
            break;

          case 'user_presence':
            if (data.user_id) {
              setOnlineUsers((prev) => {
                const newSet = new Set(prev);
                if (data.status === 'online') {
                  newSet.add(data.user_id!);
                } else {
                  newSet.delete(data.user_id!);
                }
                return newSet;
              });
            }
            break;

          case 'reaction':
            break;
        }
      } catch (error) {
        console.error('[Chat] Failed to parse message:', error);
      }
    };
  }, [roomId, userId, userName, userEmail, queryClient]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close(1000, 'User disconnected');
      wsRef.current = null;
    }
    setIsConnected(false);
    setMessages([]);
    setTypingUsers([]);
  }, []);

  useEffect(() => {
    if (roomId) {
      connect();
    }
    return () => {
      disconnect();
    };
  }, [roomId, connect, disconnect]);

  const sendMessage = useCallback((content: string, parentMessageId?: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'chat_message',
        content,
        parent_message_id: parentMessageId,
      }));
    }
  }, []);

  const startTyping = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'typing_start' }));
    }
  }, []);

  const stopTyping = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'typing_stop' }));
    }
  }, []);

  const markAsRead = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'mark_read' }));
    }
  }, []);

  const addReaction = useCallback((messageId: string, emoji: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'reaction_add',
        message_id: messageId,
        emoji,
      }));
    }
  }, []);

  return {
    isConnected,
    messages,
    typingUsers,
    onlineUsers,
    sendMessage,
    startTyping,
    stopTyping,
    markAsRead,
    addReaction,
    setMessages,
  };
}

export function useDMThreads() {
  return useQuery<DirectMessageThread[]>({
    queryKey: ['dm-threads'],
    queryFn: async () => {
      const response = await fetch('/api/v1/chat/dm/');
      if (!response.ok) throw new Error('Failed to fetch DM threads');
      const data = await response.json();
      return data.results || data;
    },
    staleTime: 30000,
  });
}

export function useDMThread(threadId: string | null) {
  return useQuery<DirectMessageThread>({
    queryKey: ['dm-thread', threadId],
    queryFn: async () => {
      if (!threadId) throw new Error('No thread ID');
      const response = await fetch(`/api/v1/chat/dm/${threadId}/`);
      if (!response.ok) throw new Error('Failed to fetch DM thread');
      return response.json();
    },
    enabled: !!threadId,
  });
}

export function useDMMessages(threadId: string | null) {
  return useQuery<{ messages: DirectMessage[]; thread_id: string; channel_name: string }>({
    queryKey: ['dm-messages', threadId],
    queryFn: async () => {
      if (!threadId) throw new Error('No thread ID');
      const response = await fetch(`/api/v1/chat/dm/${threadId}/messages/`);
      if (!response.ok) throw new Error('Failed to fetch DM messages');
      return response.json();
    },
    enabled: !!threadId,
    staleTime: 10000,
  });
}

export function useCreateDMThread() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: { 
      target_user_id: string; 
      target_user_name?: string; 
      target_user_email?: string;
    }) => {
      const response = await fetch('/api/v1/chat/dm/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error('Failed to create DM thread');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dm-threads'] });
    },
  });
}

export function useSendDM() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ threadId, content }: { threadId: string; content: string }) => {
      const response = await fetch(`/api/v1/chat/dm/${threadId}/send/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content }),
      });
      if (!response.ok) throw new Error('Failed to send DM');
      return response.json();
    },
    onSuccess: (_, { threadId }) => {
      queryClient.invalidateQueries({ queryKey: ['dm-messages', threadId] });
      queryClient.invalidateQueries({ queryKey: ['dm-threads'] });
    },
  });
}

export function useDMWebSocket(
  threadId: string | null,
  userId: string,
  userName: string,
  userEmail: string
) {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<DirectMessage[]>([]);
  const [typingUsers, setTypingUsers] = useState<TypingUser[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const queryClient = useQueryClient();

  const connect = useCallback(() => {
    if (!threadId) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const params = new URLSearchParams({
      user_id: userId,
      user_name: userName,
      user_email: userEmail,
    });
    const wsUrl = `${protocol}//${window.location.host}/ws/dm/${threadId}/?${params}`;

    console.log('[DM] Connecting to WebSocket:', wsUrl);

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('[DM] WebSocket connected');
      setIsConnected(true);
    };

    ws.onclose = (event) => {
      console.log('[DM] WebSocket closed:', event.code);
      setIsConnected(false);
      
      if (event.code !== 1000) {
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('[DM] Attempting to reconnect...');
          connect();
        }, 3000);
      }
    };

    ws.onerror = (error) => {
      console.error('[DM] WebSocket error:', error);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('[DM] Received:', data);

        switch (data.type) {
          case 'new_dm':
            if (data.message) {
              setMessages((prev) => [...prev, data.message]);
              queryClient.invalidateQueries({ queryKey: ['dm-threads'] });
            }
            break;

          case 'typing':
            if (data.user_id && data.user_name !== undefined) {
              setTypingUsers((prev) => {
                const filtered = prev.filter((u) => u.user_id !== data.user_id);
                if (data.is_typing) {
                  return [...filtered, { 
                    user_id: data.user_id, 
                    user_name: data.user_name, 
                    is_typing: true 
                  }];
                }
                return filtered;
              });
            }
            break;
        }
      } catch (error) {
        console.error('[DM] Failed to parse message:', error);
      }
    };
  }, [threadId, userId, userName, userEmail, queryClient]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close(1000, 'User disconnected');
      wsRef.current = null;
    }
    setIsConnected(false);
    setMessages([]);
    setTypingUsers([]);
  }, []);

  useEffect(() => {
    if (threadId) {
      connect();
    }
    return () => {
      disconnect();
    };
  }, [threadId, connect, disconnect]);

  const sendMessage = useCallback((content: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'dm_message',
        content,
      }));
    }
  }, []);

  const startTyping = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'typing_start' }));
    }
  }, []);

  const stopTyping = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'typing_stop' }));
    }
  }, []);

  const markAsRead = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'mark_read' }));
    }
  }, []);

  return {
    isConnected,
    messages,
    typingUsers,
    sendMessage,
    startTyping,
    stopTyping,
    markAsRead,
    setMessages,
  };
}
