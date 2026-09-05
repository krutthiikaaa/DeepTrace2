import React, { useEffect, useState } from 'react';
import { checkHealth } from '../services/api';
import { Activity, XCircle, CheckCircle2 } from 'lucide-react';

const BackendStatus: React.FC = () => {
  const [status, setStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    const ping = async () => {
      try {
        const data = await checkHealth();
        if (data.status === 'ok') {
          setStatus('online');
        } else {
          setStatus('offline');
        }
      } catch (err) {
        setStatus('offline');
      }
    };
    
    ping();
  }, []);

  if (status === 'checking') {
    return (
      <div className="status-indicator checking">
        <Activity size={16} />
        <span>Checking backend...</span>
      </div>
    );
  }

  if (status === 'offline') {
    return (
      <div className="status-indicator offline">
        <XCircle size={16} />
        <span>Backend Offline</span>
      </div>
    );
  }

  return (
    <div className="status-indicator online">
      <CheckCircle2 size={16} />
      <span>Backend Connected</span>
    </div>
  );
};

export default BackendStatus;
