import { useEffect, useRef, useState, useCallback } from 'react';
import { format } from 'date-fns';
import { Send, User, MoreVertical } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  useDMThread,
  useDMMessages,
  useDMWebSocket,
  type DirectMessage,
  type TypingUser,
} from '@/hooks/use-chat';

interface DMMessagePaneProps {
  threadId: string | null;
  userId: string;
  userName: string;
  userEmail: string;
}

function getInitials(name: string): string {
  if (!name) return '?';
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

function DMBubble({
  message,
  isOwnMessage,
  showAvatar,
}: {
  message: DirectMessage;
  isOwnMessage: boolean;
  showAvatar: boolean;
}) {
  const [showActions, setShowActions] = useState(false);

  return (
    <div
      className={`group flex items-start gap-3 px-4 py-1 hover:bg-accent/50 ${
        showAvatar ? 'mt-4' : ''
      }`}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
      data-testid={`dm-message-${message.id}`}
    >
      <div className="w-10 flex-shrink-0">
        {showAvatar && (
          <Avatar className="h-10 w-10">
            <AvatarFallback className="bg-primary/10 text-primary">
              {getInitials(message.sender_name)}
            </AvatarFallback>
          </Avatar>
        )}
      </div>
      
      <div className="flex-1 min-w-0">
        {showAvatar && (
          <div className="flex items-baseline gap-2">
            <span className="font-semibold">{message.sender_name}</span>
            <span className="text-xs text-muted-foreground">
              {format(new Date(message.created_at), 'h:mm a')}
            </span>
            {message.is_edited && (
              <span className="text-xs text-muted-foreground">(edited)</span>
            )}
          </div>
        )}
        
        <p className="break-words text-sm leading-relaxed">{message.content}</p>
      </div>
      
      {showActions && isOwnMessage && (
        <div className="flex items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-7 w-7">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem>Copy text</DropdownMenuItem>
              <DropdownMenuItem>Edit message</DropdownMenuItem>
              <DropdownMenuItem className="text-destructive">
                Delete message
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      )}
    </div>
  );
}

function TypingIndicator({ users }: { users: TypingUser[] }) {
  if (users.length === 0) return null;

  const names = users.map((u) => u.user_name);
  const text = names.length === 1 
    ? `${names[0]} is typing...` 
    : 'Typing...';

  return (
    <div className="flex items-center gap-2 px-4 py-2 text-sm text-muted-foreground">
      <div className="flex space-x-1">
        <span className="inline-block h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.3s]" />
        <span className="inline-block h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.15s]" />
        <span className="inline-block h-2 w-2 animate-bounce rounded-full bg-muted-foreground" />
      </div>
      <span>{text}</span>
    </div>
  );
}

export function DMMessagePane({
  threadId,
  userId,
  userName,
  userEmail,
}: DMMessagePaneProps) {
  const [newMessage, setNewMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout>();
  
  const { data: thread } = useDMThread(threadId);
  const { data: initialMessages, isLoading } = useDMMessages(threadId);
  
  const {
    isConnected,
    messages: wsMessages,
    typingUsers,
    sendMessage,
    startTyping,
    stopTyping,
    markAsRead,
    setMessages,
  } = useDMWebSocket(threadId, userId, userName, userEmail);

  const otherUser = thread?.other_user;

  useEffect(() => {
    if (initialMessages?.messages) {
      setMessages(initialMessages.messages);
    }
  }, [initialMessages, setMessages]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [wsMessages]);

  useEffect(() => {
    if (threadId && isConnected) {
      markAsRead();
    }
  }, [threadId, isConnected, markAsRead]);

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setNewMessage(e.target.value);
      
      startTyping();
      
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      
      typingTimeoutRef.current = setTimeout(() => {
        stopTyping();
      }, 2000);
    },
    [startTyping, stopTyping]
  );

  const handleSendMessage = useCallback(() => {
    if (!newMessage.trim()) return;
    
    sendMessage(newMessage.trim());
    setNewMessage('');
    stopTyping();
  }, [newMessage, sendMessage, stopTyping]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
      }
    },
    [handleSendMessage]
  );

  const allMessages = wsMessages;

  if (!threadId) {
    return (
      <div className="flex h-full flex-col items-center justify-center text-muted-foreground">
        <User className="mb-4 h-12 w-12" />
        <h3 className="text-lg font-medium">Select a conversation</h3>
        <p className="text-sm">Choose a conversation or start a new one</p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b px-4 py-3">
        <div className="flex items-center gap-3">
          <Avatar className="h-8 w-8">
            <AvatarFallback className="bg-primary/10 text-primary">
              {getInitials(otherUser?.user_name || 'Unknown')}
            </AvatarFallback>
          </Avatar>
          <div>
            <h2 className="font-semibold">{otherUser?.user_name || 'Loading...'}</h2>
            {otherUser?.user_email && (
              <span className="text-xs text-muted-foreground">{otherUser.user_email}</span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {isConnected ? (
            <span className="flex items-center gap-1 text-xs text-green-600">
              <span className="h-2 w-2 rounded-full bg-green-500" />
              Connected
            </span>
          ) : (
            <span className="flex items-center gap-1 text-xs text-amber-600">
              <span className="h-2 w-2 rounded-full bg-amber-500" />
              Connecting...
            </span>
          )}
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="py-4">
          {isLoading ? (
            <div className="space-y-4 p-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="flex gap-3">
                  <div className="h-10 w-10 animate-pulse rounded-full bg-muted" />
                  <div className="flex-1 space-y-2">
                    <div className="h-4 w-32 animate-pulse rounded bg-muted" />
                    <div className="h-4 w-full animate-pulse rounded bg-muted" />
                  </div>
                </div>
              ))}
            </div>
          ) : allMessages.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <User className="mb-4 h-12 w-12" />
              <h3 className="text-lg font-medium">Start the conversation</h3>
              <p className="text-sm">Send a message to {otherUser?.user_name || 'this user'}</p>
            </div>
          ) : (
            allMessages.map((message, index) => {
              const prevMessage = index > 0 ? allMessages[index - 1] : null;
              const showAvatar =
                !prevMessage ||
                prevMessage.sender_id !== message.sender_id ||
                new Date(message.created_at).getTime() -
                  new Date(prevMessage.created_at).getTime() >
                  300000;

              return (
                <DMBubble
                  key={message.id}
                  message={message}
                  isOwnMessage={message.sender_id === userId}
                  showAvatar={showAvatar}
                />
              );
            })
          )}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      <TypingIndicator users={typingUsers.filter((u) => u.user_id !== userId)} />

      <div className="border-t p-4">
        <div className="flex items-center gap-2">
          <Input
            placeholder={`Message ${otherUser?.user_name || 'user'}...`}
            value={newMessage}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            className="flex-1"
            data-testid="input-dm-message"
          />
          <Button
            onClick={handleSendMessage}
            disabled={!newMessage.trim() || !isConnected}
            className="flex-shrink-0"
            data-testid="button-send-dm"
          >
            <Send className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </div>
  );
}
