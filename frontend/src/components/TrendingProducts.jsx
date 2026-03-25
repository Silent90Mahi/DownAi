import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { TrendingUp, Package, ShoppingBag, ChevronRight } from 'lucide-react';
import { recommendationAPI } from '../services/recommendationAPI';

const glass = { background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: '1.25rem', backdropFilter: 'blur(16px)', WebkitBackdropFilter: 'blur(16px)' };

const TrendingProducts = ({ district = null, limit = 10 }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => { fetchTrendingProducts(); }, [district, limit]);

  const fetchTrendingProducts = async () => {
    try {
      setLoading(true);
      const r = await recommendationAPI.getTrendingProducts(district, limit);
      setProducts(r.data || []);
    } catch { console.error('Failed to fetch trending'); }
    finally { setLoading(false); }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <TrendingUp size={20} style={{ color: '#a78bfa' }} />
          <h2 style={{ fontSize: '1.25rem', fontWeight: 900, color: 'var(--text-primary)', margin: 0 }}>Trending Now</h2>
          {district && <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', background: 'rgba(139,92,246,0.1)', padding: '2px 8px', borderRadius: 6 }}>in {district}</span>}
        </div>
        <button onClick={() => navigate('/marketplace')} style={{ background: 'transparent', border: 'none', color: '#c4b5fd', fontSize: '0.85rem', fontWeight: 700, cursor: 'pointer' }}>View All <ChevronRight size={14} /></button>
      </div>

      <div style={{ display: 'flex', gap: '1rem', overflowX: 'auto', paddingBottom: '0.75rem' }} className="scrollbar-hide">
        {loading ? [1,2,3,4].map(i => <div key={i} style={{ flexShrink: 0, width: 200, height: 260, ...glass, animation: 'glowPulse 2s infinite' }} />) :
         products.map(p => (
          <article key={p.id} onClick={() => navigate(`/products/${p.id}`)} style={{ flexShrink: 0, width: 200, ...glass, cursor: 'pointer', overflow: 'hidden', transition: 'all 0.2s' }} onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-4px)'} onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}>
            <div style={{ position: 'relative', height: 160, background: 'rgba(0,0,0,0.2)' }}>
              {p.image_url ? <img src={p.image_url} alt={p.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} /> : <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Package size={36} style={{ color: 'rgba(139,92,246,0.3)' }} /></div>}
              {p.order_count !== undefined && (
                <div style={{ position: 'absolute', top: 8, right: 8, background: '#a855f7', color: '#fff', padding: '2px 8px', borderRadius: 99, display: 'flex', alignItems: 'center', gap: 4, boxShadow: '0 0 10px rgba(168,85,247,0.4)', border: '1px solid rgba(255,255,255,0.2)' }}>
                  <ShoppingBag size={10} />
                  <span style={{ fontSize: '0.65rem', fontWeight: 800 }}>{p.order_count}+ sold</span>
                </div>
              )}
            </div>
            <div style={{ padding: '0.75rem' }}>
              <h3 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-secondary)', margin: '0 0 4px', lineClamp: 1, overflow: 'hidden', display: '-webkit-box', WebkitLineClamp: 1, WebkitBoxOrient: 'vertical' }}>{p.name}</h3>
              <div style={{ fontSize: '1.1rem', fontWeight: 900, color: '#a78bfa', marginBottom: 6 }}>₹{p.price?.toLocaleString()}</div>
              {p.category && <span style={{ fontSize: '0.6rem', fontWeight: 800, color: 'var(--text-muted)', background: 'rgba(255,255,255,0.05)', padding: '2px 6px', borderRadius: 4, textTransform: 'uppercase' }}>{p.category}</span>}
            </div>
          </article>
        ))}
      </div>
    </div>
  );
};

export default TrendingProducts;
