import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { marketAPI } from '../services/api';
import { TrendingUp, DollarSign, Calendar, MapPin, Package } from 'lucide-react';

const glass = { background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: '1.25rem', backdropFilter: 'blur(16px)', WebkitBackdropFilter: 'blur(16px)' };
const inputStyle = { width: '100%', padding: '0.65rem 0.9rem', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(139,92,246,0.22)', borderRadius: 10, outline: 'none', color: 'var(--text-primary)', fontSize: '0.9rem', transition: 'all 0.2s' };
const labelStyle = { display: 'block', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' };
const onFocus = e => { e.target.style.borderColor = '#8b5cf6'; e.target.style.boxShadow = '0 0 0 3px rgba(139,92,246,0.15)'; };
const onBlur  = e => { e.target.style.borderColor = 'rgba(139,92,246,0.22)'; e.target.style.boxShadow = 'none'; };

const MarketAnalyzer = () => {
  const navigate = useNavigate();
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [formData, setFormData] = useState({ product_name: '', category: 'Handicrafts', district: 'Hyderabad', price: '' });

  const categories = ['Handicrafts','Food Products','Textiles','Pickles','Spices','Handmade Baskets'];
  const districts  = ['Hyderabad','Visakhapatnam','Vijayawada','Guntur','Tirupati','Rajahmundry','Kakinada','Kurnool'];

  const handleAnalyze = async (e) => {
    e.preventDefault(); setAnalyzing(true); setResult(null);
    try {
      const response = await marketAPI.analyze({ product_name: formData.product_name, category: formData.category, district: formData.district, price: formData.price ? parseFloat(formData.price) : null });
      setResult(response.data);
    } catch (error) { alert('Analysis failed: ' + (error.response?.data?.detail || 'Unknown error')); }
    finally { setAnalyzing(false); }
  };

  const demandColor = { High: '#6ee7b7', Medium: '#fcd34d', Low: '#fca5a5' };
  const demandBg    = { High: 'rgba(16,185,129,0.12)', Medium: 'rgba(245,158,11,0.12)', Low: 'rgba(239,68,68,0.12)' };
  const demandBorder= { High: 'rgba(16,185,129,0.3)',  Medium: 'rgba(245,158,11,0.3)',  Low: 'rgba(239,68,68,0.3)' };

  const quickActions = [
    { label: 'Sell Product',  icon: TrendingUp, path: '/sell',       color: '#8b5cf6' },
    { label: 'Find Buyers',   icon: TrendingUp, path: '/matches',    color: '#a78bfa' },
    { label: 'Buy Materials', icon: Package,    path: '/suppliers',  color: '#10b981' },
    { label: 'Trust Coins',   icon: DollarSign, path: '/wallet',     color: '#f59e0b' },
  ];

  return (
    <div className="animate-fade-in" style={{ padding: '1.5rem', maxWidth: 1100, margin: '0 auto', paddingBottom: '6rem' }}>
      <div style={{ marginBottom: '1.75rem' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 900, margin: '0 0 4px', background: 'linear-gradient(135deg, #f8fafc 0%, #c4b5fd 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>Agent Bazaar Buddhi</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', margin: 0 }}>Market Intelligence & Price Recommendations</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: result ? '1fr 1fr' : '1fr', gap: '1.25rem', marginBottom: '1.5rem' }}>
        {/* Form */}
        <div style={{ ...glass, padding: '1.75rem' }}>
          <h2 style={{ fontWeight: 800, color: 'var(--text-primary)', fontSize: '1.1rem', marginBottom: '1.25rem' }}>Analyze Your Product</h2>
          <form onSubmit={handleAnalyze} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={labelStyle}>Product Name</label>
              <input type="text" value={formData.product_name} onChange={e => setFormData({ ...formData, product_name: e.target.value })} style={inputStyle} placeholder="e.g., Bamboo Basket" required onFocus={onFocus} onBlur={onBlur} />
            </div>
            <div>
              <label style={labelStyle}>Category</label>
              <select value={formData.category} onChange={e => setFormData({ ...formData, category: e.target.value })} style={{ ...inputStyle, cursor: 'pointer' }} required onFocus={onFocus} onBlur={onBlur}>
                {categories.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label style={labelStyle}>District</label>
              <select value={formData.district} onChange={e => setFormData({ ...formData, district: e.target.value })} style={{ ...inputStyle, cursor: 'pointer' }} required onFocus={onFocus} onBlur={onBlur}>
                {districts.map(d => <option key={d} value={d}>{d}</option>)}
              </select>
            </div>
            <div>
              <label style={labelStyle}>Your Cost Price (₹)</label>
              <input type="number" value={formData.price} onChange={e => setFormData({ ...formData, price: e.target.value })} style={inputStyle} placeholder="e.g., 500" onFocus={onFocus} onBlur={onBlur} />
            </div>
            <button type="submit" disabled={analyzing} style={{ padding: '0.75rem', background: analyzing ? 'rgba(139,92,246,0.2)' : 'linear-gradient(135deg, #7c3aed, #a855f7)', border: 'none', borderRadius: 10, color: '#fff', fontWeight: 700, cursor: analyzing ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, boxShadow: '0 4px 14px rgba(139,92,246,0.35)', transition: 'all 0.2s' }}>
              {analyzing ? <><div style={{ width: 16, height: 16, borderRadius: '50%', border: '2px solid rgba(255,255,255,0.3)', borderTopColor: '#fff', animation: 'spin 0.7s linear infinite' }} />Analyzing...</> : <><TrendingUp size={17} />Analyze Market</>}
            </button>
          </form>
        </div>

        {/* Results */}
        {result && (
          <div style={{ ...glass, padding: '1.75rem' }}>
            <h3 style={{ fontWeight: 800, color: 'var(--text-primary)', fontSize: '1.1rem', marginBottom: '1.25rem' }}>Market Analysis Results</h3>
            {/* Demand */}
            <div style={{ marginBottom: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Demand Level</span>
                <span style={{ padding: '3px 10px', borderRadius: 99, fontSize: '0.72rem', fontWeight: 800, background: demandBg[result.demand_level] || 'rgba(139,92,246,0.1)', color: demandColor[result.demand_level] || '#c4b5fd', border: `1px solid ${demandBorder[result.demand_level] || 'rgba(139,92,246,0.25)'}` }}>{result.demand_level}</span>
              </div>
              <div style={{ width: '100%', height: 8, background: 'rgba(255,255,255,0.06)', borderRadius: 99, overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${result.demand_score}%`, background: 'linear-gradient(90deg, #7c3aed, #a855f7)', borderRadius: 99, transition: 'width 1s ease' }} />
              </div>
              <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textAlign: 'right', margin: '4px 0 0' }}>{result.demand_score}/100</p>
            </div>
            {/* Price */}
            <div style={{ background: 'rgba(16,185,129,0.06)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: 10, padding: '0.9rem', marginBottom: '1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 8 }}>
                <DollarSign size={15} style={{ color: '#10b981' }} />
                <span style={{ fontWeight: 700, color: '#6ee7b7', fontSize: '0.85rem' }}>Price Recommendation</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: '0 0 2px' }}>Min: ₹{result.recommended_price_min}</p>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>Max: ₹{result.recommended_price_max}</p>
                </div>
                <p style={{ fontWeight: 900, color: '#6ee7b7', fontSize: '1.3rem', margin: 0 }}>₹{Math.round((result.recommended_price_min + result.recommended_price_max) / 2)}</p>
              </div>
            </div>
            {/* Seasonal */}
            {result.is_seasonal && (
              <div style={{ background: 'rgba(245,158,11,0.07)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: 10, padding: '0.9rem', marginBottom: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 6 }}>
                  <Calendar size={15} style={{ color: '#f59e0b' }} />
                  <span style={{ fontWeight: 700, color: '#fcd34d', fontSize: '0.85rem' }}>Seasonal Demand</span>
                </div>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', margin: '0 0 3px' }}>Peak season: {result.peak_season}</p>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0 }}>Currently: {result.current_season} {result.is_peak_season && '✅ Peak!'}</p>
              </div>
            )}
            {/* Districts */}
            <div style={{ marginBottom: '1rem' }}>
              <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
                <MapPin size={14} style={{ color: '#a78bfa' }} /> Best Selling Districts
              </h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {result.best_selling_districts?.map((d, i) => (
                  <span key={i} style={{ padding: '3px 10px', background: 'rgba(139,92,246,0.12)', border: '1px solid rgba(139,92,246,0.25)', borderRadius: 99, fontSize: '0.72rem', fontWeight: 600, color: '#c4b5fd' }}>{d}</span>
                ))}
              </div>
            </div>
            {/* Suggestions */}
            <div>
              <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: 8 }}>Suggestions</h4>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 5 }}>
                {result.suggestions?.map((s, i) => (
                  <li key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 7, fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                    <span style={{ color: '#6ee7b7', flexShrink: 0 }}>✓</span>{s}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px,1fr))', gap: '0.75rem' }}>
        {quickActions.map(({ label, icon: Icon, path, color }) => (
          <button key={path} onClick={() => navigate(path)} style={{ ...glass, padding: '1.25rem', textAlign: 'center', border: 'none', cursor: 'pointer', transition: 'all 0.25s' }}
            onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.07)'; e.currentTarget.style.transform = 'translateY(-3px)'; }}
            onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.04)'; e.currentTarget.style.transform = 'translateY(0)'; }}>
            <div style={{ width: 44, height: 44, borderRadius: '50%', background: `${color}18`, border: `1px solid ${color}35`, display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 10px' }}>
              <Icon size={20} style={{ color }} />
            </div>
            <p style={{ fontWeight: 600, color: 'var(--text-secondary)', margin: 0, fontSize: '0.85rem' }}>{label}</p>
          </button>
        ))}
      </div>
    </div>
  );
};

export default MarketAnalyzer;
