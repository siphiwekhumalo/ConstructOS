import { useState } from 'react';
import { MessageSquare, Plus, Search, User } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { useDMThreads, useCreateDMThread, type DirectMessageThread } from '@/hooks/use-chat';
import { formatDistanceToNow } from 'date-fns';

interface DMThreadListProps {
  selectedThreadId: string | null;
  onSelectThread: (threadId: string) => void;
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

function StartDMDialog({ onSuccess }: { onSuccess?: (threadId: string) => void }) {
  const [open, setOpen] = useState(false);
  const [targetUserId, setTargetUserId] = useState('');
  const [targetUserName, setTargetUserName] = useState('');
  const [targetUserEmail, setTargetUserEmail] = useState('');
  
  const createThread = useCreateDMThread();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const thread = await createThread.mutateAsync({
        target_user_id: targetUserId,
        target_user_name: targetUserName,
        target_user_email: targetUserEmail,
      });
      setOpen(false);
      setTargetUserId('');
      setTargetUserName('');
      setTargetUserEmail('');
      onSuccess?.(thread.id);
    } catch (error) {
      console.error('Failed to start DM:', error);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon" className="h-8 w-8" data-testid="button-start-dm">
          <Plus className="h-4 w-4" />
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Start Direct Message</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="userId">User ID</Label>
            <Input
              id="userId"
              value={targetUserId}
              onChange={(e) => setTargetUserId(e.target.value)}
              placeholder="Enter user ID"
              required
              data-testid="input-dm-user-id"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="userName">Name (optional)</Label>
            <Input
              id="userName"
              value={targetUserName}
              onChange={(e) => setTargetUserName(e.target.value)}
              placeholder="User's name"
              data-testid="input-dm-user-name"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="userEmail">Email (optional)</Label>
            <Input
              id="userEmail"
              type="email"
              value={targetUserEmail}
              onChange={(e) => setTargetUserEmail(e.target.value)}
              placeholder="User's email"
              data-testid="input-dm-user-email"
            />
          </div>
          <Button 
            type="submit" 
            className="w-full" 
            disabled={createThread.isPending}
            data-testid="button-submit-dm"
          >
            {createThread.isPending ? 'Starting...' : 'Start Conversation'}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export function DMThreadList({ selectedThreadId, onSelectThread }: DMThreadListProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const { data: threads, isLoading, error } = useDMThreads();

  const filteredThreads = threads?.filter((thread) => {
    const otherUser = thread.other_user;
    if (!otherUser) return true;
    return (
      otherUser.user_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      otherUser.user_email.toLowerCase().includes(searchQuery.toLowerCase())
    );
  });

  if (error) {
    return (
      <div className="p-4 text-center text-muted-foreground">
        Failed to load conversations
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col border-r">
      <div className="flex items-center justify-between border-b p-3">
        <h2 className="font-semibold">Direct Messages</h2>
        <StartDMDialog onSuccess={onSelectThread} />
      </div>
      
      <div className="p-2">
        <div className="relative">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search conversations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-8"
            data-testid="input-search-dm"
          />
        </div>
      </div>
      
      <ScrollArea className="flex-1">
        <div className="space-y-1 p-2">
          {isLoading ? (
            <div className="space-y-2">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-14 animate-pulse rounded-lg bg-muted" />
              ))}
            </div>
          ) : filteredThreads?.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 text-center text-muted-foreground">
              <MessageSquare className="mb-2 h-8 w-8" />
              <p>No conversations yet</p>
              <p className="text-sm">Start a new conversation above</p>
            </div>
          ) : (
            filteredThreads?.map((thread) => (
              <ThreadItem
                key={thread.id}
                thread={thread}
                isSelected={thread.id === selectedThreadId}
                onSelect={() => onSelectThread(thread.id)}
              />
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
}

function ThreadItem({
  thread,
  isSelected,
  onSelect,
}: {
  thread: DirectMessageThread;
  isSelected: boolean;
  onSelect: () => void;
}) {
  const otherUser = thread.other_user;
  const displayName = otherUser?.user_name || 'Unknown User';
  
  return (
    <button
      onClick={onSelect}
      className={`w-full rounded-lg p-3 text-left transition-colors hover:bg-accent ${
        isSelected ? 'bg-accent' : ''
      }`}
      data-testid={`dm-thread-${thread.id}`}
    >
      <div className="flex items-start gap-3">
        <Avatar className="h-10 w-10">
          <AvatarFallback className="bg-primary/10 text-primary">
            {getInitials(displayName)}
          </AvatarFallback>
        </Avatar>
        <div className="flex-1 overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="font-medium">{displayName}</span>
            {thread.unread_count > 0 && (
              <Badge variant="default" className="ml-2">
                {thread.unread_count}
              </Badge>
            )}
          </div>
          {thread.last_message && (
            <p className="truncate text-sm text-muted-foreground">
              {thread.last_message.content}
            </p>
          )}
          {thread.last_message && (
            <p className="text-xs text-muted-foreground">
              {formatDistanceToNow(new Date(thread.last_message.created_at), { addSuffix: true })}
            </p>
          )}
        </div>
      </div>
    </button>
  );
}
