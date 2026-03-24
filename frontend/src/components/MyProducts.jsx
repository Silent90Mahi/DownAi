import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { productsAPI } from '../services/api';
import { Package, Edit, Trash2, Plus, Eye, TrendingUp, IndianRupee } from 'lucide-react';

const STAT_CONF = [
  { label:'Total Listings', key:null,       fn:p=>p.length,                                       icon:Package,    color:'#8b5cf6' },
  { label:'Available',      key:'Available', fn:p=>p.filter(x=>x.status==='Available').length,     icon:TrendingUp, color:'#10b981' },
  { label:'Total Value',    key:null,        fn:p=>`₹${p.reduce((s,x)=>s+(x.price*x.quantity||0),0).toLocaleString()}`, icon:IndianRupee, color:'#a78bfa', accent:true },
  { label:'Sold Out',       key:'Sold Out',  fn:p=>p.filter(x=>x.status==='Sold Out').length,      icon:Package,    color:'#f87171' },
];
const STATUS_MAP = { Available:['rgba(16,185,129,0.12)','rgba(16,185,129,0.3)','#6ee7b7'], 'Sold Out':['rgba(239,68,68,0.12)','rgba(239,68,68,0.3)','#fca5a5'], Pending:['rgba(245,158,11,0.12)','rgba(245,158,11,0.3)','#fcd34d'] };

const MyProducts = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => { fetchMyProducts(); }, [filter]);

  const fetchMyProducts = async () => {
    try {
      setLoading(true);
      const r = await productsAPI.getAll(filter==='all' ? null : filter);
      setProducts(r.data.filter(p=>p.seller_id===user?.id));
    } catch { console.error('Failed to fetch products'); }
    finally { setLoading(false); }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this product?')) return;
    try { await productsAPI.delete(id); setProducts(p=>p.filter(x=>x.id!==id)); }
    catch (e) { alert('Failed: '+(e.response?.data?.detail||'Unknown error')); }
  };

  if (loading) return (
    <div style={{ textAlign:'center', padding:'3rem', color:'var(--text-muted)' }}>
      <div style={{ width:36,height:36,borderRadius:'50%',border:'3px solid rgba(139,92,246,0.2)',borderTopColor:'#8b5cf6',margin:'0 auto 12px',animation:'spin 0.7s linear infinite' }}/>
      Loading products...
    </div>
  );

  return (
    <div className="animate-fade-in" style={{ padding:'1.5rem', maxWidth:1100, margin:'0 auto', paddingBottom:'6rem' }}>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:'1.75rem', flexWrap:'wrap', gap:'1rem' }}>
        <div>
          <h1 style={{ fontSize:'1.75rem', fontWeight:900, margin:'0 0 4px', background:'linear-gradient(135deg,#f8fafc 0%,#c4b5fd 100%)', WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent', backgroundClip:'text' }}>My Products</h1>
          <p style={{ color:'var(--text-muted)', fontSize:'0.875rem', margin:0 }}>Manage your product listings</p>
        </div>
        <button onClick={()=>navigate('/sell')} style={{ display:'flex', alignItems:'center', gap:6, padding:'0.55rem 1.1rem', background:'linear-gradient(135deg,#7c3aed,#a855f7)', border:'none', borderRadius:10, cursor:'pointer', color:'#fff', fontWeight:700, fontSize:'0.875rem', boxShadow:'0 4px 12px rgba(139,92,246,0.35)' }}>
          <Plus size={16}/> Add New Product
        </button>
      </div>

      {/* Stats */}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(150px,1fr))', gap:'0.9rem', marginBottom:'1.5rem' }}>
        {STAT_CONF.map(({ label, icon:Icon, color, fn }) => (
          <div key={label} style={{ background:`${color}0a`, border:`1px solid ${color}22`, borderRadius:'1rem', padding:'1.1rem', backdropFilter:'blur(12px)' }}>
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
              <div>
                <p style={{ fontSize:'0.72rem', fontWeight:600, color:'var(--text-muted)', margin:'0 0 4px' }}>{label}</p>
                <p style={{ fontWeight:900, fontSize:'1.6rem', color, margin:0 }}>{fn(products)}</p>
              </div>
              <Icon size={26} style={{ color, opacity:0.6 }}/>
            </div>
          </div>
        ))}
      </div>

      {/* Filter Pills */}
      <div style={{ display:'flex', gap:8, overflowX:'auto', paddingBottom:4, marginBottom:'1.25rem' }}>
        {['all','Available','Sold Out','Pending'].map(s=>{
          const active = filter===s;
          return (
            <button key={s} onClick={()=>setFilter(s)} style={{ padding:'6px 16px', borderRadius:99, border:active?'1px solid rgba(139,92,246,0.5)':'1px solid rgba(255,255,255,0.08)', background:active?'rgba(139,92,246,0.2)':'rgba(255,255,255,0.04)', color:active?'#c4b5fd':'var(--text-muted)', fontWeight:600, fontSize:'0.8rem', cursor:'pointer', whiteSpace:'nowrap', transition:'all 0.2s', boxShadow:active?'0 0 10px rgba(139,92,246,0.2)':'none' }}>
              {s==='all'?'All Products':s}
            </button>
          );
        })}
      </div>

      {products.length===0 ? (
        <div style={{ textAlign:'center', padding:'3rem', background:'rgba(255,255,255,0.03)', border:'1px solid rgba(139,92,246,0.12)', borderRadius:'1.25rem' }}>
          <Package size={48} style={{ color:'rgba(139,92,246,0.25)', margin:'0 auto 12px' }}/>
          <p style={{ fontWeight:600, color:'var(--text-muted)', margin:'0 0 8px' }}>No products listed yet</p>
          <p style={{ fontSize:'0.85rem', color:'var(--text-muted)', margin:'0 0 1.25rem' }}>Start by adding your first product</p>
          <button onClick={()=>navigate('/sell')} style={{ display:'inline-flex', alignItems:'center', gap:7, padding:'0.55rem 1.25rem', background:'linear-gradient(135deg,#7c3aed,#a855f7)', border:'none', borderRadius:10, color:'#fff', fontWeight:700, cursor:'pointer' }}>
            <Plus size={16}/> Add Your First Product
          </button>
        </div>
      ) : (
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(260px,1fr))', gap:'0.9rem' }}>
          {products.map(product=>{
            const smap = STATUS_MAP[product.status]||['rgba(255,255,255,0.06)','rgba(255,255,255,0.1)','var(--text-muted)'];
            return (
              <div key={product.id} style={{ background:'rgba(255,255,255,0.04)', border:'1px solid rgba(139,92,246,0.18)', borderRadius:'1rem', overflow:'hidden', backdropFilter:'blur(12px)', transition:'all 0.3s' }}
                onMouseEnter={e=>{e.currentTarget.style.border='1px solid rgba(139,92,246,0.4)';e.currentTarget.style.transform='translateY(-3px)';}}
                onMouseLeave={e=>{e.currentTarget.style.border='1px solid rgba(139,92,246,0.18)';e.currentTarget.style.transform='translateY(0)';}}>
                {/* Image */}
                <div style={{ position:'relative', height:160 }}>
                  {product.image_url
                    ? <img src={product.image_url} alt={product.name} style={{ width:'100%', height:'100%', objectFit:'cover' }}/>
                    : <div style={{ width:'100%', height:'100%', background:'linear-gradient(135deg,rgba(139,92,246,0.12),rgba(168,85,247,0.08))', display:'flex', alignItems:'center', justifyContent:'center' }}><Package size={44} style={{ color:'rgba(139,92,246,0.3)' }}/></div>
                  }
                  <span style={{ position:'absolute', top:10, right:10, padding:'3px 10px', borderRadius:99, fontSize:'0.68rem', fontWeight:800, background:smap[0], border:`1px solid ${smap[1]}`, color:smap[2] }}>{product.status}</span>
                </div>
                {/* Info */}
                <div style={{ padding:'1rem' }}>
                  <p style={{ fontSize:'0.7rem', fontWeight:700, color:'var(--text-muted)', textTransform:'uppercase', letterSpacing:'0.07em', margin:'0 0 4px' }}>{product.category}</p>
                  <h3 style={{ fontWeight:800, color:'var(--text-primary)', margin:'0 0 5px', fontSize:'0.95rem', display:'-webkit-box', WebkitLineClamp:2, WebkitBoxOrient:'vertical', overflow:'hidden' }}>{product.name}</h3>
                  <p style={{ fontSize:'0.78rem', color:'var(--text-muted)', margin:'0 0 10px', display:'-webkit-box', WebkitLineClamp:1, WebkitBoxOrient:'vertical', overflow:'hidden' }}>{product.description||'No description'}</p>
                  <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', paddingBottom:10, borderBottom:'1px solid rgba(255,255,255,0.05)', marginBottom:10 }}>
                    <div>
                      <p style={{ fontWeight:900, color:'#a78bfa', fontSize:'1.1rem', margin:0 }}>₹{product.price?.toLocaleString()}</p>
                      <p style={{ fontSize:'0.7rem', color:'var(--text-muted)', margin:0 }}>per {product.unit}</p>
                    </div>
                    <div style={{ textAlign:'right' }}>
                      <p style={{ fontWeight:700, color:'var(--text-secondary)', margin:0, fontSize:'0.875rem' }}>{product.quantity} {product.unit}</p>
                      <p style={{ fontSize:'0.7rem', color:'var(--text-muted)', margin:0 }}>In Stock</p>
                    </div>
                  </div>
                  {/* Actions */}
                  <div style={{ display:'flex', gap:6 }}>
                    <button onClick={()=>navigate(`/products/${product.id}`)} style={{ flex:1, padding:'6px', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.08)', borderRadius:8, color:'var(--text-muted)', fontWeight:600, fontSize:'0.75rem', cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:4 }}>
                      <Eye size={13}/> View
                    </button>
                    <button onClick={()=>navigate(`/products/${product.id}/edit`)} style={{ flex:1, padding:'6px', background:'rgba(59,130,246,0.1)', border:'1px solid rgba(59,130,246,0.2)', borderRadius:8, color:'#93c5fd', fontWeight:600, fontSize:'0.75rem', cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:4 }}>
                      <Edit size={13}/> Edit
                    </button>
                    <button onClick={()=>handleDelete(product.id)} style={{ padding:'6px 10px', background:'rgba(239,68,68,0.1)', border:'1px solid rgba(239,68,68,0.2)', borderRadius:8, color:'#fca5a5', cursor:'pointer', display:'flex', alignItems:'center' }}>
                      <Trash2 size={14}/>
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default MyProducts;
