import { useState, useEffect, useRef } from 'react';
import { MessageSquare, Send, X, Bot, Mic, Volume2, Loader2 } from 'lucide-react';
import { chatAPI, voiceAPI } from '../services/api';

const ChatAssistant = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [language, setLanguage] = useState('English');
  const [chatLog, setChatLog] = useState([
    { role: 'assistant', content: '🙏 Namaste! I am Vaani, your SHG Marketplace Assistant.\n\nI can help you with:\n\n🛒 **Selling Products** - List & price your items\n📦 **Finding Buyers** - Connect with verified buyers\n💰 **Market Pricing** - Get competitive price insights\n🏭 **Raw Materials** - Source quality supplies\n⭐ **Trust Scores** - Improve your marketplace reputation\n📝 **Orders** - Track & manage deliveries\n\nWhat would you like help with today?' }
  ]);
  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);
  const [currentResponse, setCurrentResponse] = useState('');
  const [streaming, setStreaming] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    if (bottomRef.current) bottomRef.current.scrollIntoView({ behavior: 'smooth' });
  }, [chatLog, currentResponse, isOpen]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!message.trim() || loading) return;
    const userMsg = message;
    setMessage('');
    setChatLog(prev => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true); setStreaming(true); setCurrentResponse('');

    try {
      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const token = localStorage.getItem('token');
      const eventSource = new EventSource(
        `${API_BASE_URL}/api/chat/stream?query=${encodeURIComponent(userMsg)}&language=${language}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      let fullResponse = '';
      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.error) {
          setChatLog(prev => [...prev, { role: 'assistant', content: 'Error: ' + data.error }]);
          setStreaming(false); setLoading(false); eventSource.close(); return;
        }
        if (data.content) { fullResponse += data.content; setCurrentResponse(fullResponse); }
        if (data.done) {
          setChatLog(prev => [...prev, { role: 'assistant', content: fullResponse, agent: 'VAANI' }]);
          setCurrentResponse(''); setStreaming(false); setLoading(false); eventSource.close();
        }
      };
      eventSource.onerror = async () => {
        eventSource.close();
        try {
          const res = await chatAPI.sendMessage(userMsg, language);
          setChatLog(prev => [...prev, { role: 'assistant', content: res.data.reply || res.data.response, agent: res.data.agent_triggered || res.data.agent_used }]);
        } catch { setChatLog(prev => [...prev, { role: 'assistant', content: 'Connection failed. Please try again later.' }]); }
        finally { setCurrentResponse(''); setStreaming(false); setLoading(false); }
      };
    } catch {
      try {
        const res = await chatAPI.sendMessage(userMsg, language);
        setChatLog(prev => [...prev, { role: 'assistant', content: res.data.reply || res.data.response, agent: res.data.agent_triggered || res.data.agent_used }]);
      } catch { setChatLog(prev => [...prev, { role: 'assistant', content: 'Connection failed. Please try again later.' }]); }
      finally { setCurrentResponse(''); setStreaming(false); setLoading(false); }
    }
  };

  const handleVoiceInput = async () => {
    if (recording) return;
    try {
      setRecording(true);
      alert('Recording... Speak now!');
      setTimeout(async () => {
        try {
          const response = await voiceAPI.transcribe('');
          if (response.data.transcript) setMessage(response.data.transcript);
        } catch { console.error('Voice transcription failed'); }
        finally { setRecording(false); }
      }, 2000);
    } catch { setRecording(false); }
  };

  const handleVoicePlayback = async (text) => {
    try {
      const response = await voiceAPI.synthesize(text, language);
      if (response.data.audio_url) new Audio(response.data.audio_url).play();
    } catch { console.error('Voice playback failed'); }
  };

  const FAB_BOTTOM = 90; // above bottom nav

  return (
    <>
      {/* FAB */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          style={{
            position: 'fixed', bottom: FAB_BOTTOM, right: 20,
            width: 58, height: 58,
            background: 'linear-gradient(135deg, #7c3aed 0%, #a855f7 100%)',
            borderRadius: '50%',
            border: 'none',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            cursor: 'pointer',
            boxShadow: '0 0 25px rgba(139,92,246,0.55), 0 8px 25px rgba(0,0,0,0.4)',
            color: '#fff',
            zIndex: 60,
            transition: 'all 0.3s',
          }}
          onMouseEnter={e => {
            e.currentTarget.style.transform = 'scale(1.1)';
            e.currentTarget.style.boxShadow = '0 0 35px rgba(139,92,246,0.7), 0 8px 25px rgba(0,0,0,0.4)';
          }}
          onMouseLeave={e => {
            e.currentTarget.style.transform = 'scale(1)';
            e.currentTarget.style.boxShadow = '0 0 25px rgba(139,92,246,0.55), 0 8px 25px rgba(0,0,0,0.4)';
          }}
        >
          <MessageSquare size={26} />
        </button>
      )}

      {/* Chat Panel */}
      {isOpen && (
        <div
          className="animate-scale-in"
          style={{
            position: 'fixed', bottom: FAB_BOTTOM, right: 16,
            width: 380, height: 580,
            background: 'rgba(10, 7, 18, 0.95)',
            border: '1px solid rgba(139,92,246,0.3)',
            borderRadius: '1.5rem',
            backdropFilter: 'blur(24px)',
            WebkitBackdropFilter: 'blur(24px)',
            boxShadow: '0 30px 70px rgba(0,0,0,0.7), 0 0 40px rgba(139,92,246,0.12)',
            display: 'flex', flexDirection: 'column',
            zIndex: 60, overflow: 'hidden',
          }}
        >
          {/* Header */}
          <div style={{
            background: 'linear-gradient(135deg, rgba(124,58,237,0.35) 0%, rgba(168,85,247,0.25) 100%)',
            borderBottom: '1px solid rgba(139,92,246,0.25)',
            padding: '1rem 1.25rem',
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{
                width: 38, height: 38, borderRadius: '50%',
                background: 'rgba(139,92,246,0.25)',
                border: '1px solid rgba(139,92,246,0.4)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <Bot size={20} style={{ color: '#c4b5fd' }} />
              </div>
              <div>
                <h3 style={{ fontWeight: 700, color: '#f8fafc', fontSize: '0.95rem', margin: 0 }}>Agent Vaani</h3>
                <p style={{ fontSize: '0.72rem', color: '#a78bfa', margin: 0, fontWeight: 500 }}>Multilingual AI Assistant</p>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                style={{
                  background: 'rgba(139,92,246,0.15)',
                  border: '1px solid rgba(139,92,246,0.25)',
                  color: '#c4b5fd', fontSize: '0.75rem',
                  borderRadius: 6, padding: '3px 6px', outline: 'none', cursor: 'pointer',
                }}
              >
                <option value="English">English</option>
                <option value="Hindi">हिंदी</option>
                <option value="Telugu">తెలుగు</option>
                <option value="Tamil">தமிழ்</option>
              </select>
              <button
                onClick={() => setIsOpen(false)}
                style={{
                  padding: 4, border: 'none', borderRadius: 6,
                  background: 'rgba(255,255,255,0.08)',
                  color: '#94a3b8', cursor: 'pointer', display: 'flex',
                }}
              >
                <X size={18} />
              </button>
            </div>
          </div>

          {/* Messages */}
          <div style={{
            flex: 1, overflowY: 'auto', padding: '1rem',
            display: 'flex', flexDirection: 'column', gap: '0.75rem',
          }}>
            {/* Quick prompts */}
            {chatLog.length === 1 && (
              <div style={{ marginBottom: 8 }}>
                <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: 6 }}>
                  💡 Quick Questions:
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
                  {[
                    'How do I sell my products?',
                    'Find buyers for handicrafts',
                    "What's the market price for textiles?",
                    'How to improve my trust score?',
                    'Where to get raw materials?',
                  ].map((q, idx) => (
                    <button
                      key={idx}
                      onClick={() => setMessage(q)}
                      style={{
                        textAlign: 'left', fontSize: '0.78rem',
                        background: 'rgba(139,92,246,0.08)',
                        border: '1px solid rgba(139,92,246,0.18)',
                        color: 'var(--text-secondary)',
                        padding: '6px 10px', borderRadius: 8,
                        cursor: 'pointer', transition: 'all 0.2s',
                      }}
                      onMouseEnter={e => {
                        e.currentTarget.style.background = 'rgba(139,92,246,0.15)';
                        e.currentTarget.style.color = '#c4b5fd';
                        e.currentTarget.style.borderColor = 'rgba(139,92,246,0.35)';
                      }}
                      onMouseLeave={e => {
                        e.currentTarget.style.background = 'rgba(139,92,246,0.08)';
                        e.currentTarget.style.color = 'var(--text-secondary)';
                        e.currentTarget.style.borderColor = 'rgba(139,92,246,0.18)';
                      }}
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {chatLog.map((msg, idx) => (
              <div key={idx} style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                <div style={{
                  maxWidth: '85%', padding: '0.7rem 0.9rem',
                  borderRadius: msg.role === 'user' ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                  background: msg.role === 'user'
                    ? 'linear-gradient(135deg, #7c3aed 0%, #a855f7 100%)'
                    : 'rgba(255,255,255,0.06)',
                  border: msg.role === 'user'
                    ? 'none'
                    : '1px solid rgba(139,92,246,0.18)',
                  fontSize: '0.85rem', lineHeight: 1.55,
                  color: msg.role === 'user' ? '#fff' : 'var(--text-secondary)',
                  boxShadow: msg.role === 'user'
                    ? '0 4px 15px rgba(139,92,246,0.3)'
                    : '0 2px 8px rgba(0,0,0,0.3)',
                }}>
                  {msg.agent && (
                    <div style={{ fontSize: '0.68rem', fontWeight: 700, color: '#a78bfa', marginBottom: 4 }}>
                      🤖 {msg.agent}
                    </div>
                  )}
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
                    <div style={{ flex: 1, whiteSpace: 'pre-line' }}>{msg.content}</div>
                    {msg.role === 'assistant' && (
                      <button
                        onClick={() => handleVoicePlayback(msg.content)}
                        style={{ flexShrink: 0, padding: 3, border: 'none', background: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}
                        title="Listen"
                      >
                        <Volume2 size={14} />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {streaming && currentResponse && (
              <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                <div style={{
                  maxWidth: '85%', padding: '0.7rem 0.9rem',
                  background: 'rgba(255,255,255,0.06)',
                  border: '1px solid rgba(139,92,246,0.18)',
                  borderRadius: '16px 16px 16px 4px',
                  fontSize: '0.85rem', color: 'var(--text-secondary)',
                }}>
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
                    <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#8b5cf6', flexShrink: 0, marginTop: 4, animation: 'glowPulse 1s ease-in-out infinite' }} />
                    <div style={{ whiteSpace: 'pre-line' }}>{currentResponse}</div>
                  </div>
                </div>
              </div>
            )}

            {loading && !currentResponse && (
              <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                <div style={{
                  padding: '0.65rem 1rem',
                  background: 'rgba(255,255,255,0.05)',
                  border: '1px solid rgba(139,92,246,0.15)',
                  borderRadius: '16px 16px 16px 4px',
                  display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-muted)', fontSize: '0.8rem',
                }}>
                  <Loader2 size={14} style={{ animation: 'spin 0.7s linear infinite', color: '#8b5cf6' }} />
                  Vaani is thinking...
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input Bar */}
          <form
            onSubmit={handleSend}
            style={{
              padding: '0.75rem 1rem',
              borderTop: '1px solid rgba(139,92,246,0.15)',
              background: 'rgba(0,0,0,0.3)',
              display: 'flex', alignItems: 'center', gap: 8,
            }}
          >
            <button
              type="button"
              onClick={handleVoiceInput}
              disabled={recording}
              style={{
                width: 38, height: 38, borderRadius: '50%', border: 'none',
                background: recording ? 'rgba(239,68,68,0.2)' : 'rgba(255,255,255,0.06)',
                color: recording ? '#fca5a5' : 'var(--text-muted)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                cursor: 'pointer', flexShrink: 0,
                border: `1px solid ${recording ? 'rgba(239,68,68,0.3)' : 'rgba(139,92,246,0.15)'}`,
              }}
            >
              <Mic size={16} />
            </button>

            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message..."
              style={{
                flex: 1, padding: '0.6rem 1rem',
                background: 'rgba(255,255,255,0.06)',
                border: '1px solid rgba(139,92,246,0.2)',
                borderRadius: 99, outline: 'none',
                color: 'var(--text-primary)', fontSize: '0.875rem',
                transition: 'all 0.2s',
              }}
              onFocus={e => {
                e.target.style.borderColor = '#8b5cf6';
                e.target.style.boxShadow = '0 0 0 3px rgba(139,92,246,0.1)';
              }}
              onBlur={e => {
                e.target.style.borderColor = 'rgba(139,92,246,0.2)';
                e.target.style.boxShadow = 'none';
              }}
            />

            <button
              type="submit"
              disabled={loading || !message.trim()}
              style={{
                width: 38, height: 38, borderRadius: '50%', border: 'none',
                background: !loading && message.trim()
                  ? 'linear-gradient(135deg, #7c3aed, #a855f7)'
                  : 'rgba(255,255,255,0.06)',
                color: !loading && message.trim() ? '#fff' : 'var(--text-muted)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                cursor: loading || !message.trim() ? 'not-allowed' : 'pointer',
                flexShrink: 0,
                boxShadow: !loading && message.trim() ? '0 4px 12px rgba(139,92,246,0.35)' : 'none',
                transition: 'all 0.2s',
              }}
            >
              <Send size={16} style={{ marginLeft: 1 }} />
            </button>
          </form>
        </div>
      )}
    </>
  );
};

export default ChatAssistant;
