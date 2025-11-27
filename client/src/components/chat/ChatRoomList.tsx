import { useState } from 'react';
import { Hash, Lock, Users, MessageSquare, Plus, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useChatRooms, useCreateRoom, type ChatRoom } from '@/hooks/use-chat';
import { formatDistanceToNow } from 'date-fns';

interface ChatRoomListProps {
  selectedRoomId: string | null;
  onSelectRoom: (roomId: string) => void;
}

function RoomIcon({ roomType }: { roomType: string }) {
  switch (roomType) {
    case 'private':
      return <Lock className="h-4 w-4" />;
    case 'direct':
      return <MessageSquare className="h-4 w-4" />;
    case 'project':
      return <Users className="h-4 w-4" />;
    default:
      return <Hash className="h-4 w-4" />;
  }
}

function CreateRoomDialog({ onSuccess }: { onSuccess?: () => void }) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [roomType, setRoomType] = useState('public');
  
  const createRoom = useCreateRoom();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createRoom.mutateAsync({
        name,
        description,
        room_type: roomType,
      });
      setOpen(false);
      setName('');
      setDescription('');
      setRoomType('public');
      onSuccess?.();
    } catch (error) {
      console.error('Failed to create room:', error);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon" className="h-8 w-8" data-testid="button-create-room">
          <Plus className="h-4 w-4" />
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create Channel</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Channel Name</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="general"
              required
              data-testid="input-room-name"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="description">Description (optional)</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What's this channel about?"
              data-testid="input-room-description"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="type">Channel Type</Label>
            <Select value={roomType} onValueChange={setRoomType}>
              <SelectTrigger data-testid="select-room-type">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="public">Public</SelectItem>
                <SelectItem value="private">Private</SelectItem>
                <SelectItem value="project">Project</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <Button 
            type="submit" 
            className="w-full" 
            disabled={createRoom.isPending}
            data-testid="button-submit-room"
          >
            {createRoom.isPending ? 'Creating...' : 'Create Channel'}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export function ChatRoomList({ selectedRoomId, onSelectRoom }: ChatRoomListProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const { data: rooms, isLoading, error } = useChatRooms();

  const filteredRooms = rooms?.filter((room) =>
    room.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    room.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (error) {
    return (
      <div className="p-4 text-center text-muted-foreground">
        Failed to load channels
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col border-r">
      <div className="flex items-center justify-between border-b p-3">
        <h2 className="font-semibold">Channels</h2>
        <CreateRoomDialog />
      </div>
      
      <div className="p-2">
        <div className="relative">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search channels..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-8"
            data-testid="input-search-rooms"
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
          ) : filteredRooms?.length === 0 ? (
            <div className="p-4 text-center text-muted-foreground">
              No channels found
            </div>
          ) : (
            filteredRooms?.map((room) => (
              <RoomItem
                key={room.id}
                room={room}
                isSelected={room.id === selectedRoomId}
                onSelect={() => onSelectRoom(room.id)}
              />
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
}

function RoomItem({
  room,
  isSelected,
  onSelect,
}: {
  room: ChatRoom;
  isSelected: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      onClick={onSelect}
      className={`w-full rounded-lg p-3 text-left transition-colors hover:bg-accent ${
        isSelected ? 'bg-accent' : ''
      }`}
      data-testid={`room-item-${room.id}`}
    >
      <div className="flex items-start gap-3">
        <div className="mt-0.5 text-muted-foreground">
          <RoomIcon roomType={room.room_type} />
        </div>
        <div className="flex-1 overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="font-medium">{room.name}</span>
            {room.unread_count > 0 && (
              <Badge variant="default" className="ml-2">
                {room.unread_count}
              </Badge>
            )}
          </div>
          {room.last_message && (
            <p className="truncate text-sm text-muted-foreground">
              <span className="font-medium">{room.last_message.sender_name}:</span>{' '}
              {room.last_message.content}
            </p>
          )}
          {room.last_message && (
            <p className="text-xs text-muted-foreground">
              {formatDistanceToNow(new Date(room.last_message.created_at), { addSuffix: true })}
            </p>
          )}
        </div>
      </div>
    </button>
  );
}
