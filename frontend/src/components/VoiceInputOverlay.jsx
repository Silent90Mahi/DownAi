import { useState, useRef, useEffect, useCallback } from 'react';
import { Mic, MicOff, X, Check } from 'lucide-react';

const glass = { background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: '1.5rem', backdropFilter: 'blur(24px)', WebkitBackdropFilter: 'blur(24px)' };

const VoiceInputOverlay = ({ isOpen, onClose, onConfirm, placeholder = 'Speak now...' }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState(null);
  const [audioLevel, setAudioLevel] = useState(0);
  const [hasAudioData, setHasAudioData] = useState(false);
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const streamRef = useRef(null);
  const audioChunksRef = useRef([]);
  const prevIsOpenRef = useRef(false);

  const drawWaveform = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || !analyserRef.current) return;
    const ctx = canvas.getContext('2d');
    const analyser = analyserRef.current;
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    const draw = () => {
      if (!isRecording) return;
      animationRef.current = requestAnimationFrame(draw);
      analyser.getByteTimeDomainData(dataArray);
      const maxLevel = Math.max(...dataArray);
      const minLevel = Math.min(...dataArray);
      setAudioLevel((maxLevel - minLevel) / 255);
      ctx.fillStyle = 'rgba(10, 7, 18, 0.2)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.lineWidth = 3;
      ctx.strokeStyle = '#a855f7';
      ctx.beginPath();
      const sliceWidth = canvas.width / bufferLength;
      let x = 0;
      for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128.0;
        const y = (v * canvas.height) / 2;
        if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        x += sliceWidth;
      }
      ctx.lineTo(canvas.width, canvas.height / 2);
      ctx.stroke();
    };
    draw();
  }, [isRecording]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
      if (streamRef.current) { streamRef.current.getTracks().forEach(t => t.stop()); streamRef.current = null; }
      if (audioContextRef.current) { audioContextRef.current.close(); audioContextRef.current = null; }
    }
  }, [isRecording]);

  const startRecording = useCallback(async () => {
    setHasAudioData(false); audioChunksRef.current = [];
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      analyserRef.current = audioContextRef.current.createAnalyser();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      analyserRef.current.fftSize = 2048;
      const mr = new MediaRecorder(stream, { mimeType: MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/mp4' });
      mediaRecorderRef.current = mr;
      mr.ondataavailable = (e) => { if (e.data.size > 0) { audioChunksRef.current.push(e.data); setHasAudioData(true); } };
      mr.start(100); setIsRecording(true);
    } catch (err) { setError(err.message || 'Microphone denied'); }
  }, []);

  useEffect(() => {
    if (isOpen && !prevIsOpenRef.current) { setTranscript(''); setError(null); setAudioLevel(0); startRecording(); }
    else if (!isOpen && prevIsOpenRef.current) { stopRecording(); }
    prevIsOpenRef.current = isOpen;
  }, [isOpen, startRecording, stopRecording]);

  useEffect(() => { if (isRecording) drawWaveform(); }, [isRecording, drawWaveform]);

  if (!isOpen) return null;

  return (
    <div className="animate-fade-in" style={{ position: 'fixed', inset: 0, zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem' }}>
      <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(5px)' }} onClick={onClose} />
      <div style={{ ...glass, maxWidth: 450, width: '100%', overflow: 'hidden', position: 'relative', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.8)' }}>
        {/* Header */}
        <div style={{ background: 'linear-gradient(135deg, #7c3aed, #a855f7)', padding: '1.25rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ width: 40, height: 40, borderRadius: '50%', background: isRecording ? 'rgba(239,68,68,0.3)' : 'rgba(255,255,255,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {isRecording ? <Mic size={20} className="animate-pulse" color="#fff" /> : <Mic size={20} color="#fff" />}
            </div>
            <div>
              <p style={{ fontWeight: 800, color: '#fff', margin: 0, fontSize: '0.95rem' }}>Agent Vaani listening</p>
              <p style={{ fontSize: '0.72rem', color: 'rgba(255,255,255,0.8)', margin: 0 }}>{isRecording ? 'Listening for your input...' : 'Ready'}</p>
            </div>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer', padding: 5 }}><X size={22} /></button>
        </div>
        {/* Body */}
        <div style={{ padding: '1.5rem' }}>
          <div style={{ position: 'relative', marginBottom: '1.25rem' }}>
            <canvas ref={canvasRef} width={400} height={120} style={{ width: '100%', height: 120, borderRadius: 12, background: 'rgba(0,0,0,0.3)', border: '1px solid rgba(139,92,246,0.15)' }} />
            {isRecording && <div style={{ position: 'absolute', inset: 0, borderRadius: 12, border: '2px solid #a855f7', opacity: 0.2 + audioLevel, pointerEvents: 'none' }} />}
          </div>
          <div style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 12, padding: '1rem', minHeight: 80, marginBottom: '1.5rem' }}>
            {transcript ? <p style={{ color: '#fff', fontSize: '1.1rem', margin: 0 }}>{transcript}</p> : <p style={{ color: 'var(--text-muted)', fontSize: '1rem', fontStyle: 'italic', margin: 0 }}>{placeholder}</p>}
          </div>
          {error && <p style={{ color: '#fca5a5', fontSize: '0.8rem', textAlign: 'center', marginBottom: '1rem' }}>{error}</p>}
          <div style={{ display: 'flex', gap: 10 }}>
            <button onClick={onClose} style={{ flex: 1, padding: '0.75rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10, color: 'var(--text-muted)', fontWeight: 700, cursor: 'pointer' }}>Cancel</button>
            <button onClick={() => onConfirm({ transcript, audioBlob: hasAudioData ? new Blob(audioChunksRef.current, { type: 'audio/webm' }) : null })} disabled={!hasAudioData && !transcript} style={{ flex: 1, padding: '0.75rem', background: 'linear-gradient(135deg,#7c3aed,#a855f7)', border: 'none', borderRadius: 10, color: '#fff', fontWeight: 800, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, opacity: (!hasAudioData && !transcript) ? 0.5 : 1 }}>
              <Check size={18} /> Confirm
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VoiceInputOverlay;
