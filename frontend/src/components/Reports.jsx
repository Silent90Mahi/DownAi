import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { analyticsAPI } from '../services/api';
import { BarChart3, Download, FileText, Calendar, TrendingUp, Users, Package, Building2, MapPin } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip } from 'recharts';

const glass = { background:'rgba(255,255,255,0.04)', border:'1px solid rgba(139,92,246,0.2)', borderRadius:'1.1rem', backdropFilter:'blur(16px)', WebkitBackdropFilter:'blur(16px)' };

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background:'rgba(13,10,26,0.97)', border:'1px solid rgba(139,92,246,0.3)', borderRadius:8, padding:'0.6rem 0.9rem' }}>
      <p style={{ color:'var(--text-muted)', fontSize:'0.75rem', margin:'0 0 4px' }}>{label}</p>
      <p style={{ color:'#a78bfa', fontWeight:800, margin:0 }}>₹{payload[0].value?.toLocaleString()}</p>
    </div>
  );
};

const Reports = () => {
  const { user, isAdmin } = useAuth();
  const [dashboardStats, setDashboardStats] = useState(null);
  const [districtStats, setDistrictStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    if (!isAdmin) { window.location.href='/'; return; }
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const [dr, dsr] = await Promise.all([
        analyticsAPI.getDashboard().catch(()=>({ data:null })),
        analyticsAPI.getDistrictStats().catch(()=>({ data:[] })),
      ]);
      setDashboardStats(dr.data);
      setDistrictStats(dsr.data);
    } catch { console.error('Failed to fetch reports'); }
    finally { setLoading(false); }
  };

  const handleGenerateReport = async (type) => {
    try {
      setGenerating(true);
      await analyticsAPI.generate(type);
      alert('Report generated! (In production, this would download a file)');
    } catch (e) { alert('Failed: '+(e.response?.data?.detail||'Unknown error')); }
    finally { setGenerating(false); }
  };

  if (!isAdmin) return null;

  const STAT_CARDS = [
    { label:'Total Users',    value:dashboardStats?.total_users,                     icon:Users,    grad:'from-[#7c3aed] to-[#a855f7]', glow:'rgba(139,92,246,0.3)' },
    { label:'Active Users',   value:dashboardStats?.active_users,                    icon:TrendingUp,grad:'from-[#10b981] to-[#059669]', glow:'rgba(16,185,129,0.25)' },
    { label:'Active Listings',value:dashboardStats?.active_listings,                  icon:Package,  grad:'from-[#a855f7] to-[#7c3aed]', glow:'rgba(168,85,247,0.25)' },
    { label:'Total Revenue',  value:`₹${dashboardStats?.total_revenue?.toLocaleString()||0}`, icon:BarChart3, grad:'from-[#0ea5e9] to-[#7c3aed]', glow:'rgba(14,165,233,0.2)' },
  ];

  const REPORT_CARDS = [
    { type:'user',       icon:FileText,  color:'#60a5fa', bg:'rgba(59,130,246,0.1)',   border:'rgba(59,130,246,0.25)', title:'User Report',       sub:'Individual SHG performance' },
    { type:'federation', icon:Building2, color:'#6ee7b7', bg:'rgba(16,185,129,0.1)',  border:'rgba(16,185,129,0.25)', title:'Federation Report',  sub:'Aggregate federation data' },
    { type:'district',   icon:MapPin,    color:'#fcd34d', bg:'rgba(245,158,11,0.1)',  border:'rgba(245,158,11,0.25)', title:'District Report',    sub:'District-wise analytics' },
  ];

  const AGENT_METRICS = [
    { label:'Vaani Queries',   key:'vaani_interactions', color:'#a78bfa' },
    { label:'Bazaar Queries',  key:'bazaar_queries',     color:'#fcd34d' },
    { label:'Jodi Matches',    key:'jodi_matches',       color:'#60a5fa' },
    { label:'Samagri Searches',key:'samagri_searches',   color:'#6ee7b7' },
  ];

  if (loading) return (
    <div style={{ textAlign:'center', padding:'3rem', color:'var(--text-muted)' }}>
      <div style={{ width:36,height:36,borderRadius:'50%',border:'3px solid rgba(139,92,246,0.2)',borderTopColor:'#8b5cf6',margin:'0 auto 12px',animation:'spin 0.7s linear infinite' }}/>
      Loading reports...
    </div>
  );

  return (
    <div className="animate-fade-in" style={{ padding:'1.5rem', maxWidth:1100, margin:'0 auto', paddingBottom:'6rem' }}>
      <div style={{ marginBottom:'1.75rem' }}>
        <h1 style={{ fontSize:'1.75rem', fontWeight:900, margin:'0 0 4px', background:'linear-gradient(135deg,#f8fafc 0%,#c4b5fd 100%)', WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent', backgroundClip:'text' }}>Analytics & Reports</h1>
        <p style={{ color:'var(--text-muted)', fontSize:'0.875rem', margin:0 }}>Admin Dashboard — Comprehensive Ecosystem View</p>
      </div>

      {/* Stats */}
      {dashboardStats && (
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(180px,1fr))', gap:'0.9rem', marginBottom:'1.5rem' }}>
          {STAT_CARDS.map(({ label, value, icon:Icon, grad, glow }) => (
            <div key={label} style={{ background:`linear-gradient(135deg,${grad.replace('from-[','').replace('] to-[','_').replace(']','').split('_').map(c=>`${c}30`).join(',')})`, border:'1px solid rgba(139,92,246,0.2)', borderRadius:'1rem', padding:'1.25rem', boxShadow:`0 6px 20px ${glow}` }}>
              <Icon size={28} style={{ color:'rgba(255,255,255,0.7)', marginBottom:8 }}/>
              <p style={{ fontWeight:900, fontSize:'2rem', color:'#fff', margin:'0 0 4px' }}>{value}</p>
              <p style={{ fontSize:'0.78rem', color:'rgba(255,255,255,0.7)', margin:0 }}>{label}</p>
            </div>
          ))}
        </div>
      )}

      {/* Charts */}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(320px,1fr))', gap:'1rem', marginBottom:'1.5rem' }}>
        <div style={{ ...glass, padding:'1.25rem' }}>
          <h3 style={{ fontWeight:700, color:'var(--text-primary)', marginBottom:'1rem', fontSize:'0.95rem' }}>District Performance</h3>
          {districtStats.length>0 ? (
            <div style={{ height:220 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={districtStats}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.06)"/>
                  <XAxis dataKey="district" tick={{ fontSize:11, fill:'var(--text-muted)' }} stroke="rgba(255,255,255,0.1)"/>
                  <YAxis tick={{ fontSize:11, fill:'var(--text-muted)' }} stroke="rgba(255,255,255,0.1)"/>
                  <Tooltip content={<CustomTooltip/>}/>
                  <Bar dataKey="total_revenue" fill="url(#purpleGrad)" radius={[4,4,0,0]}/>
                  <defs>
                    <linearGradient id="purpleGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#a855f7"/>
                      <stop offset="100%" stopColor="#7c3aed"/>
                    </linearGradient>
                  </defs>
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p style={{ textAlign:'center', color:'var(--text-muted)', padding:'2rem 0' }}>No district data available</p>
          )}
        </div>

        <div style={{ ...glass, padding:'1.25rem', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center' }}>
          <h3 style={{ fontWeight:700, color:'var(--text-primary)', marginBottom:'1.25rem', fontSize:'0.95rem', alignSelf:'flex-start' }}>Trust Score Distribution</h3>
          {dashboardStats && (
            <div style={{ textAlign:'center' }}>
              <div style={{ position:'relative', display:'inline-flex', alignItems:'center', justifyContent:'center', marginBottom:16 }}>
                <svg width={160} height={160} viewBox="0 0 36 36">
                  <circle cx="18" cy="18" r="15" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="3"/>
                  <circle cx="18" cy="18" r="15" fill="none" stroke="url(#ringGrad)" strokeWidth="3" strokeDasharray={`${(dashboardStats.avg_trust_score||0)*0.943} 100`} strokeLinecap="round" transform="rotate(-90 18 18)"/>
                  <defs>
                    <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="#7c3aed"/>
                      <stop offset="100%" stopColor="#a855f7"/>
                    </linearGradient>
                  </defs>
                </svg>
                <div style={{ position:'absolute', textAlign:'center' }}>
                  <p style={{ fontWeight:900, fontSize:'1.4rem', color:'#c4b5fd', margin:0 }}>{dashboardStats.avg_trust_score?.toFixed(1)}</p>
                </div>
              </div>
              <p style={{ color:'var(--text-muted)', fontSize:'0.8rem', margin:0 }}>Average Trust Score</p>
            </div>
          )}
        </div>
      </div>

      {/* Generate Reports */}
      <div style={{ ...glass, padding:'1.5rem', marginBottom:'1.25rem' }}>
        <h3 style={{ fontWeight:700, color:'var(--text-primary)', marginBottom:'1rem', fontSize:'0.95rem' }}>Generate Reports</h3>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(180px,1fr))', gap:'0.75rem', marginBottom:'1rem' }}>
          {REPORT_CARDS.map(({ type, icon:Icon, color, bg, border, title, sub }) => (
            <button key={type} onClick={()=>handleGenerateReport(type)} disabled={generating}
              style={{ background:bg, border:`1px solid ${border}`, borderRadius:10, padding:'1rem', textAlign:'left', cursor:'pointer', transition:'all 0.2s', opacity:generating?0.6:1 }}>
              <Icon size={26} style={{ color, marginBottom:8 }}/>
              <p style={{ fontWeight:700, color, margin:'0 0 3px', fontSize:'0.875rem' }}>{title}</p>
              <p style={{ fontSize:'0.75rem', color:'var(--text-muted)', margin:0 }}>{sub}</p>
            </button>
          ))}
        </div>
        <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', padding:'0.9rem', background:'rgba(255,255,255,0.03)', borderRadius:10, border:'1px solid rgba(255,255,255,0.06)' }}>
          <div>
            <h4 style={{ fontWeight:700, color:'var(--text-primary)', margin:'0 0 3px', fontSize:'0.875rem' }}>Export Options</h4>
            <p style={{ fontSize:'0.78rem', color:'var(--text-muted)', margin:0 }}>Download reports as PDF or CSV</p>
          </div>
          <Download size={24} style={{ color:'var(--text-muted)' }}/>
        </div>
      </div>

      {/* Agent Metrics */}
      {dashboardStats?.agent_metrics && (
        <div style={{ ...glass, padding:'1.25rem' }}>
          <h3 style={{ fontWeight:700, color:'var(--text-primary)', marginBottom:'1rem', fontSize:'0.95rem' }}>Agent Usage Metrics</h3>
          <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(160px,1fr))', gap:'0.75rem' }}>
            {AGENT_METRICS.map(({ label, key, color }) => (
              <div key={key} style={{ background:`${color}0f`, border:`1px solid ${color}25`, borderRadius:10, padding:'0.9rem', textAlign:'center' }}>
                <p style={{ fontWeight:900, fontSize:'1.6rem', color, margin:'0 0 4px' }}>{dashboardStats.agent_metrics[key]||0}</p>
                <p style={{ fontSize:'0.72rem', color:'var(--text-muted)', margin:0 }}>{label}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Reports;
