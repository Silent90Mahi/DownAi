import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ChevronRight, Star, Shield, Package } from 'lucide-react';
import { recommendationAPI } from '../services/recommendationAPI';

const glass = { background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: '1.25rem', backdropFilter: 'blur(16px)', WebkitBackdropFilter: 'blur(16px)' };

const RecommendationSection = ({ title = 'Recommended for You', limit = 10, type = 'products' }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => { fetchRecommendations(); }, [type, limit]);

  const fetchRecommendations = async () => {
    try {
      setLoading(true); setError(null);
      const response = await recommendationAPI.getRecommendations(type, limit);
      setRecommendations(response.data || []);
    } catch { setError('Unable to load'); }
    finally { setLoading(false); }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Sparkles size={20} style={{ color: '#a78bfa' }} />
          <h2 style={{ fontSize: '1.25rem', fontWeight: 900, color: 'var(--text-primary)', margin: 0 }}>{title}</h2>
        </div>
        <button onClick={() => navigate('/marketplace')} style={{ display: 'flex', alignItems: 'center', gap: 4, background: 'transparent', border: 'none', color: '#c4b5fd', fontSize: '0.85rem', fontWeight: 700, cursor: 'pointer' }}>
          View All <ChevronRight size={14} />
        </button>
      </div>

      <div style={{ display: 'flex', gap: '1rem', overflowX: 'auto', paddingBottom: '0.75rem' }} className="scrollbar-hide">
        {loading ? [1,2,3,4].map(i => <div key={i} style={{ flexShrink: 0, width: 220, height: 280, ...glass, animation: 'glowPulse 2s infinite' }} />) :
         recommendations.map(item => (
          <article key={item.id} onClick={() => navigate(`/products/${item.id}`)} style={{ flexShrink: 0, width: 220, ...glass, cursor: 'pointer', overflow: 'hidden', transition: 'all 0.2s' }} onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-4px)'} onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}>
            <div style={{ position: 'relative', aspectSquare: '1/1', background: 'rgba(0,0,0,0.2)' }}>
              {item.image_url ? <img src={item.image_url} alt={item.name} style={{ width: '100%', height: 180, objectFit: 'cover' }} /> : <div style={{ width: '100%', height: 180, display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Package size={40} style={{ color: 'rgba(139,92,246,0.3)' }} /></div>}
              {item.recommendation_score && (
                <div style={{ position: 'absolute', top: 8, right: 8, background: 'rgba(13,10,26,0.8)', backdropFilter: 'blur(5px)', padding: '2px 8px', borderRadius: 99, display: 'flex', alignItems: 'center', gap: 4, border: '1px solid rgba(139,92,246,0.2)' }}>
                  <Star size={10} fill="#fbbf24" color="#fbbf24" />
                  <span style={{ fontSize: '0.65rem', fontWeight: 800, color: '#fff' }}>{Math.round(item.recommendation_score * 100)}%</span>
                </div>
              )}
            </div>
            <div style={{ padding: '0.75rem' }}>
              <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-secondary)', margin: '0 0 6px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{item.name}</h3>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 4, marginBottom: 8 }}>
                <span style={{ fontSize: '1.2rem', fontWeight: 900, color: '#a78bfa' }}>₹{item.price?.toLocaleString()}</span>
              </div>
              {item.trust_score !== undefined && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <Shield size={12} style={{ color: '#6ee7b7' }} />
                  <span style={{ fontSize: '0.7rem', fontWeight: 700, color: '#6ee7b7' }}>Trust: {item.trust_score.toFixed(1)}</span>
                </div>
              )}
            </div>
          </article>
        ))}
      </div>
    </div>
  );
};

export default RecommendationSection;
