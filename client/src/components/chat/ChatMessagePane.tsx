import { useEffect, useRef, useState, useCallback } from 'react';
import { format } from 'date-fns';
import { Send, Smile, Paperclip, Hash, MoreVertical, Reply } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  useChatRoom,
  useMessages,
  useChatWebSocket,
  type Message,
  type TypingUser,
} from '@/hooks/use-chat';

interface ChatMessagePaneProps {
  roomId: string | null;
  userId: string;
  userName: string;
  userEmail: string;
}

function getInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

function MessageBubble({
  message,
  isOwnMessage,
  showAvatar,
  onReply,
}: {
  message: Message;
  isOwnMessage: boolean;
  showAvatar: boolean;
  onReply?: (message: Message) => void;
}) {
  const [showActions, setShowActions] = useState(false);

  return (
    <div
      className={`group flex items-start gap-3 px-4 py-1 hover:bg-accent/50 ${
        showAvatar ? 'mt-4' : ''
      }`}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
      data-testid={`message-${message.id}`}
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
        
        <div className="relative">
          <p className="break-words text-sm leading-relaxed">{message.content}</p>
          
          {message.reactions && message.reactions.length > 0 && (
            <div className="mt-1 flex flex-wrap gap-1">
              {message.reactions.map((reaction) => (
                <span
                  key={reaction.id}
                  className="inline-flex items-center rounded-full bg-accent px-2 py-0.5 text-xs"
                >
                  {reaction.emoji} 1
                </span>
              ))}
            </div>
          )}
          
          {message.reply_count > 0 && (
            <button className="mt-1 text-xs text-primary hover:underline">
              {message.reply_count} {message.reply_count === 1 ? 'reply' : 'replies'}
            </button>
          )}
        </div>
      </div>
      
      {showActions && (
        <div className="flex items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7"
                  onClick={() => onReply?.(message)}
                >
                  <Reply className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Reply in thread</TooltipContent>
            </Tooltip>
          </TooltipProvider>
          
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" className="h-7 w-7">
                  <Smile className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Add reaction</TooltipContent>
            </Tooltip>
          </TooltipProvider>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-7 w-7">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem>Copy text</DropdownMenuItem>
              <DropdownMenuItem>Pin message</DropdownMenuItem>
              {isOwnMessage && (
                <>
                  <DropdownMenuItem>Edit message</DropdownMenuItem>
                  <DropdownMenuItem className="text-destructive">
                    Delete message
                  </DropdownMenuItem>
                </>
              )}
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
  let text = '';
  
  if (names.length === 1) {
    text = `${names[0]} is typing...`;
  } else if (names.length === 2) {
    text = `${names[0]} and ${names[1]} are typing...`;
  } else {
    text = 'Several people are typing...';
  }

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

export function ChatMessagePane({
  roomId,
  userId,
  userName,
  userEmail,
}: ChatMessagePaneProps) {
  const [newMessage, setNewMessage] = useState('');
  const [replyTo, setReplyTo] = useState<Message | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout>();
  
  const { data: room } = useChatRoom(roomId);
  const { data: initialMessages, isLoading } = useMessages(roomId);
  
  const {
    isConnected,
    messages: wsMessages,
    typingUsers,
    sendMessage,
    startTyping,
    stopTyping,
    markAsRead,
    setMessages,
  } = useChatWebSocket(roomId, userId, userName, userEmail);

  useEffect(() => {
    if (initialMessages?.messages) {
      setMessages(initialMessages.messages);
    }
  }, [initialMessages, setMessages]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [wsMessages]);

  useEffect(() => {
    if (roomId && isConnected) {
      markAsRead();
    }
  }, [roomId, isConnected, markAsRead]);

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
    
    sendMessage(newMessage.trim(), replyTo?.id);
    setNewMessage('');
    setReplyTo(null);
    stopTyping();
  }, [newMessage, replyTo, sendMessage, stopTyping]);

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

  if (!roomId) {
    return (
      <div className="flex h-full flex-col items-center justify-center text-muted-foreground">
        <Hash className="mb-4 h-12 w-12" />
        <h3 className="text-lg font-medium">Select a channel</h3>
        <p className="text-sm">Choose a channel to start messaging</p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b px-4 py-3">
        <div className="flex items-center gap-2">
          <Hash className="h-5 w-5 text-muted-foreground" />
          <h2 className="font-semibold">{room?.name || 'Loading...'}</h2>
          {room?.description && (
            <>
              <Separator orientation="vertical" className="h-4" />
              <span className="text-sm text-muted-foreground">{room.description}</span>
            </>
          )}
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
              <Hash className="mb-4 h-12 w-12" />
              <h3 className="text-lg font-medium">Welcome to #{room?.name}</h3>
              <p className="text-sm">This is the start of the channel.</p>
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
                <MessageBubble
                  key={message.id}
                  message={message}
                  isOwnMessage={message.sender_id === userId}
                  showAvatar={showAvatar}
                  onReply={(msg) => setReplyTo(msg)}
                />
              );
            })
          )}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      <TypingIndicator users={typingUsers.filter((u) => u.user_id !== userId)} />

      {replyTo && (
        <div className="flex items-center justify-between border-t bg-accent/50 px-4 py-2">
          <div className="flex items-center gap-2 text-sm">
            <Reply className="h-4 w-4" />
            <span>Replying to {replyTo.sender_name}</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setReplyTo(null)}
          >
            Cancel
          </Button>
        </div>
      )}

      <div className="border-t p-4">
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" className="flex-shrink-0">
            <Paperclip className="h-5 w-5" />
          </Button>
          <Input
            placeholder={`Message #${room?.name || 'channel'}`}
            value={newMessage}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            className="flex-1"
            data-testid="input-message"
          />
          <Button variant="ghost" size="icon" className="flex-shrink-0">
            <Smile className="h-5 w-5" />
          </Button>
          <Button
            onClick={handleSendMessage}
            disabled={!newMessage.trim() || !isConnected}
            className="flex-shrink-0"
            data-testid="button-send-message"
          >
            <Send className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </div>
  );
}
