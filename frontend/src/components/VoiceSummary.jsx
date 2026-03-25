import { useState, useEffect, useCallback, useRef } from 'react';
import { Volume2, VolumeX, Pause, Play } from 'lucide-react';

const VoiceSummary = ({ text, autoPlay = false, onEnd, onError }) => {
  const language = 'en-US';
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isSupported, setIsSupported] = useState(true);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const progressIntervalRef = useRef(null);

  const stop = useCallback(() => {
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    if (progressIntervalRef.current) clearInterval(progressIntervalRef.current);
    setIsPlaying(false); setIsPaused(false); setIsSpeaking(false); setProgress(0);
  }, []);

  const speak = useCallback(() => {
    if (!('speechSynthesis' in window) || !text) { setIsSupported(false); return; }
    stop();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = language; u.rate = 0.95; u.pitch = 1.1;
    let start = Date.now();
    const dur = (text.split(' ').length / 150) * 60 * 1000;
    u.onstart = () => {
      setIsSpeaking(true); setIsPlaying(true); setIsPaused(false); start = Date.now();
      progressIntervalRef.current = setInterval(() => { const elapsed = Date.now() - start; setProgress(Math.min((elapsed/dur)*100, 100)); }, 100);
    };
    u.onend = () => { if (progressIntervalRef.current) clearInterval(progressIntervalRef.current); setProgress(100); setIsPlaying(false); setIsSpeaking(false); if (onEnd) onEnd(); };
    u.onerror = (e) => { if (progressIntervalRef.current) clearInterval(progressIntervalRef.current); setIsPlaying(false); if (onError) onError(e.error); };
    window.speechSynthesis.speak(u);
  }, [text, stop, onEnd, onError]);

  const toggle = () => {
    if (isSpeaking && !isPaused) { window.speechSynthesis.pause(); setIsPaused(true); }
    else if (isPaused) { window.speechSynthesis.resume(); setIsPaused(false); }
    else speak();
  };

  useEffect(() => { if (autoPlay && text) speak(); return () => stop(); }, [autoPlay, text, speak, stop]);

  return (
    <div style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: '1rem', padding: '1rem', display: 'flex', alignItems: 'center', gap: 15, backdropFilter: 'blur(10px)' }}>
      <button onClick={toggle} style={{ width: 50, height: 50, borderRadius: '50%', background: isPlaying && !isPaused ? 'linear-gradient(135deg,#7c3aed,#a855f7)' : 'rgba(139,92,246,0.15)', border: '1px solid rgba(139,92,246,0.3)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', transition: 'all 0.2s', boxShadow: isPlaying && !isPaused ? '0 0 15px rgba(139,92,246,0.5)' : 'none' }}>
        {isSpeaking && !isPaused ? <Pause size={22} fill="#fff" /> : <Play size={22} fill="#fff" style={{ marginLeft: 3 }} />}
      </button>
      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
          <Volume2 size={14} style={{ color: '#a78bfa' }} />
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>{isSpeaking && !isPaused ? 'Voice Summary Playing' : 'Listen with Agent Vaani'}</span>
        </div>
        <div style={{ height: 4, background: 'rgba(255,255,255,0.06)', borderRadius: 2, overflow: 'hidden' }}>
          <div style={{ height: '100%', width: `${progress}%`, background: 'linear-gradient(90deg,#7c3aed,#a855f7)', transition: 'width 0.1s linear' }} />
        </div>
      </div>
      <button onClick={stop} disabled={!isPlaying} style={{ width: 36, height: 36, borderRadius: '50%', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', opacity: isPlaying ? 1 : 0.4 }}><VolumeX size={18} /></button>
    </div>
  );
};

export default VoiceSummary;
