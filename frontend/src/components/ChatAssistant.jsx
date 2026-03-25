import { useState, useEffect, useRef } from 'react';
import { MessageSquare, Send, X, Bot, Mic, Volume2, Loader2, ChevronLeft, History, Sparkles, ShoppingCart, TrendingUp, Users, Heart, Wallet, HelpCircle, Package } from 'lucide-react';
import { chatAPI, voiceAPI } from '../services/api';

const AGENTS = [
  { id: 'VAANI', name: 'Vaani', title: 'General Assistant', icon: Bot, color: '#8b5cf6', description: 'General help & guidance' },
  { id: 'BAZAAR', name: 'Market Expert', title: 'Market Intelligence', icon: TrendingUp, color: '#10b981', description: 'Market analysis & pricing' },
  { id: 'JODI', name: 'Order Assistant', title: 'Order Management', icon: Package, color: '#f59e0b', description: 'Orders & deliveries' },
  { id: 'SAMAGRI', name: 'Supplier Advisor', title: 'Supplier Network', icon: Users, color: '#06b6d4', description: 'Raw materials & suppliers' },
  { id: 'SAMPARK', name: 'Community Guide', title: 'Community Hub', icon: Heart, color: '#ec4899', description: 'Community & federation' },
  { id: 'VISHWAS', name: 'Finance Assistant', title: 'Wallet & Payments', icon: Wallet, color: '#f97316', description: 'Trust coins & payments' },
  { id: 'SUPPORT', name: 'Support Bot', title: 'General Support', icon: HelpCircle, color: '#6366f1', description: 'App help & troubleshooting' },
];

const AGENT_SUGGESTIONS = {
  'VAANI': ['How do I sell my products?', 'What can you help me with?', 'How to improve my trust score?'],
  'BAZAAR': ['What is the market price for textiles?', 'Show me demand trends', 'What products are trending?'],
  'JODI': ['Track my recent order', 'How to cancel an order?', 'Update delivery address'],
  'SAMAGRI': ['Find raw material suppliers', 'Compare supplier prices', 'Join bulk purchase request'],
  'SAMPARK': ['Show my federation hierarchy', 'How to post in community?', 'Find peer SHGs'],
  'VISHWAS': ['What is my trust coin balance?', 'How to redeem trust coins?', 'Connect my wallet'],
  'SUPPORT': ['How does the app work?', 'Report a bug', 'Contact support'],
};

const PROJECT_KNOWLEDGE = `
You are part of the Ooumph SHG Marketplace ecosystem. Here's what you know about the app:

**MODULES:**
1. **Marketplace** - Buy and sell products, browse categories (handicrafts, textiles, food, etc.)
2. **My Orders** - Track orders, view history, cancel orders, see delivery status
3. **Market Analyzer** - View price trends, demand analysis, AI-powered market predictions
4. **Supplier Network** - Find suppliers, compare prices, join bulk requests, rate suppliers
5. **Community Hub** - Post updates, comment, like, view federation hierarchy
6. **Trust Wallet** - View trust coins, transaction history, connect crypto wallet, redeem rewards

**USER ROLES:**
- SHG (Self Help Group) members
- SLF (Slum Level Federation) coordinators
- TLF (Town Level Federation) admins
- Buyers and Suppliers

**KEY FEATURES:**
- Trust score system (0-100) with Bronze/Silver/Gold badges
- Trust coins earned through orders, reviews, training
- Multi-language support (English, Hindi, Telugu, Tamil)
- Voice input/output support
- Real-time chat with AI agents

**AI AGENTS:**
- Vaani (General), Market Expert, Order Assistant, Supplier Advisor, Community Guide, Finance Assistant, Support Bot

When users ask about the app, refer to these modules and features.
`;

const ChatAssistant = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [showAgents, setShowAgents] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState(AGENTS[0]);
  const [message, setMessage] = useState('');
  const [language, setLanguage] = useState('English');
  const [chatLog, setChatLog] = useState([
    { role: 'assistant', content: `🙏 Namaste! I am ${AGENTS[0].name}, your SHG Marketplace Assistant.\n\nI can help you with:\n\n🛒 **Products** - List & sell your items\n📦 **Orders** - Track & manage deliveries\n💰 **Market** - Get price insights\n🏭 **Suppliers** - Find quality materials\n⭐ **Trust** - Improve your reputation\n👥 **Community** - Connect with SHGs\n\nWhat would you like help with today?`, agent: 'VAANI' }
  ]);
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);
  const [currentResponse, setCurrentResponse] = useState('');
  const [streaming, setStreaming] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    if (bottomRef.current) bottomRef.current.scrollIntoView({ behavior: 'smooth' });
  }, [chatLog, currentResponse, isOpen]);

  useEffect(() => {
    const saved = localStorage.getItem('chatHistory');
    if (saved) setChatHistory(JSON.parse(saved));
  }, []);

  const saveToHistory = (messages) => {
    const newSession = {
      id: Date.now(),
      date: new Date().toISOString(),
      agent: selectedAgent.id,
      messages: messages.slice(-10)
    };
    const updated = [newSession, ...chatHistory.slice(0, 19)];
    setChatHistory(updated);
    localStorage.setItem('chatHistory', JSON.stringify(updated));
  };

  const handleAgentSelect = (agent) => {
    setSelectedAgent(agent);
    setShowAgents(false);
    const welcomeMsg = getAgentWelcome(agent);
    setChatLog([{ role: 'assistant', content: welcomeMsg, agent: agent.id }]);
  };

  const getAgentWelcome = (agent) => {
    const welcomes = {
      'VAANI': `🙏 Namaste! I am ${agent.name}. How can I help you today?`,
      'BAZAAR': `📊 Hello! I'm ${agent.name}. I can help you with market trends, pricing, and demand analysis. What would you like to know?`,
      'JODI': `📦 Hi there! I'm ${agent.name}. I can help you track orders, manage deliveries, and handle order issues. What do you need?`,
      'SAMAGRI': `🏭 Welcome! I'm ${agent.name}. I can help you find suppliers, compare prices, and coordinate bulk purchases. How can I assist?`,
      'SAMPARK': `👥 Hello! I'm ${agent.name}. I can help you with community posts, federation info, and connecting with other SHGs. What would you like to know?`,
      'VISHWAS': `💰 Hi! I'm ${agent.name}. I can help you with trust coins, wallet connections, and payments. What do you need?`,
      'SUPPORT': `🆘 Hello! I'm ${agent.name}. I can help you with app navigation, troubleshooting, and general questions. How can I help?`,
    };
    return welcomes[agent.id] || welcomes['VAANI'];
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!message.trim() || loading) return;
    const userMsg = message;
    setMessage('');
    const newLog = [...chatLog, { role: 'user', content: userMsg }];
    setChatLog(newLog);
    setLoading(true); setStreaming(true); setCurrentResponse('');

    try {
      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const token = localStorage.getItem('token');
      const eventSource = new EventSource(
        `${API_BASE_URL}/api/chat/stream?query=${encodeURIComponent(userMsg)}&language=${language}&agent=${selectedAgent.id}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      let fullResponse = '';
      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.error) {
          setChatLog(prev => [...prev, { role: 'assistant', content: 'Error: ' + data.error, agent: selectedAgent.id }]);
          setStreaming(false); setLoading(false); eventSource.close(); return;
        }
        if (data.content) { fullResponse += data.content; setCurrentResponse(fullResponse); }
        if (data.done) {
          const finalLog = [...newLog, { role: 'assistant', content: fullResponse, agent: selectedAgent.id }];
          setChatLog(finalLog);
          saveToHistory(finalLog);
          setCurrentResponse(''); setStreaming(false); setLoading(false); eventSource.close();
        }
      };
      eventSource.onerror = async () => {
        eventSource.close();
        try {
          const res = await chatAPI.sendMessage(userMsg, language);
          const finalLog = [...newLog, { role: 'assistant', content: res.data.reply || res.data.response, agent: res.data.agent_triggered || selectedAgent.id }];
          setChatLog(finalLog);
          saveToHistory(finalLog);
        } catch { setChatLog(prev => [...prev, { role: 'assistant', content: 'Connection failed. Please try again later.', agent: selectedAgent.id }]); }
        finally { setCurrentResponse(''); setStreaming(false); setLoading(false); }
      };
    } catch {
      try {
        const res = await chatAPI.sendMessage(userMsg, language);
        const finalLog = [...newLog, { role: 'assistant', content: res.data.reply || res.data.response, agent: res.data.agent_triggered || selectedAgent.id }];
        setChatLog(finalLog);
        saveToHistory(finalLog);
      } catch { setChatLog(prev => [...prev, { role: 'assistant', content: 'Connection failed. Please try again later.', agent: selectedAgent.id }]); }
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

  const loadHistorySession = (session) => {
    setChatLog(session.messages);
    const agent = AGENTS.find(a => a.id === session.agent) || AGENTS[0];
    setSelectedAgent(agent);
    setShowHistory(false);
  };

  const clearHistory = () => {
    setChatHistory([]);
    localStorage.removeItem('chatHistory');
  };

  const FAB_BOTTOM = 90;

  return (
    <>
      {!isOpen && (
        <button onClick={() => setIsOpen(true)} style={{
          position: 'fixed', bottom: FAB_BOTTOM, right: 20, width: 58, height: 58,
          background: `linear-gradient(135deg, ${selectedAgent.color} 0%, ${selectedAgent.color}99 100%)`,
          borderRadius: '50%', border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center',
          cursor: 'pointer', boxShadow: `0 0 25px ${selectedAgent.color}55, 0 8px 25px rgba(0,0,0,0.4)`, color: '#fff', zIndex: 60, transition: 'all 0.3s',
        }} onMouseEnter={e => { e.currentTarget.style.transform = 'scale(1.1)'; }} onMouseLeave={e => { e.currentTarget.style.transform = 'scale(1)'; }}>
          <MessageSquare size={26} />
        </button>
      )}

      {isOpen && (
        <div className="animate-scale-in" style={{
          position: 'fixed', bottom: FAB_BOTTOM, right: 16, width: 400, height: 620,
          background: 'rgba(10, 7, 18, 0.95)', border: `1px solid ${selectedAgent.color}40`,
          borderRadius: '1.5rem', backdropFilter: 'blur(24px)', WebkitBackdropFilter: 'blur(24px)',
          boxShadow: `0 30px 70px rgba(0,0,0,0.7), 0 0 40px ${selectedAgent.color}12`,
          display: 'flex', flexDirection: 'column', zIndex: 60, overflow: 'hidden',
        }}>
          {/* Header */}
          <div style={{
            background: `linear-gradient(135deg, ${selectedAgent.color}25 0%, ${selectedAgent.color}15 100%)`,
            borderBottom: `1px solid ${selectedAgent.color}25`, padding: '0.75rem 1rem',
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <button onClick={() => setShowAgents(!showAgents)} style={{
                width: 40, height: 40, borderRadius: 12, background: `${selectedAgent.color}20`,
                border: `1px solid ${selectedAgent.color}40`, display: 'flex', alignItems: 'center', justifyContent: 'center',
                cursor: 'pointer', transition: 'all 0.2s',
              }}>
                <selectedAgent.icon size={20} style={{ color: selectedAgent.color }} />
              </button>
              <div>
                <h3 style={{ fontWeight: 700, color: '#f8fafc', fontSize: '0.9rem', margin: 0 }}>{selectedAgent.name}</h3>
                <p style={{ fontSize: '0.7rem', color: selectedAgent.color, margin: 0 }}>{selectedAgent.title}</p>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <button onClick={() => setShowHistory(!showHistory)} style={{ padding: 6, border: 'none', borderRadius: 8, background: 'rgba(255,255,255,0.08)', color: '#94a3b8', cursor: 'pointer' }}>
                <History size={16} />
              </button>
              <select value={language} onChange={(e) => setLanguage(e.target.value)} style={{
                background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)',
                color: '#c4b5fd', fontSize: '0.7rem', borderRadius: 6, padding: '3px 6px', outline: 'none', cursor: 'pointer',
              }}>
                <option value="English">EN</option>
                <option value="Hindi">HI</option>
                <option value="Telugu">TE</option>
                <option value="Tamil">TA</option>
              </select>
              <button onClick={() => setIsOpen(false)} style={{ padding: 4, border: 'none', borderRadius: 6, background: 'rgba(255,255,255,0.08)', color: '#94a3b8', cursor: 'pointer' }}>
                <X size={18} />
              </button>
            </div>
          </div>

          {/* Agent Selector */}
          {showAgents && (
            <div style={{ padding: '0.75rem', borderBottom: `1px solid ${selectedAgent.color}20`, background: 'rgba(0,0,0,0.2)' }}>
              <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', margin: '0 0 0.5rem', fontWeight: 600 }}>Select an Agent:</p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 6 }}>
                {AGENTS.map((agent) => (
                  <button key={agent.id} onClick={() => handleAgentSelect(agent)} style={{
                    display: 'flex', alignItems: 'center', gap: 8, padding: '0.5rem 0.6rem',
                    background: selectedAgent.id === agent.id ? `${agent.color}20` : 'rgba(255,255,255,0.03)',
                    border: `1px solid ${selectedAgent.id === agent.id ? agent.color + '50' : 'rgba(255,255,255,0.08)'}`,
                    borderRadius: 10, cursor: 'pointer', textAlign: 'left', transition: 'all 0.2s',
                  }}>
                    <agent.icon size={16} style={{ color: agent.color, flexShrink: 0 }} />
                    <div>
                      <p style={{ fontWeight: 600, color: 'var(--text-primary)', margin: 0, fontSize: '0.75rem' }}>{agent.name}</p>
                      <p style={{ fontSize: '0.65rem', color: 'var(--text-muted)', margin: 0 }}>{agent.description}</p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* History Panel */}
          {showHistory && (
            <div style={{ padding: '0.75rem', borderBottom: `1px solid ${selectedAgent.color}20`, background: 'rgba(0,0,0,0.2)', maxHeight: 200, overflowY: 'auto' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', margin: 0, fontWeight: 600 }}>Chat History</p>
                {chatHistory.length > 0 && (
                  <button onClick={clearHistory} style={{ fontSize: '0.65rem', color: '#f87171', background: 'none', border: 'none', cursor: 'pointer' }}>Clear</button>
                )}
              </div>
              {chatHistory.length === 0 ? (
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textAlign: 'center', padding: '1rem 0' }}>No chat history yet</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {chatHistory.slice(0, 5).map((session) => (
                    <button key={session.id} onClick={() => loadHistorySession(session)} style={{
                      display: 'flex', alignItems: 'center', gap: 8, padding: '0.5rem',
                      background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)',
                      borderRadius: 8, cursor: 'pointer', textAlign: 'left',
                    }}>
                      <Bot size={14} style={{ color: AGENTS.find(a => a.id === session.agent)?.color || '#8b5cf6' }} />
                      <div style={{ flex: 1 }}>
                        <p style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', margin: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {session.messages[session.messages.length - 1]?.content?.substring(0, 40)}...
                        </p>
                        <p style={{ fontSize: '0.65rem', color: 'var(--text-muted)', margin: 0 }}>
                          {new Date(session.date).toLocaleDateString()}
                        </p>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Messages */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            {/* Quick prompts for selected agent */}
            {chatLog.length === 1 && (
              <div style={{ marginBottom: 6 }}>
                <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: 6 }}>
                  💡 Suggested questions:
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                  {AGENT_SUGGESTIONS[selectedAgent.id]?.map((q, idx) => (
                    <button key={idx} onClick={() => setMessage(q)} style={{
                      textAlign: 'left', fontSize: '0.75rem', background: `${selectedAgent.color}08`,
                      border: `1px solid ${selectedAgent.color}18`, color: 'var(--text-secondary)',
                      padding: '5px 10px', borderRadius: 8, cursor: 'pointer', transition: 'all 0.2s',
                    }}>
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {chatLog.map((msg, idx) => (
              <div key={idx} style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                <div style={{
                  maxWidth: '85%', padding: '0.6rem 0.8rem',
                  borderRadius: msg.role === 'user' ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                  background: msg.role === 'user' ? `linear-gradient(135deg, ${selectedAgent.color}, ${selectedAgent.color}cc)` : 'rgba(255,255,255,0.06)',
                  border: msg.role === 'user' ? 'none' : `1px solid ${selectedAgent.color}18`,
                  fontSize: '0.8rem', lineHeight: 1.5,
                  color: msg.role === 'user' ? '#fff' : 'var(--text-secondary)',
                }}>
                  {msg.agent && (
                    <div style={{ fontSize: '0.65rem', fontWeight: 700, color: selectedAgent.color, marginBottom: 3 }}>
                      🤖 {AGENTS.find(a => a.id === msg.agent)?.name || msg.agent}
                    </div>
                  )}
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: 6 }}>
                    <div style={{ flex: 1, whiteSpace: 'pre-line' }}>{msg.content}</div>
                    {msg.role === 'assistant' && (
                      <button onClick={() => handleVoicePlayback(msg.content)} style={{ flexShrink: 0, padding: 2, border: 'none', background: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}>
                        <Volume2 size={12} />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {streaming && currentResponse && (
              <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                <div style={{
                  maxWidth: '85%', padding: '0.6rem 0.8rem',
                  background: 'rgba(255,255,255,0.06)', border: `1px solid ${selectedAgent.color}18`,
                  borderRadius: '16px 16px 16px 4px', fontSize: '0.8rem', color: 'var(--text-secondary)',
                }}>
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: 6 }}>
                    <div style={{ width: 6, height: 6, borderRadius: '50%', background: selectedAgent.color, flexShrink: 0, marginTop: 5, animation: 'glowPulse 1s ease-in-out infinite' }} />
                    <div style={{ whiteSpace: 'pre-line' }}>{currentResponse}</div>
                  </div>
                </div>
              </div>
            )}

            {loading && !currentResponse && (
              <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                <div style={{
                  padding: '0.5rem 0.8rem', background: 'rgba(255,255,255,0.05)',
                  border: `1px solid ${selectedAgent.color}15`, borderRadius: '16px 16px 16px 4px',
                  display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-muted)', fontSize: '0.75rem',
                }}>
                  <Loader2 size={12} style={{ animation: 'spin 0.7s linear infinite', color: selectedAgent.color }} />
                  {selectedAgent.name} is thinking...
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input Bar */}
          <form onSubmit={handleSend} style={{
            padding: '0.6rem 0.8rem', borderTop: `1px solid ${selectedAgent.color}15`,
            background: 'rgba(0,0,0,0.3)', display: 'flex', alignItems: 'center', gap: 8,
          }}>
            <button type="button" onClick={handleVoiceInput} disabled={recording} style={{
              width: 34, height: 34, borderRadius: '50%', border: `1px solid ${recording ? '#ef444430' : selectedAgent.color + '20'}`,
              background: recording ? 'rgba(239,68,68,0.15)' : 'rgba(255,255,255,0.05)',
              color: recording ? '#fca5a5' : selectedAgent.color, display: 'flex', alignItems: 'center', justifyContent: 'center',
              cursor: 'pointer', flexShrink: 0,
            }}>
              <Mic size={14} />
            </button>

            <input type="text" value={message} onChange={(e) => setMessage(e.target.value)} placeholder={`Ask ${selectedAgent.name}...`} style={{
              flex: 1, padding: '0.5rem 0.8rem', background: 'rgba(255,255,255,0.06)',
              border: `1px solid ${selectedAgent.color}20`, borderRadius: 99, outline: 'none',
              color: 'var(--text-primary)', fontSize: '0.8rem', transition: 'all 0.2s',
            }} />

            <button type="submit" disabled={loading || !message.trim()} style={{
              width: 34, height: 34, borderRadius: '50%', border: 'none',
              background: !loading && message.trim() ? `linear-gradient(135deg, ${selectedAgent.color}, ${selectedAgent.color}cc)` : 'rgba(255,255,255,0.06)',
              color: !loading && message.trim() ? '#fff' : 'var(--text-muted)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              cursor: loading || !message.trim() ? 'not-allowed' : 'pointer', flexShrink: 0,
              boxShadow: !loading && message.trim() ? `0 4px 12px ${selectedAgent.color}35` : 'none',
            }}>
              <Send size={14} style={{ marginLeft: 1 }} />
            </button>
          </form>
        </div>
      )}
    </>
  );
};

export default ChatAssistant;
