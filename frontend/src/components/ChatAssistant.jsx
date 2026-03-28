import { useState, useEffect, useRef } from 'react';
import { MessageSquare, Send, X, Bot, Loader2, History, TrendingUp, Users, Heart, Wallet, HelpCircle, Package, Globe, Search } from 'lucide-react';
import { chatAPI } from '../services/api';

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
  'VAANI': ['How do I sell products?', 'What can you help with?', 'Show my dashboard summary'],
  'BAZAAR': ['Current market prices', 'Demand trends this month', 'Best products to sell now'],
  'JODI': ['Track my orders', 'Update delivery address', 'Cancel an order'],
  'SAMAGRI': ['Find suppliers nearby', 'Request a quote', 'Join bulk purchase'],
  'SAMPARK': ['My federation hierarchy', 'Latest community posts', 'Connect with SHGs'],
  'VISHWAS': ['My trust coin balance', 'How to earn coins?', 'Redeem my coins'],
  'SUPPORT': ['How does the app work?', 'I found a bug', 'Contact support'],
};

const QUICK_ACTIONS = [
  { id: 'track_order', label: '📦 Track Order', message: 'Track my recent orders' },
  { id: 'check_balance', label: '💰 Check Balance', message: 'What is my trust coin balance?' },
  { id: 'find_suppliers', label: '🏭 Find Suppliers', message: 'Find raw material suppliers near me' },
  { id: 'market_price', label: '📊 Market Price', message: 'What is the current market price for handicrafts?' },
];

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
  const [currentResponse, setCurrentResponse] = useState('');
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState(null);
  const [globalSearchMode, setGlobalSearchMode] = useState(false);
  const [showGlobalSearchPrompt, setShowGlobalSearchPrompt] = useState(false);
  const [pendingQuery, setPendingQuery] = useState('');
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
      'VAANI': `🙏 Namaste! I am ${agent.name}, your SHG Marketplace Assistant.\n\n**I can help you with:**\n• 🛒 Selling products on the marketplace\n• 📋 Understanding your dashboard\n• ⭐ Improving your trust score\n• 🎯 Finding the right features\n\n**Try asking:** "Show my dashboard summary"`,
      'BAZAAR': `📊 Welcome! I'm ${agent.name}, your Market Intelligence expert.\n\n**I can help you with:**\n• 💹 Current market prices & trends\n• 📈 Demand analysis for products\n• 🎯 Best products to sell right now\n• 🌍 Regional market insights\n\n**Try asking:** "What are the best products to sell now?"`,
      'JODI': `📦 Hi there! I'm ${agent.name}, your Order Management assistant.\n\n**I can help you with:**\n• 🚚 Track your orders in real-time\n• 📍 Update delivery addresses\n• ❌ Cancel orders when needed\n• 📋 View order history\n\n**Try asking:** "Track my orders"`,
      'SAMAGRI': `🏭 Welcome! I'm ${agent.name}, your Supplier Network advisor.\n\n**I can help you with:**\n• 🔍 Find quality suppliers nearby\n• 💰 Compare supplier prices\n• 🤝 Join bulk purchase requests\n• ⭐ Rate and review suppliers\n\n**Try asking:** "Find suppliers nearby"`,
      'SAMPARK': `👥 Hello! I'm ${agent.name}, your Community Hub guide.\n\n**I can help you with:**\n• 🏛️ View your federation hierarchy\n• 📰 Latest community posts & updates\n• 🤝 Connect with other SHGs\n• 💬 Share your experiences\n\n**Try asking:** "Show my federation hierarchy"`,
      'VISHWAS': `💰 Hi! I'm ${agent.name}, your Trust Wallet assistant.\n\n**I can help you with:**\n• 💵 Check your trust coin balance\n• 🎁 Learn how to earn more coins\n• 🔄 Redeem coins for rewards\n• 🔗 Connect your crypto wallet\n\n**Try asking:** "What is my trust coin balance?"`,
      'SUPPORT': `🆘 Hello! I'm ${agent.name}, your Support Bot.\n\n**I can help you with:**\n• 📱 App navigation & features\n• 🐛 Report bugs or issues\n• ❓ Answer general questions\n• 📞 Contact human support\n\n**Try asking:** "How does the app work?"`,
    };
    return welcomes[agent.id] || welcomes['VAANI'];
  };

  const handleQuickAction = (actionMessage) => {
    setMessage(actionMessage);
    setTimeout(() => {
      const form = document.querySelector('form');
      if (form) {
        form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
      }
    }, 50);
  };

  const getErrorMessage = (err) => {
    if (err.response?.data?.detail) return err.response.data.detail;
    if (err.message) return err.message;
    return 'An unexpected error occurred. Please try again.';
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

  const handleSend = async (e, forceGlobalSearch = false) => {
    e.preventDefault();
    if (!message.trim() && !pendingQuery) return;

    const userMessage = (forceGlobalSearch ? pendingQuery : message).trim();
    if (!userMessage || loading) return;

    setMessage('');
    setShowGlobalSearchPrompt(false);
    setPendingQuery('');
    setChatLog(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);
    setError(null);
    setCurrentResponse('');
    setStreaming(true);

    const useGlobalSearch = forceGlobalSearch || globalSearchMode;

    try {
      const response = await chatAPI.send(userMessage, selectedAgent.id, language, useGlobalSearch);
      const assistantMessage = response.data.reply || response.data.response || response.data.message || 'I understand your request. How can I help you further?';
      const needsGlobalSearch = response.data.needs_global_search || false;

      if (needsGlobalSearch && !useGlobalSearch) {
        setPendingQuery(userMessage);
        setShowGlobalSearchPrompt(true);
        setChatLog(prev => [...prev, { 
          role: 'assistant', 
          content: "I couldn't find any data on the platform for your query. Would you like me to search globally across the web?",
          agent: selectedAgent.id,
          isGlobalSearchPrompt: true
        }]);
      } else {
        setChatLog(prev => [...prev, { 
          role: 'assistant', 
          content: assistantMessage, 
          agent: selectedAgent.id,
          isGlobalSearch: useGlobalSearch
        }]);
        saveToHistory([...chatLog, { role: 'user', content: userMessage }, { role: 'assistant', content: assistantMessage, agent: selectedAgent.id }]);
      }
    } catch (err) {
      setError(err);
      setChatLog(prev => [...prev, { role: 'assistant', content: getErrorMessage(err), isError: true }]);
    } finally {
      setLoading(false);
      setStreaming(false);
      setCurrentResponse('');
    }
  };

  const handleGlobalSearchConfirm = () => {
    const fakeEvent = { preventDefault: () => {} };
    handleSend(fakeEvent, true);
  };

  const handleGlobalSearchCancel = () => {
    setShowGlobalSearchPrompt(false);
    setPendingQuery('');
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
                  background: msg.isError ? 'rgba(239, 68, 68, 0.1)' : msg.role === 'user' ? `linear-gradient(135deg, ${selectedAgent.color}, ${selectedAgent.color}cc)` : 'rgba(255,255,255,0.06)',
                  border: msg.isError ? '1px solid rgba(239, 68, 68, 0.3)' : msg.role === 'user' ? 'none' : `1px solid ${selectedAgent.color}18`,
                  fontSize: '0.8rem', lineHeight: 1.5,
                  color: msg.isError ? '#fca5a5' : msg.role === 'user' ? '#fff' : 'var(--text-secondary)',
                }}>
                  {msg.agent && (
                    <div style={{ fontSize: '0.65rem', fontWeight: 700, color: selectedAgent.color, marginBottom: 3, display: 'flex', alignItems: 'center', gap: 4 }}>
                      <span>🤖 {AGENTS.find(a => a.id === msg.agent)?.name || msg.agent}</span>
                      {msg.isGlobalSearch && (
                        <span style={{ 
                          background: 'rgba(59, 130, 246, 0.2)', 
                          color: '#60a5fa', 
                          padding: '1px 6px', 
                          borderRadius: 4, 
                          fontSize: '0.6rem',
                          display: 'flex',
                          alignItems: 'center',
                          gap: 3
                        }}>
                          <Globe size={10} /> Global Search
                        </span>
                      )}
                    </div>
                  )}
                  <div style={{ whiteSpace: 'pre-line' }}>{msg.content}</div>
                  {msg.isGlobalSearchPrompt && (
                    <div style={{ marginTop: 10, display: 'flex', gap: 8 }}>
                      <button
                        onClick={handleGlobalSearchConfirm}
                        disabled={loading}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 4,
                          padding: '6px 12px',
                          background: 'linear-gradient(135deg, #3b82f6, #2563eb)',
                          border: 'none',
                          borderRadius: 8,
                          color: '#fff',
                          fontSize: '0.75rem',
                          fontWeight: 600,
                          cursor: loading ? 'not-allowed' : 'pointer',
                          opacity: loading ? 0.5 : 1,
                        }}
                      >
                        <Globe size={14} />
                        Search Globally
                      </button>
                      <button
                        onClick={handleGlobalSearchCancel}
                        disabled={loading}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 4,
                          padding: '6px 12px',
                          background: 'rgba(255,255,255,0.08)',
                          border: '1px solid rgba(255,255,255,0.15)',
                          borderRadius: 8,
                          color: 'var(--text-secondary)',
                          fontSize: '0.75rem',
                          cursor: loading ? 'not-allowed' : 'pointer',
                          opacity: loading ? 0.5 : 1,
                        }}
                      >
                        Cancel
                      </button>
                    </div>
                  )}
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
                  padding: '0.6rem 1rem', background: 'rgba(255,255,255,0.05)',
                  border: `1px solid ${selectedAgent.color}15`, borderRadius: '16px 16px 16px 4px',
                  display: 'flex', alignItems: 'center', gap: 10,
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    <div style={{ width: 6, height: 6, borderRadius: '50%', background: selectedAgent.color, animation: 'typingDot 1s ease-in-out infinite' }} />
                    <div style={{ width: 6, height: 6, borderRadius: '50%', background: selectedAgent.color, animation: 'typingDot 1s ease-in-out 0.2s infinite' }} />
                    <div style={{ width: 6, height: 6, borderRadius: '50%', background: selectedAgent.color, animation: 'typingDot 1s ease-in-out 0.4s infinite' }} />
                  </div>
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>{selectedAgent.name} is typing...</span>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input Bar */}
          <form onSubmit={handleSend} style={{
            padding: '0.6rem 0.8rem', borderTop: `1px solid ${selectedAgent.color}15`,
            background: 'rgba(0,0,0,0.3)', display: 'flex', alignItems: 'center', gap: 8,
            position: 'relative',
          }}>
            {globalSearchMode && (
              <div style={{
                position: 'absolute',
                bottom: '100%',
                left: 0,
                right: 0,
                background: 'rgba(59, 130, 246, 0.1)',
                borderBottom: '1px solid rgba(59, 130, 246, 0.3)',
                padding: '4px 12px',
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                fontSize: '0.7rem',
                color: '#60a5fa',
              }}>
                <Globe size={12} />
                <span>Global search mode enabled</span>
              </div>
            )}
            <input type="text" value={message} onChange={(e) => setMessage(e.target.value)} placeholder={`Ask ${selectedAgent.name}...`} style={{
              flex: 1, padding: '0.5rem 0.8rem', background: 'rgba(255,255,255,0.06)',
              border: `1px solid ${selectedAgent.color}20`, borderRadius: 99, outline: 'none',
              color: 'var(--text-primary)', fontSize: '0.8rem', transition: 'all 0.2s',
            }} />

            <button
              type="button"
              onClick={() => setGlobalSearchMode(!globalSearchMode)}
              title={globalSearchMode ? 'Disable global search' : 'Enable global search'}
              style={{
                width: 34, height: 34, borderRadius: '50%', border: 'none',
                background: globalSearchMode ? 'linear-gradient(135deg, #3b82f6, #2563eb)' : 'rgba(255,255,255,0.06)',
                color: globalSearchMode ? '#fff' : 'var(--text-muted)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                cursor: 'pointer', flexShrink: 0,
                transition: 'all 0.2s',
              }}
            >
              <Globe size={14} />
            </button>

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

          {/* Quick Action Buttons */}
          <div style={{
            padding: '0.5rem 0.8rem 0.7rem', borderTop: `1px solid ${selectedAgent.color}10`,
            background: 'rgba(0,0,0,0.2)', display: 'flex', flexWrap: 'wrap', gap: 6,
          }}>
            {QUICK_ACTIONS.map((action) => (
              <button key={action.id} onClick={() => handleQuickAction(action.message)} disabled={loading} style={{
                display: 'flex', alignItems: 'center', gap: 4, padding: '4px 8px',
                background: `${selectedAgent.color}10`, border: `1px solid ${selectedAgent.color}25`,
                borderRadius: 12, cursor: loading ? 'not-allowed' : 'pointer', fontSize: '0.7rem',
                color: 'var(--text-secondary)', transition: 'all 0.2s', opacity: loading ? 0.5 : 1,
              }}>
                {action.label}
              </button>
            ))}
          </div>
        </div>
      )}
      <style>{`
        @keyframes typingDot {
          0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
          30% { transform: translateY(-4px); opacity: 1; }
        }
      `}</style>
    </>
  );
};

export default ChatAssistant;
