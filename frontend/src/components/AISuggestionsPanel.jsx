import { useState, useEffect, useCallback } from 'react';
import { Lightbulb, X, TrendingUp, Package, Users, DollarSign, RefreshCw, Sparkles } from 'lucide-react';

const glass = { background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: '1.25rem', backdropFilter: 'blur(20px)', WebkitBackdropFilter: 'blur(20px)' };
const SUGGESTION_ICONS = { listing: Package, pricing: DollarSign, buyer: Users, trend: TrendingUp, default: Lightbulb };
const SUGGESTION_COLORS = { 
  listing: { color: '#60a5fa', bg: 'rgba(59,130,246,0.08)', border: 'rgba(59,130,246,0.25)' },
  pricing: { color: '#10b981', bg: 'rgba(16,185,129,0.08)', border: 'rgba(16,185,129,0.25)' },
  buyer: { color: '#8b5cf6', bg: 'rgba(139,92,246,0.08)', border: 'rgba(139,92,246,0.25)' },
  trend: { color: '#fcd34d', bg: 'rgba(245,158,11,0.08)', border: 'rgba(245,158,11,0.25)' },
  default: { color: '#cbd5e1', bg: 'rgba(255,255,255,0.04)', border: 'rgba(255,255,255,0.1)' }
};

const MOCK_SUGGESTIONS = [
  { id: 1, type: 'listing', title: 'List more products', message: 'You have 3 drafts ready. Listing them could increase visibility by 40%.', priority: 'high' },
  { id: 2, type: 'pricing', title: 'Price update', message: 'Market prices for fabrics are up 12%. Consider updating listing price.', priority: 'medium' },
  { id: 3, type: 'buyer', title: 'New buyer match', message: '3 new buyers looking in your category. Check your matches now!', priority: 'high' },
  { id: 4, type: 'trend', title: 'Trending now', message: 'Eco-demand is up 25%. Consider adding sustainability tags.', priority: 'low' },
];

const AISuggestionsPanel = ({ limit = 5 }) => {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dismissed, setDismissed] = useState(new Set());

  const fetchSuggestions = useCallback(async () => {
    setLoading(true);
    try {
      await new Promise(r => setTimeout(r, 600));
      setSuggestions(MOCK_SUGGESTIONS.filter(s => !dismissed.has(s.id)).slice(0, limit));
    } catch { console.error('Failed to fetch suggestions'); }
    finally { setLoading(false); }
  }, [limit, dismissed]);

  useEffect(() => { fetchSuggestions(); }, [fetchSuggestions]);

  const dismiss = (id) => {
    setDismissed(prev => new Set([...prev, id]));
    setSuggestions(prev => prev.filter(s => s.id !== id));
  };

  const visible = suggestions.filter(s => !dismissed.has(s.id));

  return (
    <div style={{ ...glass, padding: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Sparkles size={18} style={{ color: '#a78bfa' }} />
          <h3 style={{ fontWeight: 800, color: 'var(--text-primary)', margin: 0, fontSize: '0.95rem' }}>AI Insights</h3>
          <span style={{ padding: '1px 8px', background: 'rgba(139,92,246,0.15)', border: '1px solid rgba(139,92,246,0.3)', borderRadius: 99, fontSize: '0.65rem', fontWeight: 800, color: '#c4b5fd' }}>{visible.length}</span>
        </div>
        <button onClick={fetchSuggestions} disabled={loading} style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: 4 }}><RefreshCw size={14} className={loading ? 'animate-spin' : ''} /></button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {visible.map(s => {
          const Icon = SUGGESTION_ICONS[s.type] || SUGGESTION_ICONS.default;
          const style = SUGGESTION_COLORS[s.type] || SUGGESTION_COLORS.default;
          const priorityColor = s.priority === 'high' ? '#ef4444' : s.priority === 'medium' ? '#f59e0b' : '#10b981';

          return (
            <div key={s.id} className="group" style={{ position: 'relative', padding: '1rem', background: style.bg, border: `1px solid ${style.border}`, borderRadius: 12, transition: 'all 0.2s' }}>
              <button onClick={() => dismiss(s.id)} style={{ position: 'absolute', top: 8, right: 8, border: 'none', background: 'transparent', color: 'var(--text-muted)', cursor: 'pointer', padding: 2, opacity: 0 }} className="group-hover:opacity-100"><X size={14} /></button>
              <div style={{ display: 'flex', gap: 12 }}>
                <div style={{ width: 32, height: 32, borderRadius: 8, background: 'rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  <Icon size={16} style={{ color: style.color }} />
                </div>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 2 }}>
                    <div style={{ width: 6, height: 6, borderRadius: '50%', background: priorityColor }} />
                    <h4 style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '0.85rem', margin: 0 }}>{s.title}</h4>
                  </div>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.4 }}>{s.message}</p>
                </div>
              </div>
            </div>
          );
        })}
        {visible.length === 0 && !loading && (
          <div style={{ textAlign: 'center', padding: '1.5rem 0' }}>
            <Lightbulb size={32} style={{ color: 'rgba(139,92,246,0.2)', marginBottom: 8 }} />
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0 }}>All caught up! Check back later.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AISuggestionsPanel;
