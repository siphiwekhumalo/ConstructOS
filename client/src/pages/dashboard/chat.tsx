import { useState, useEffect } from 'react';
import { useLocation } from 'wouter';
import { DashboardLayout } from '@/components/dashboard-layout';
import { ChatRoomList } from '@/components/chat/ChatRoomList';
import { ChatMessagePane } from '@/components/chat/ChatMessagePane';
import { useAuth } from '@/hooks/use-auth';

export default function ChatPage() {
  const [selectedRoomId, setSelectedRoomId] = useState<string | null>(null);
  const [location] = useLocation();
  const { user } = useAuth();

  const userId = user?.localAccountId || 'demo-user';
  const userName = user?.name || 'Demo User';
  const userEmail = user?.username || 'demo@constructos.co.za';

  useEffect(() => {
    const params = new URLSearchParams(location.split('?')[1] || '');
    const roomParam = params.get('room');
    if (roomParam) {
      setSelectedRoomId(roomParam);
    }
  }, [location]);

  return (
    <DashboardLayout>
      <div className="flex h-[calc(100vh-10rem)] -mx-6 md:-mx-8 -mt-6 md:-mt-8" data-testid="chat-page">
        <div className="w-72 flex-shrink-0">
          <ChatRoomList
            selectedRoomId={selectedRoomId}
            onSelectRoom={setSelectedRoomId}
          />
        </div>
        
        <div className="flex-1">
          <ChatMessagePane
            roomId={selectedRoomId}
            userId={userId}
            userName={userName}
            userEmail={userEmail}
          />
        </div>
      </div>
    </DashboardLayout>
  );
}
