import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, Shield, Package, UserPlus, UserCheck, ChevronRight } from 'lucide-react';
import { recommendationAPI } from '../services/recommendationAPI';

const glass = { background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: '1.25rem', backdropFilter: 'blur(16px)', WebkitBackdropFilter: 'blur(16px)' };

const RecommendedSHGs = ({ limit = 5 }) => {
  const [shgs, setShgs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [followingIds, setFollowingIds] = useState(new Set());
  const navigate = useNavigate();

  useEffect(() => { fetchRecommendedSHGs(); }, [limit]);

  const fetchRecommendedSHGs = async () => {
    try {
      setLoading(true);
      const r = await recommendationAPI.getRecommendedSHGs(limit);
      setShgs(r.data || []);
    } catch { console.error('Failed to fetch SHGs'); }
    finally { setLoading(false); }
  };

  const toggleFollow = (id) => {
    setFollowingIds(prev => {
      const n = new Set(prev);
      if (n.has(id)) n.delete(id); else n.add(id);
      return n;
    });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Users size={20} style={{ color: '#a78bfa' }} />
          <h2 style={{ fontSize: '1.25rem', fontWeight: 900, color: 'var(--text-primary)', margin: 0 }}>SHGs to Follow</h2>
        </div>
        <button onClick={() => navigate('/community')} style={{ background: 'transparent', border: 'none', color: '#c4b5fd', fontSize: '0.85rem', fontWeight: 700, cursor: 'pointer' }}>View All <ChevronRight size={14} /></button>
      </div>

      <div style={{ display: 'flex', gap: '1rem', overflowX: 'auto', paddingBottom: '0.75rem' }} className="scrollbar-hide">
        {loading ? [1,2,3].map(i => <div key={i} style={{ flexShrink: 0, width: 260, height: 180, ...glass, animation: 'glowPulse 2s infinite' }} />) :
         shgs.map(shg => (
          <article key={shg.id} style={{ flexShrink: 0, width: 260, ...glass, padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: 15 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, cursor: 'pointer' }} onClick={() => navigate(`/profile`)}>
              <div style={{ width: 48, height: 48, borderRadius: '50%', background: 'linear-gradient(135deg,#7c3aed,#a855f7)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 900, color: '#fff', fontSize: '1.2rem', flexShrink: 0 }}>
                {shg.name?.charAt(0)}
              </div>
              <div style={{ minWidth: 0 }}>
                <h3 style={{ fontSize: '0.95rem', fontWeight: 800, color: 'var(--text-primary)', margin: '0 0 2px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{shg.name}</h3>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0 }}>{shg.district || 'Andhra Pradesh'}</p>
              </div>
            </div>
            
            <div style={{ display: 'flex', gap: 8 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 4, background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)', padding: '3px 8px', borderRadius: 99 }}>
                <Shield size={12} style={{ color: '#6ee7b7' }} />
                <span style={{ fontSize: '0.7rem', fontWeight: 700, color: '#6ee7b7' }}>{shg.trust_score?.toFixed(1) || '4.5'}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 4, background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', padding: '3px 8px', borderRadius: 99 }}>
                <Package size={12} style={{ color: 'var(--text-muted)' }} />
                <span style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-secondary)' }}>{shg.product_count || 12} Products</span>
              </div>
            </div>

            <button onClick={() => toggleFollow(shg.id)} style={{ width: '100%', padding: '0.65rem', background: followingIds.has(shg.id) ? 'rgba(16,185,129,0.15)' : '#7c3aed', border: 'none', borderRadius: 10, color: followingIds.has(shg.id) ? '#6ee7b7' : '#fff', fontWeight: 800, fontSize: '0.85rem', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, transition: 'all 0.2s' }}>
              {followingIds.has(shg.id) ? <><UserCheck size={16} /> Following</> : <><UserPlus size={16} /> Follow</>}
            </button>
          </article>
        ))}
      </div>
    </div>
  );
};

export default RecommendedSHGs;
