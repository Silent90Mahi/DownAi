import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { productsAPI, matchingAPI } from '../services/api';
import { Users, Handshake, TrendingUp, CheckCircle, Package } from 'lucide-react';

const glass = { background:'rgba(255,255,255,0.04)', border:'1px solid rgba(139,92,246,0.2)', borderRadius:'1.1rem', backdropFilter:'blur(16px)', WebkitBackdropFilter:'blur(16px)' };

const BuyerMatches = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [matches, setMatches] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user?.role !== 'SHG') { navigate('/'); return; }
    fetchMyProducts();
  }, [user, navigate]);

  const fetchMyProducts = async () => {
    try { const r = await productsAPI.getMyProducts(); setProducts(r.data); }
    catch { console.error('Failed to fetch products'); }
  };

  const handleFindBuyers = async (product) => {
    try {
      setLoading(product.id);
      const r = await matchingAPI.findBuyers({ product_id:product.id, quantity:10, price:product.price, district:user?.district||'Hyderabad' });
      setMatches(p=>({...p,[product.id]:r.data}));
    } catch { console.error('Failed to find buyers'); }
    finally { setLoading(null); }
  };

  return (
    <div className="animate-fade-in" style={{ padding:'1.5rem', maxWidth:900, margin:'0 auto', paddingBottom:'6rem' }}>
      <div style={{ marginBottom:'1.75rem' }}>
        <h1 style={{ fontSize:'1.75rem', fontWeight:900, margin:'0 0 4px', background:'linear-gradient(135deg,#f8fafc 0%,#c4b5fd 100%)', WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent', backgroundClip:'text' }}>Agent Jodi</h1>
        <p style={{ color:'var(--text-muted)', fontSize:'0.875rem', margin:0 }}>Buyer Matching & Government Procurement</p>
      </div>

      {/* Trust Score Banner */}
      <div style={{ background:'rgba(139,92,246,0.08)', border:'1px solid rgba(139,92,246,0.2)', borderRadius:'1rem', padding:'1rem 1.25rem', marginBottom:'1.5rem', display:'flex', alignItems:'center', gap:12 }}>
        <div style={{ width:44, height:44, borderRadius:'50%', background:'rgba(139,92,246,0.15)', border:'1px solid rgba(139,92,246,0.3)', display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0 }}>
          <TrendingUp size={20} style={{ color:'#a78bfa' }}/>
        </div>
        <div>
          <p style={{ fontWeight:700, color:'var(--text-primary)', margin:'0 0 2px', fontSize:'0.9rem' }}>Trust Score: <span style={{ color:'#c4b5fd' }}>{user?.trust_score||50}</span></p>
          <p style={{ fontSize:'0.78rem', color:'var(--text-muted)', margin:0 }}>Higher trust scores = Better buyer matches</p>
        </div>
      </div>

      {/* Products */}
      <h2 style={{ fontSize:'1.1rem', fontWeight:800, color:'var(--text-primary)', marginBottom:'1rem' }}>Your Products</h2>
      {products.length===0 ? (
        <div style={{ textAlign:'center', padding:'3rem', ...glass }}>
          <Package size={48} style={{ color:'rgba(139,92,246,0.25)', margin:'0 auto 12px' }}/>
          <p style={{ fontWeight:600, color:'var(--text-muted)', margin:'0 0 12px' }}>No products yet</p>
          <button onClick={()=>navigate('/sell')} style={{ padding:'0.55rem 1.25rem', background:'linear-gradient(135deg,#7c3aed,#a855f7)', border:'none', borderRadius:10, color:'#fff', fontWeight:700, cursor:'pointer' }}>
            List Your First Product
          </button>
        </div>
      ) : (
        <div style={{ display:'flex', flexDirection:'column', gap:'1rem', marginBottom:'1.5rem' }}>
          {products.map(product=>(
            <div key={product.id} style={{ ...glass, padding:'1.25rem' }}>
              <div style={{ display:'flex', gap:'1rem', flexWrap:'wrap' }}>
                {/* Product thumbnail */}
                <div style={{ width:96, height:96, borderRadius:12, background:'rgba(139,92,246,0.1)', border:'1px solid rgba(139,92,246,0.2)', display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0 }}>
                  <Package size={36} style={{ color:'#8b5cf6' }}/>
                </div>
                {/* Details */}
                <div style={{ flex:1 }}>
                  <h3 style={{ fontWeight:800, color:'var(--text-primary)', margin:'0 0 4px', fontSize:'1rem' }}>{product.name}</h3>
                  <p style={{ fontSize:'0.8rem', color:'var(--text-muted)', margin:'0 0 6px' }}>{product.category}</p>
                  <p style={{ fontWeight:900, color:'#a78bfa', fontSize:'1.2rem', margin:0 }}>₹{product.price}</p>
                </div>
                {/* Actions */}
                <div style={{ display:'flex', flexDirection:'column', alignItems:'flex-end', gap:8 }}>
                  <button
                    onClick={()=>handleFindBuyers(product)}
                    disabled={loading===product.id}
                    style={{ padding:'8px 18px', background:'linear-gradient(135deg,#7c3aed,#a855f7)', border:'none', borderRadius:10, color:'#fff', fontWeight:700, cursor:loading===product.id?'not-allowed':'pointer', display:'flex', alignItems:'center', gap:7, boxShadow:'0 4px 12px rgba(139,92,246,0.35)', opacity:loading===product.id?0.7:1 }}
                  >
                    {loading===product.id
                      ? <><div style={{ width:14,height:14,borderRadius:'50%',border:'2px solid rgba(255,255,255,0.3)',borderTopColor:'#fff',animation:'spin 0.7s linear infinite' }}/>Finding...</>
                      : <><Users size={15}/>Find Buyers</>
                    }
                  </button>
                  {matches[product.id] && (
                    <span style={{ padding:'4px 12px', background:'rgba(16,185,129,0.12)', border:'1px solid rgba(16,185,129,0.25)', borderRadius:99, fontSize:'0.75rem', fontWeight:700, color:'#6ee7b7' }}>
                      {matches[product.id].length} Matches
                    </span>
                  )}
                </div>
              </div>
              {/* Buyer Matches Expanded */}
              {matches[product.id] && (
                <div style={{ marginTop:'1rem', paddingTop:'1rem', borderTop:'1px solid rgba(139,92,246,0.12)' }}>
                  <h4 style={{ fontWeight:700, color:'var(--text-primary)', marginBottom:'0.75rem', fontSize:'0.9rem' }}>Matched Buyers</h4>
                  <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
                    {matches[product.id].slice(0,3).map((buyer,idx)=>(
                      <div key={idx} style={{ background:'rgba(255,255,255,0.03)', border:'1px solid rgba(139,92,246,0.13)', borderRadius:10, padding:'0.75rem', display:'flex', justifyContent:'space-between', alignItems:'center', flexWrap:'wrap', gap:8 }}>
                        <div>
                          <p style={{ fontWeight:700, color:'var(--text-primary)', margin:'0 0 3px', fontSize:'0.875rem' }}>{buyer.business_name}</p>
                          <p style={{ fontSize:'0.78rem', color:'var(--text-muted)', margin:'0 0 5px' }}>{buyer.district} • {buyer.buyer_type}</p>
                          <div style={{ display:'flex', alignItems:'center', gap:6 }}>
                            <span style={{ color:'#fcd34d', fontSize:'0.85rem' }}>★</span>
                            <span style={{ fontSize:'0.78rem', color:'var(--text-secondary)' }}>{buyer.rating}</span>
                            <span style={{ padding:'2px 8px', background:'rgba(16,185,129,0.12)', border:'1px solid rgba(16,185,129,0.25)', borderRadius:99, fontSize:'0.68rem', fontWeight:700, color:'#6ee7b7' }}>{buyer.match_score}% match</span>
                          </div>
                        </div>
                        <div style={{ textAlign:'right' }}>
                          <p style={{ fontWeight:900, color:'#a78bfa', fontSize:'1.15rem', margin:'0 0 6px' }}>₹{buyer.offer_price}</p>
                          <button style={{ padding:'5px 14px', background:'rgba(139,92,246,0.15)', border:'1px solid rgba(139,92,246,0.3)', borderRadius:8, color:'#c4b5fd', fontWeight:700, fontSize:'0.78rem', cursor:'pointer', display:'inline-flex', alignItems:'center', gap:5 }}>
                            <Handshake size={13}/> Connect
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Government Opportunities */}
      <div style={{ ...glass, padding:'1.25rem' }}>
        <h3 style={{ fontWeight:800, color:'var(--text-primary)', marginBottom:'0.9rem', fontSize:'1rem', display:'flex', alignItems:'center', gap:8 }}>
          <CheckCircle size={18} style={{ color:'#6ee7b7' }}/> Government Procurement Opportunities
        </h3>
        <p style={{ fontSize:'0.82rem', color:'var(--text-secondary)', margin:'0 0 1rem' }}>GeM Tenders matching your products are available</p>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(200px,1fr))', gap:'0.75rem' }}>
          {[
            { id:1, org:'AP Tourism', title:'Handicraft Items', budget:'₹50,000', district:'Amaravati' },
            { id:2, org:'Education Dept', title:'Pickles (Mid-Day Meal)', budget:'₹45,000', district:'Hyderabad' },
            { id:3, org:'MA&UD Dept', title:'Textile Supplies', budget:'₹80,000', district:'Hyderabad' },
          ].map(o=>(
            <div key={o.id} style={{ background:'rgba(245,158,11,0.07)', border:'1px solid rgba(245,158,11,0.2)', borderRadius:10, padding:'0.85rem' }}>
              <p style={{ fontSize:'0.72rem', fontWeight:800, color:'#f59e0b', margin:'0 0 4px', textTransform:'uppercase' }}>{o.org}</p>
              <p style={{ fontWeight:700, color:'var(--text-primary)', margin:'0 0 5px', fontSize:'0.875rem' }}>{o.title}</p>
              <p style={{ fontWeight:900, color:'#fcd34d', margin:'0 0 5px' }}>{o.budget}</p>
              <p style={{ fontSize:'0.72rem', color:'var(--text-muted)', margin:0 }}>📍 {o.district}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default BuyerMatches;
