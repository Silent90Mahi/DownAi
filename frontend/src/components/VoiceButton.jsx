import { useState, useRef, useCallback } from 'react';
import { Mic, MicOff } from 'lucide-react';

const VoiceButton = ({ onResult, disabled = false, className = '' }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState(null);
  const mrRef = useRef(null);
  const chunksRef = useRef([]);
  const streamRef = useRef(null);

  const start = useCallback(async () => {
    if (disabled) return;
    setError(null); chunksRef.current = [];
    try {
      const s = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = s;
      const mr = new MediaRecorder(s, { mimeType: MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/mp4' });
      mrRef.current = mr;
      mr.ondataavailable = (e) => { if (e.data.size > 0) chunksRef.current.push(e.data); };
      mr.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: mr.mimeType });
        if (onResult) onResult({ blob, language: 'English', mimeType: mr.mimeType });
        if (streamRef.current) { streamRef.current.getTracks().forEach(t => t.stop()); streamRef.current = null; }
      };
      mr.start(100); setIsRecording(true);
    } catch (err) { setError('Mic access denied'); setIsRecording(false); }
  }, [disabled, onResult]);

  const stop = useCallback(() => { if (mrRef.current && isRecording) { mrRef.current.stop(); setIsRecording(false); } }, [isRecording]);

  return (
    <div style={{ position: 'relative', display: 'inline-flex', flexDirection: 'column', alignItems: 'center' }}>
      <button
        onClick={() => isRecording ? stop() : start()}
        disabled={disabled}
        aria-label={isRecording ? 'Stop' : 'Start'}
        style={{ width: 56, height: 56, borderRadius: '50%', background: isRecording ? '#ef4444' : 'linear-gradient(135deg,#7c3aed,#a855f7)', border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', cursor: 'pointer', transition: 'all 0.3s', boxShadow: isRecording ? '0 0 20px rgba(239,68,68,0.4)' : '0 4px 12px rgba(139,92,246,0.3)', zIndex: 2 }}
        onMouseEnter={e => e.currentTarget.style.transform = 'scale(1.05)'}
        onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}
      >
        {isRecording && <span style={{ position: 'absolute', inset: 0, borderRadius: '50%', background: '#ef4444', animation: 'ping 1s cubic-bezier(0,0,0.2,1) infinite', opacity: 0.6 }} />}
        {isRecording ? <Mic size={24} className="animate-pulse" /> : <Mic size={24} />}
      </button>
      {isRecording && <span style={{ position: 'absolute', bottom: -24, fontSize: '0.7rem', fontWeight: 700, color: '#fca5a5', whiteSpace: 'nowrap' }}>Listening...</span>}
      {error && !isRecording && <span style={{ position: 'absolute', bottom: -24, fontSize: '0.7rem', color: '#fca5a5' }}>Deny</span>}
    </div>
  );
};

export default VoiceButton;
