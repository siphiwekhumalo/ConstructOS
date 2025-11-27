import { useState, useEffect } from 'react';
import { useLocation } from 'wouter';
import { Hash, MessageSquare } from 'lucide-react';
import { DashboardLayout } from '@/components/dashboard-layout';
import { ChatRoomList } from '@/components/chat/ChatRoomList';
import { ChatMessagePane } from '@/components/chat/ChatMessagePane';
import { DMThreadList } from '@/components/chat/DMThreadList';
import { DMMessagePane } from '@/components/chat/DMMessagePane';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useAuth } from '@/hooks/use-auth';

type ChatMode = 'channels' | 'dm';

export default function ChatPage() {
  const [chatMode, setChatMode] = useState<ChatMode>('channels');
  const [selectedRoomId, setSelectedRoomId] = useState<string | null>(null);
  const [selectedThreadId, setSelectedThreadId] = useState<string | null>(null);
  const [location] = useLocation();
  const { user } = useAuth();

  const userId = (user as any)?.localAccountId || (user as any)?.id || 'demo-user';
  const userName = (user as any)?.name || (user as any)?.full_name || 'Demo User';
  const userEmail = (user as any)?.username || (user as any)?.email || 'demo@constructos.co.za';

  useEffect(() => {
    const params = new URLSearchParams(location.split('?')[1] || '');
    const roomParam = params.get('room');
    const dmParam = params.get('dm');
    
    if (dmParam) {
      setChatMode('dm');
      setSelectedThreadId(dmParam);
    } else if (roomParam) {
      setChatMode('channels');
      setSelectedRoomId(roomParam);
    }
  }, [location]);

  return (
    <DashboardLayout>
      <div className="flex h-[calc(100vh-10rem)] -mx-6 md:-mx-8 -mt-6 md:-mt-8" data-testid="chat-page">
        <div className="w-72 flex-shrink-0 flex flex-col border-r">
          <div className="p-2 border-b">
            <Tabs value={chatMode} onValueChange={(v) => setChatMode(v as ChatMode)}>
              <TabsList className="w-full">
                <TabsTrigger value="channels" className="flex-1 gap-1" data-testid="tab-channels">
                  <Hash className="h-4 w-4" />
                  Channels
                </TabsTrigger>
                <TabsTrigger value="dm" className="flex-1 gap-1" data-testid="tab-dm">
                  <MessageSquare className="h-4 w-4" />
                  DMs
                </TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
          
          <div className="flex-1 overflow-hidden">
            {chatMode === 'channels' ? (
              <ChatRoomList
                selectedRoomId={selectedRoomId}
                onSelectRoom={setSelectedRoomId}
              />
            ) : (
              <DMThreadList
                selectedThreadId={selectedThreadId}
                onSelectThread={setSelectedThreadId}
              />
            )}
          </div>
        </div>
        
        <div className="flex-1">
          {chatMode === 'channels' ? (
            <ChatMessagePane
              roomId={selectedRoomId}
              userId={userId}
              userName={userName}
              userEmail={userEmail}
            />
          ) : (
            <DMMessagePane
              threadId={selectedThreadId}
              userId={userId}
              userName={userName}
              userEmail={userEmail}
            />
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
