import { useState, useEffect, useCallback } from 'react';
import offlineManager from '../utils/offlineManager';

function OfflineIndicator({ compact = false }) {
  const [isOnline, setIsOnline] = useState(offlineManager.isOnline());
  const [queueCount, setQueueCount] = useState(offlineManager.getQueueCount());
  const [isSyncing, setIsSyncing] = useState(false);

  useEffect(() => {
    const handleOnline    = () => setIsOnline(true);
    const handleOffline   = () => setIsOnline(false);
    const handleQueue     = (e) => setQueueCount(e.detail.queue.length);
    const handleSyncStart = () => setIsSyncing(true);
    const handleSyncDone  = () => { setIsSyncing(false); setQueueCount(offlineManager.getQueueCount()); };

    window.addEventListener('app:online', handleOnline);
    window.addEventListener('app:offline', handleOffline);
    window.addEventListener('queue:updated', handleQueue);
    window.addEventListener('sync:start', handleSyncStart);
    window.addEventListener('sync:complete', handleSyncDone);
    return () => {
      window.removeEventListener('app:online', handleOnline);
      window.removeEventListener('app:offline', handleOffline);
      window.removeEventListener('queue:updated', handleQueue);
      window.removeEventListener('sync:start', handleSyncStart);
      window.removeEventListener('sync:complete', handleSyncDone);
    };
  }, []);

  const handleSync = useCallback(async () => {
    if (!isOnline || isSyncing) return;
    await offlineManager.processQueue();
  }, [isOnline, isSyncing]);

  if (isOnline && queueCount === 0) return null;

  const statusColor = isSyncing ? '#10b981' : !isOnline ? '#f59e0b' : '#f59e0b';
  const statusText  = isSyncing ? 'Syncing...' : !isOnline ? 'You are offline' : 'Pending sync';
  const bgColor = isSyncing ? 'rgba(16,185,129,0.12)' : 'rgba(245,158,11,0.12)';
  const borderColor = isSyncing ? 'rgba(16,185,129,0.3)' : 'rgba(245,158,11,0.3)';

  if (compact) return (
    <span style={{ display:'inline-flex', alignItems:'center', gap:5, padding:'3px 10px', background:bgColor, border:`1px solid ${borderColor}`, borderRadius:99, fontSize:'0.72rem', fontWeight:700, color:statusColor }}>
      <span style={{ width:6, height:6, borderRadius:'50%', background:statusColor, animation:isSyncing?'ping 0.9s ease-out infinite':'none' }}/>
      {statusText}{queueCount>0 ? ` (${queueCount})` : ''}
    </span>
  );

  return (
    <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', padding:'0.7rem 1.25rem', background:bgColor, borderBottom:`1px solid ${borderColor}` }}>
      <div style={{ display:'flex', alignItems:'center', gap:10 }}>
        <div style={{ width:10, height:10, borderRadius:'50%', background:statusColor, animation:isSyncing?'ping 0.9s ease-out infinite':'none' }}/>
        <span style={{ fontWeight:600, color:statusColor, fontSize:'0.875rem' }}>{statusText}</span>
        {queueCount>0 && <span style={{ fontSize:'0.8rem', color:'var(--text-muted)' }}>{queueCount} action{queueCount!==1?'s':''} pending</span>}
      </div>
      {queueCount>0 && isOnline && (
        <button onClick={handleSync} disabled={isSyncing} style={{ padding:'4px 14px', background:'rgba(255,255,255,0.08)', border:'1px solid rgba(255,255,255,0.15)', borderRadius:8, color:'var(--text-secondary)', fontWeight:600, fontSize:'0.8rem', cursor:isSyncing?'not-allowed':'pointer', opacity:isSyncing?0.6:1 }}>
          {isSyncing ? 'Syncing...' : 'Sync Now'}
        </button>
      )}
    </div>
  );
}

export default OfflineIndicator;
