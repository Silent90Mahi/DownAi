import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layers, Package, ArrowRight } from 'lucide-react';
import { recommendationAPI } from '../services/recommendationAPI';

const glass = { background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: '1.25rem', backdropFilter: 'blur(16px)', WebkitBackdropFilter: 'blur(16px)' };

const SimilarProducts = ({ productId, limit = 5 }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => { if (productId) fetchSimilar(); }, [productId, limit]);

  const fetchSimilar = async () => {
    try {
      setLoading(true);
      const r = await recommendationAPI.getSimilarProducts(productId, limit);
      setProducts(r.data || []);
    } catch { console.error('Failed to fetch similar'); }
    finally { setLoading(false); }
  };

  if (!productId || (!loading && products.length === 0)) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '2rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <Layers size={20} style={{ color: '#a78bfa' }} />
        <h3 style={{ fontSize: '1.1rem', fontWeight: 900, color: 'var(--text-primary)', margin: 0 }}>Similar Products You May Like</h3>
      </div>

      <div style={{ display: 'flex', gap: '1rem', overflowX: 'auto', paddingBottom: '0.75rem' }} className="scrollbar-hide">
        {loading ? [1,2,3].map(i => <div key={i} style={{ flexShrink: 0, width: 240, height: 160, ...glass, animation: 'glowPulse 2s infinite' }} />) :
         products.map(p => (
          <article key={p.id} onClick={() => navigate(`/products/${p.id}`)} style={{ flexShrink: 0, width: 240, ...glass, cursor: 'pointer', overflow: 'hidden', position: 'relative' }}>
            <div style={{ height: 120, background: 'rgba(0,0,0,0.2)' }}>
              {p.image_url ? <img src={p.image_url} alt={p.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} /> : <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Package size={32} style={{ color: 'rgba(139,92,246,0.3)' }} /></div>}
              {p.similarity_score !== undefined && (
                <div style={{ position: 'absolute', top: 8, left: 8, background: 'rgba(16,185,129,0.85)', backdropFilter: 'blur(5px)', border: '1px solid rgba(255,255,255,0.2)', color: '#fff', padding: '2px 8px', borderRadius: 99, fontSize: '0.65rem', fontWeight: 800 }}>
                  {Math.round(p.similarity_score * 100)}% Match
                </div>
              )}
            </div>
            <div style={{ padding: '0.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
              <div>
                <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-secondary)', margin: '0 0 4px', lineClamp: 1, overflow: 'hidden', whiteSpace: 'nowrap' }}>{p.name}</h4>
                <div style={{ fontSize: '1rem', fontWeight: 900, color: '#a78bfa' }}>₹{p.price?.toLocaleString()}</div>
              </div>
              <div style={{ width: 28, height: 28, borderRadius: '50%', background: 'rgba(139,92,246,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#c4b5fd' }}><ArrowRight size={14} /></div>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
};

export default SimilarProducts;
