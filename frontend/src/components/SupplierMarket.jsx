import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { suppliersAPI } from '../services/api';
import { Search, ShoppingCart, Leaf } from 'lucide-react';

const glass = { background:'rgba(255,255,255,0.04)', border:'1px solid rgba(139,92,246,0.2)', borderRadius:'1.1rem', backdropFilter:'blur(16px)', WebkitBackdropFilter:'blur(16px)' };
const selectStyle = { padding:'0.6rem 0.9rem', background:'rgba(255,255,255,0.06)', border:'1px solid rgba(139,92,246,0.22)', borderRadius:10, outline:'none', color:'var(--text-secondary)', fontSize:'0.875rem', cursor:'pointer' };

const SupplierMarket = () => {
  const navigate = useNavigate();
  const [materials, setMaterials] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedDistrict, setSelectedDistrict] = useState('All');

  const categories = ['All','Agriculture','Textile','Handicrafts','Food Processing','Packaging'];
  const districts  = ['All','Hyderabad','Guntur','Rajahmundry','Kurnool'];

  useEffect(() => { fetchMaterials(); }, [searchTerm, selectedCategory, selectedDistrict]);

  const fetchMaterials = async () => {
    try {
      setLoading(true);
      const r = await suppliersAPI.search({ query:searchTerm||'raw materials', category:selectedCategory==='All'?null:selectedCategory, district:selectedDistrict==='All'?null:selectedDistrict });
      setMaterials(r.data);
    } catch { setMaterials([]); }
    finally { setLoading(false); }
  };

  return (
    <div className="animate-fade-in" style={{ padding:'1.5rem', maxWidth:1100, margin:'0 auto', paddingBottom:'6rem' }}>
      <div style={{ marginBottom:'1.75rem' }}>
        <h1 style={{ fontSize:'1.75rem', fontWeight:900, margin:'0 0 4px', background:'linear-gradient(135deg,#f8fafc 0%,#c4b5fd 100%)', WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent', backgroundClip:'text' }}>Agent Samagri</h1>
        <p style={{ color:'var(--text-muted)', fontSize:'0.875rem', margin:0 }}>Raw Material Procurement Marketplace</p>
      </div>

      {/* Search Bar */}
      <div style={{ ...glass, padding:'1rem', display:'flex', flexWrap:'wrap', gap:'0.75rem', marginBottom:'1.25rem', alignItems:'center' }}>
        <div style={{ flex:1, minWidth:200, position:'relative' }}>
          <Search size={16} style={{ position:'absolute', left:12, top:'50%', transform:'translateY(-50%)', color:'var(--text-muted)' }}/>
          <input
            type="text" value={searchTerm} onChange={e=>setSearchTerm(e.target.value)}
            placeholder="Search for raw materials..."
            style={{ width:'100%', paddingLeft:38, paddingRight:12, paddingTop:'0.6rem', paddingBottom:'0.6rem', background:'rgba(255,255,255,0.06)', border:'1px solid rgba(139,92,246,0.22)', borderRadius:10, outline:'none', color:'var(--text-primary)', fontSize:'0.875rem' }}
          />
        </div>
        <select value={selectedCategory} onChange={e=>setSelectedCategory(e.target.value)} style={selectStyle}>
          {categories.map(c=><option key={c} value={c}>{c}</option>)}
        </select>
        <select value={selectedDistrict} onChange={e=>setSelectedDistrict(e.target.value)} style={selectStyle}>
          {districts.map(d=><option key={d} value={d}>{d}</option>)}
        </select>
      </div>

      {/* Bulk CTA */}
      <div style={{ background:'linear-gradient(135deg,rgba(16,185,129,0.15) 0%,rgba(139,92,246,0.1) 100%)', border:'1px solid rgba(16,185,129,0.25)', borderRadius:'1rem', padding:'1.1rem 1.5rem', marginBottom:'1.25rem', display:'flex', justifyContent:'space-between', alignItems:'center', flexWrap:'wrap', gap:12 }}>
        <div>
          <h3 style={{ fontWeight:800, color:'#6ee7b7', margin:'0 0 3px', fontSize:'1rem' }}>💰 Save More with Bulk Purchasing</h3>
          <p style={{ color:'var(--text-secondary)', margin:0, fontSize:'0.85rem' }}>Join other SHGs to buy in bulk and save 15–25%</p>
        </div>
        <button onClick={()=>navigate('/bulk-requests')} style={{ padding:'0.55rem 1.1rem', background:'rgba(16,185,129,0.15)', border:'1px solid rgba(16,185,129,0.3)', borderRadius:10, color:'#6ee7b7', fontWeight:700, fontSize:'0.875rem', cursor:'pointer' }}>
          View Bulk Requests
        </button>
      </div>

      {/* Materials Grid */}
      {loading ? (
        <div style={{ textAlign:'center', padding:'3rem', color:'var(--text-muted)' }}>
          <div style={{ width:36,height:36,borderRadius:'50%',border:'3px solid rgba(139,92,246,0.2)',borderTopColor:'#8b5cf6',margin:'0 auto 12px',animation:'spin 0.7s linear infinite' }}/>Loading...
        </div>
      ) : materials.length===0 ? (
        <div style={{ textAlign:'center', padding:'3rem', ...glass }}>
          <Search size={48} style={{ color:'rgba(139,92,246,0.25)', margin:'0 auto 12px' }}/>
          <p style={{ fontWeight:600, color:'var(--text-muted)', margin:'0 0 5px' }}>No materials found</p>
          <p style={{ fontSize:'0.85rem', color:'var(--text-muted)', margin:0 }}>Try adjusting your search filters</p>
        </div>
      ) : (
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(260px,1fr))', gap:'0.9rem', marginBottom:'1.25rem' }}>
          {materials.map(m=>(
            <div key={m.id} style={{ ...glass, overflow:'hidden', transition:'all 0.3s' }}
              onMouseEnter={e=>{e.currentTarget.style.border='1px solid rgba(139,92,246,0.4)';e.currentTarget.style.transform='translateY(-3px)';}}
              onMouseLeave={e=>{e.currentTarget.style.border='1px solid rgba(139,92,246,0.2)';e.currentTarget.style.transform='translateY(0)';}}>
              <div style={{ height:130, background:'linear-gradient(135deg,rgba(139,92,246,0.1),rgba(16,185,129,0.06))', display:'flex', alignItems:'center', justifyContent:'center' }}>
                <Leaf size={44} style={{ color:'rgba(16,185,129,0.4)' }}/>
              </div>
              <div style={{ padding:'1rem' }}>
                <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:8 }}>
                  <div>
                    <h3 style={{ fontWeight:800, color:'var(--text-primary)', margin:'0 0 3px', fontSize:'0.95rem' }}>{m.name}</h3>
                    <p style={{ fontSize:'0.78rem', color:'var(--text-muted)', margin:0 }}>{m.category}</p>
                  </div>
                  {m.is_organic && <span style={{ padding:'2px 8px', background:'rgba(16,185,129,0.12)', border:'1px solid rgba(16,185,129,0.25)', borderRadius:99, fontSize:'0.68rem', fontWeight:800, color:'#6ee7b7', whiteSpace:'nowrap' }}>Organic</span>}
                </div>
                <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:8 }}>
                  <div>
                    <p style={{ fontWeight:900, color:'#a78bfa', fontSize:'1.2rem', margin:0 }}>₹{m.price_per_unit}</p>
                    <p style={{ fontSize:'0.7rem', color:'var(--text-muted)', margin:0 }}>per {m.unit}</p>
                  </div>
                  {m.bulk_discount_available && <span style={{ padding:'2px 8px', background:'rgba(245,158,11,0.12)', border:'1px solid rgba(245,158,11,0.25)', borderRadius:99, fontSize:'0.7rem', fontWeight:700, color:'#fcd34d' }}>{m.bulk_discount_percentage}% off bulk</span>}
                </div>
                <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', fontSize:'0.78rem', color:'var(--text-muted)', marginBottom:10 }}>
                  <span>{m.supplier?.business_name} • {m.district}</span>
                  <span>Stock: {m.stock_available}</span>
                </div>
                <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:10 }}>
                  <span style={{ color:'#fcd34d', fontSize:'0.9rem' }}>{'★'.repeat(Math.round(m.supplier?.rating||0))}</span>
                  <span style={{ fontSize:'0.72rem', color:'var(--text-muted)' }}>({m.supplier?.total_reviews||0} reviews)</span>
                </div>
                <button onClick={()=>{}} style={{ width:'100%', padding:'0.65rem', background:'linear-gradient(135deg,#7c3aed,#a855f7)', border:'none', borderRadius:8, color:'#fff', fontWeight:700, fontSize:'0.85rem', cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:7, boxShadow:'0 3px 10px rgba(139,92,246,0.3)' }}>
                  <ShoppingCart size={15}/> Inquire
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Price Trends */}
      <div style={{ background:'rgba(59,130,246,0.07)', border:'1px solid rgba(59,130,246,0.2)', borderRadius:'1rem', padding:'1rem 1.25rem', display:'flex', justifyContent:'space-between', alignItems:'center', flexWrap:'wrap', gap:10 }}>
        <div>
          <h4 style={{ fontWeight:700, color:'#93c5fd', margin:'0 0 3px', fontSize:'0.95rem' }}>Track Price Trends</h4>
          <p style={{ fontSize:'0.8rem', color:'var(--text-secondary)', margin:0 }}>See price history for materials before buying</p>
        </div>
        <button style={{ padding:'6px 14px', background:'rgba(59,130,246,0.12)', border:'1px solid rgba(59,130,246,0.25)', borderRadius:8, color:'#93c5fd', fontWeight:700, fontSize:'0.8rem', cursor:'pointer' }}>View Trends</button>
      </div>
    </div>
  );
};

export default SupplierMarket;
