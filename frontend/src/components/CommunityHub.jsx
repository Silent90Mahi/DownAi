import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { communityAPI } from '../services/api';
import { Users, Building2, TrendingUp, MapPin, Megaphone, BarChart3 } from 'lucide-react';

const glass = { background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: '1.25rem', backdropFilter: 'blur(16px)', WebkitBackdropFilter: 'blur(16px)' };

const CommunityHub = () => {
  const { user, isAdmin } = useAuth();
  const navigate = useNavigate();
  const [overview, setOverview] = useState(null);
  const [districtStats, setDistrictStats] = useState(null);
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('hierarchy');

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [hierarchyResp, districtResp, announcementsResp] = await Promise.all([
        communityAPI.getHierarchy().catch(() => ({ data: null })),
        isAdmin ? communityAPI.getDistrictOverview(user?.district || 'Hyderabad').catch(() => ({ data: null })) : Promise.resolve({ data: null }),
        communityAPI.getAnnouncements().catch(() => ({ data: [] })),
      ]);
      setOverview(hierarchyResp.data);
      setDistrictStats(districtResp?.data);
      setAnnouncements(announcementsResp.data);
    } catch { console.error('Failed to fetch community data'); }
    finally { setLoading(false); }
  };

  const sendAlert = async () => {
    const title = prompt('Enter alert title:');
    const message = prompt('Enter alert message:');
    const targetLevel = prompt('Target level (All, SHG, SLF, TLF):');
    if (!title || !message) return;
    try { await communityAPI.sendAlert(title, message, targetLevel, user?.district); alert('Alert sent!'); fetchData(); }
    catch (error) { alert('Failed: ' + (error.response?.data?.detail || 'Unknown error')); }
  };

  if (loading) return (
    <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
      <div style={{ width: 36, height: 36, borderRadius: '50%', border: '3px solid rgba(139,92,246,0.2)', borderTopColor: '#8b5cf6', margin: '0 auto 12px', animation: 'spin 0.7s linear infinite' }} />
      Loading community hub...
    </div>
  );

  const TABS = [['hierarchy','Hierarchy'],['announcements','Announcements'],...(isAdmin?[['admin','Admin Actions']]:[])] ;
  const statCards = [
    { icon: Users,      color: '#8b5cf6', value: districtStats?.total_shgs||0,  label:'Total SHGs' },
    { icon: TrendingUp, color: '#10b981', value: districtStats?.active_shgs||0, label:'Active SHGs' },
    { icon: Building2,  color: '#a855f7', value: districtStats?.total_products||0, label:'Products' },
    { icon: MapPin,     color: '#f59e0b', value: districtStats?.avg_trust_score?.toFixed(1)||0, label:'Avg Trust' },
  ];

  return (
    <div className="animate-fade-in" style={{ padding:'1.5rem', maxWidth:1100, margin:'0 auto', paddingBottom:'6rem' }}>
      <div style={{ marginBottom:'1.75rem' }}>
        <h1 style={{ fontSize:'1.75rem', fontWeight:900, margin:'0 0 4px', background:'linear-gradient(135deg,#f8fafc 0%,#c4b5fd 100%)', WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent', backgroundClip:'text' }}>Agent Sampark</h1>
        <p style={{ color:'var(--text-muted)', fontSize:'0.875rem', margin:0 }}>Community Orchestration & Federation</p>
      </div>

      {/* Stats */}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(150px,1fr))', gap:'0.9rem', marginBottom:'1.5rem' }}>
        {statCards.map(({ icon:Icon, color, value, label }) => (
          <div key={label} style={{ ...glass, padding:'1.1rem', textAlign:'center' }}>
            <Icon size={26} style={{ color, margin:'0 auto 8px' }} />
            <p style={{ fontWeight:900, fontSize:'1.6rem', color:'var(--text-primary)', margin:'0 0 3px' }}>{value}</p>
            <p style={{ fontSize:'0.72rem', color:'var(--text-muted)', margin:0 }}>{label}</p>
          </div>
        ))}
      </div>

      {/* Federation + District */}
      {overview && (
        <div style={{ display:'grid', gridTemplateColumns:(isAdmin&&districtStats)?'1fr 1fr':'1fr', gap:'1rem', marginBottom:'1.5rem' }}>
          <div style={{ ...glass, padding:'1.25rem' }}>
            <h3 style={{ fontWeight:800, color:'var(--text-primary)', fontSize:'1rem', marginBottom:'0.9rem', display:'flex', alignItems:'center', gap:8 }}>
              <Building2 size={18} style={{ color:'#a78bfa' }} /> Your Federation
            </h3>
            {[['Level', user?.hierarchy_level||'SHG'],['Parent Federation',overview.upstream?.length>0?overview.upstream[0].name:'None'],['Peer SHGs',overview.peers?.length||0]].map(([k,v])=>(
              <div key={k} style={{ display:'flex', justifyContent:'space-between', fontSize:'0.875rem', borderBottom:'1px solid rgba(255,255,255,0.04)', padding:'6px 0' }}>
                <span style={{ color:'var(--text-muted)' }}>{k}</span>
                <span style={{ fontWeight:600, color:'var(--text-secondary)' }}>{v}</span>
              </div>
            ))}
          </div>
          {isAdmin && districtStats && (
            <div style={{ ...glass, padding:'1.25rem' }}>
              <h3 style={{ fontWeight:800, color:'var(--text-primary)', fontSize:'1rem', marginBottom:'0.9rem', display:'flex', alignItems:'center', gap:8 }}>
                <MapPin size={18} style={{ color:'#10b981' }} /> {districtStats.district} Overview
              </h3>
              <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'0.6rem' }}>
                {[['Total SHGs',districtStats.total_shgs,'#8b5cf6'],['Active SHGs',districtStats.active_shgs,'#10b981'],['Products',districtStats.total_products,'#a855f7'],['Revenue',`₹${districtStats.total_revenue?.toLocaleString()}`,'#6ee7b7']].map(([l,v,c])=>(
                  <div key={l} style={{ background:`${c}10`, border:`1px solid ${c}25`, borderRadius:10, padding:'0.65rem' }}>
                    <p style={{ fontWeight:900, color:c, fontSize:'1.1rem', margin:'0 0 2px' }}>{v}</p>
                    <p style={{ fontSize:'0.7rem', color:'var(--text-muted)', margin:0 }}>{l}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tabs */}
      <div style={{ ...glass, overflow:'hidden' }}>
        <div style={{ display:'flex', borderBottom:'1px solid rgba(139,92,246,0.15)' }}>
          {TABS.map(([id,label])=>(
            <button key={id} onClick={()=>setActiveTab(id)} style={{ flex:1, padding:'0.9rem', fontSize:'0.875rem', fontWeight:600, cursor:'pointer', border:'none', background:'transparent', color:activeTab===id?'#c4b5fd':'var(--text-muted)', borderBottom:activeTab===id?'2px solid #8b5cf6':'2px solid transparent', transition:'all 0.2s' }}>
              {label}
            </button>
          ))}
        </div>
        <div style={{ padding:'1.25rem' }}>
          {activeTab==='hierarchy' && overview && (
            <div>
              <h3 style={{ fontWeight:700, color:'var(--text-primary)', marginBottom:'1rem', fontSize:'1rem' }}>Federation Structure</h3>
              {overview.upstream?.length>0 && (
                <div style={{ marginBottom:'1rem' }}>
                  <p style={{ fontSize:'0.78rem', fontWeight:600, color:'var(--text-muted)', marginBottom:8 }}>Parent Federation</p>
                  <div style={{ background:'rgba(59,130,246,0.08)', border:'1px solid rgba(59,130,246,0.2)', borderRadius:10, padding:'0.75rem' }}>
                    <p style={{ fontWeight:700, color:'#93c5fd', margin:'0 0 3px' }}>{overview.upstream[0].name}</p>
                    <p style={{ fontSize:'0.78rem', color:'var(--text-muted)', margin:0 }}>{overview.upstream[0].level} • {overview.upstream[0].district}</p>
                  </div>
                </div>
              )}
              {overview.downstream?.length>0 && (
                <div style={{ marginBottom:'0.9rem' }}>
                  <p style={{ fontSize:'0.78rem', fontWeight:600, color:'var(--text-muted)', marginBottom:8 }}>Child SHGs ({overview.downstream.length})</p>
                  <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(170px,1fr))', gap:8 }}>
                    {overview.downstream.map(m=>(
                      <div key={m.id} style={{ background:'rgba(255,255,255,0.03)', border:'1px solid rgba(139,92,246,0.15)', borderRadius:10, padding:'0.65rem' }}>
                        <p style={{ fontWeight:600, color:'var(--text-primary)', margin:'0 0 3px', fontSize:'0.875rem' }}>{m.name}</p>
                        <p style={{ fontSize:'0.75rem', color:'var(--text-muted)', margin:'0 0 5px' }}>{m.district}</p>
                        <span style={{ fontSize:'0.75rem', fontWeight:700, color:'#a78bfa' }}>★ {m.trust_score}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {overview.peers?.length>0 && (
                <div>
                  <p style={{ fontSize:'0.78rem', fontWeight:600, color:'var(--text-muted)', marginBottom:8 }}>Peer SHGs ({overview.peers.length})</p>
                  <div style={{ display:'flex', flexWrap:'wrap', gap:6 }}>
                    {overview.peers.map(p=><span key={p.id} style={{ padding:'3px 10px', background:'rgba(139,92,246,0.12)', border:'1px solid rgba(139,92,246,0.25)', borderRadius:99, fontSize:'0.72rem', fontWeight:600, color:'#c4b5fd' }}>{p.name}</span>)}
                  </div>
                </div>
              )}
            </div>
          )}
          {activeTab==='announcements' && (
            <div>
              <h3 style={{ fontWeight:700, color:'var(--text-primary)', marginBottom:'1rem', fontSize:'1rem' }}>Community Announcements</h3>
              {announcements.length===0 ? (
                <p style={{ textAlign:'center', color:'var(--text-muted)', padding:'2rem 0' }}>No announcements yet</p>
              ) : (
                <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
                  {announcements.map((a,idx)=>(
                    <div key={idx} style={{ background:'rgba(245,158,11,0.07)', border:'1px solid rgba(245,158,11,0.2)', borderRadius:10, padding:'0.9rem' }}>
                      <p style={{ fontSize:'0.7rem', fontWeight:800, color:'#f59e0b', margin:'0 0 4px', textTransform:'uppercase' }}>{a.type}</p>
                      <h4 style={{ fontWeight:700, color:'var(--text-primary)', margin:'0 0 6px', fontSize:'0.9rem' }}>{a.title}</h4>
                      <p style={{ fontSize:'0.82rem', color:'var(--text-secondary)', margin:'0 0 5px' }}>{a.message}</p>
                      <p style={{ fontSize:'0.72rem', color:'var(--text-muted)', margin:0 }}>Valid until: {new Date(a.valid_until).toLocaleDateString()}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
          {activeTab==='admin' && isAdmin && (
            <div>
              <h3 style={{ fontWeight:700, color:'var(--text-primary)', marginBottom:'1rem', fontSize:'1rem' }}>Admin Actions</h3>
              <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
                <button onClick={sendAlert} style={{ padding:'0.75rem', background:'linear-gradient(135deg,#7c3aed,#a855f7)', border:'none', borderRadius:10, color:'#fff', fontWeight:700, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:8, boxShadow:'0 4px 14px rgba(139,92,246,0.35)' }}>
                  <Megaphone size={18}/> Send Community Alert
                </button>
                <button onClick={()=>navigate('/reports')} style={{ padding:'0.75rem', background:'rgba(16,185,129,0.1)', border:'1px solid rgba(16,185,129,0.3)', borderRadius:10, color:'#6ee7b7', fontWeight:700, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>
                  <BarChart3 size={18}/> View Reports
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CommunityHub;
