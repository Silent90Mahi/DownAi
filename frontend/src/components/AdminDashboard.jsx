import { useState, useEffect } from 'react';
import { Users, Activity, ShieldCheck, FileText, BarChart, TrendingUp } from 'lucide-react';
import { analyticsAPI, trustAPI } from '../services/api';

const glass = { background:'rgba(255,255,255,0.04)', border:'1px solid rgba(139,92,246,0.2)', borderRadius:'1.25rem', backdropFilter:'blur(16px)', WebkitBackdropFilter:'blur(16px)' };

const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchAdminData(); }, []);

  const fetchAdminData = async () => {
    try {
      setLoading(true);
      const [statsResp, logsResp] = await Promise.all([
        analyticsAPI.getDashboard().catch(()=>({ data:null })),
        trustAPI.getAuditLogs(20).catch(()=>({ data:[] }))
      ]);
      if (statsResp.data) {
        setStats({ totalShgs:statsResp.data.total_users||0, avgTrustScore:statsResp.data.avg_trust_score||0, totalVolume:statsResp.data.total_revenue?`₹${(statsResp.data.total_revenue/10000000).toFixed(1)} Cr`:'₹ 0', activeTransactions:statsResp.data.active_listings||0 });
      }
      if (logsResp.data) {
        setLogs(logsResp.data.map((log,idx)=>({ id:`LOG-${String(idx+1).padStart(3,'0')}`, agent:log.agent_name||'Vishwas', action:log.action||'Audit Log', details:log.details||log.description||'System update', time:log.created_at?new Date(log.created_at).toLocaleString():'Just now' })));
      }
    } catch {
      setStats({ totalShgs:0, avgTrustScore:0, totalVolume:'₹ 0', activeTransactions:0 });
    } finally { setLoading(false); }
  };

  if (loading) return (
    <div style={{ textAlign:'center', padding:'3rem', color:'var(--text-muted)' }}>
      <div style={{ width:36,height:36,borderRadius:'50%',border:'3px solid rgba(139,92,246,0.2)',borderTopColor:'#8b5cf6',margin:'0 auto 12px',animation:'spin 0.7s linear infinite' }}/>
      Loading Governance Portal...
    </div>
  );

  const STAT_CARDS = [
    { label:'Total SHGs',     value:stats.totalShgs.toLocaleString(),     icon:Users,     color:'#8b5cf6', bg:'rgba(139,92,246,0.1)', border:'rgba(139,92,246,0.25)' },
    { label:'Avg Trust Score',value:stats.avgTrustScore.toFixed(1),       icon:Activity,  color:'#10b981', bg:'rgba(16,185,129,0.1)', border:'rgba(16,185,129,0.25)' },
    { label:'Total Volume',   value:stats.totalVolume,                    icon:BarChart,  color:'#f59e0b', bg:'rgba(245,158,11,0.1)', border:'rgba(245,158,11,0.25)' },
    { label:'Active Txns',    value:stats.activeTransactions,             icon:FileText,  color:'#a78bfa', bg:'rgba(139,92,246,0.08)',border:'rgba(139,92,246,0.2)' },
  ];

  const AGENT_ACTIVITY = [
    { name:'Agent Vaani',         tag:'Voice AI',    color:'#a78bfa', bg:'rgba(139,92,246,0.1)', border:'rgba(139,92,246,0.25)', stat:'1,234 queries processed today' },
    { name:'Agent Jodi',          tag:'Matching',    color:'#6ee7b7', bg:'rgba(16,185,129,0.1)', border:'rgba(16,185,129,0.25)', stat:'56 buyer matches created' },
    { name:'Agent Bazaar Buddhi', tag:'Market Intel',color:'#fcd34d', bg:'rgba(245,158,11,0.1)', border:'rgba(245,158,11,0.25)', stat:'234 market analyses completed' },
  ];

  const TOP_PERFORMERS = [
    { medal:'🥇', name:'Laxmi SHG',    location:'Hyderabad', score:95.2, color:'#fcd34d', bg:'rgba(245,158,11,0.07)', border:'rgba(245,158,11,0.2)' },
    { medal:'🥈', name:'Mahila Shakti',location:'Ranga Reddy',score:92.8, color:'#cbd5e1', bg:'rgba(255,255,255,0.04)', border:'rgba(255,255,255,0.1)' },
    { medal:'🥉', name:'Sri Lakshmi',  location:'Medak',     score:89.5, color:'#fb923c', bg:'rgba(251,146,60,0.07)', border:'rgba(251,146,60,0.2)' },
  ];

  return (
    <div className="animate-fade-in" style={{ padding:'1.5rem', maxWidth:1100, margin:'0 auto', paddingBottom:'6rem' }}>
      {/* Hero Header */}
      <div style={{ background:'linear-gradient(135deg,rgba(124,58,237,0.3) 0%,rgba(168,85,247,0.2) 100%)', border:'1px solid rgba(139,92,246,0.35)', borderRadius:'1.5rem', padding:'2rem 2.5rem', marginBottom:'1.75rem', display:'flex', justifyContent:'space-between', alignItems:'center', overflow:'hidden', position:'relative' }}>
        <div style={{ position:'absolute', top:-30, right:-30, width:180, height:180, borderRadius:'50%', background:'rgba(139,92,246,0.12)', filter:'blur(40px)' }}/>
        <div>
          <h1 style={{ fontSize:'1.75rem', fontWeight:900, color:'#f8fafc', margin:'0 0 6px' }}>District Project Director Portal</h1>
          <p style={{ color:'#c4b5fd', margin:0, fontWeight:500 }}>Real-time oversight of the Agentic Ecosystem</p>
        </div>
        <ShieldCheck size={56} style={{ color:'rgba(196,181,253,0.4)', flexShrink:0 }}/>
      </div>

      {/* Stat Cards */}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(180px,1fr))', gap:'0.9rem', marginBottom:'1.5rem' }}>
        {STAT_CARDS.map(({ label, value, icon:Icon, color, bg, border }) => (
          <div key={label} style={{ background:bg, border:`1px solid ${border}`, borderRadius:'1rem', padding:'1.25rem', display:'flex', justifyContent:'space-between', alignItems:'center' }}>
            <div>
              <p style={{ fontSize:'0.72rem', fontWeight:700, color:'var(--text-muted)', textTransform:'uppercase', letterSpacing:'0.07em', margin:'0 0 6px' }}>{label}</p>
              <p style={{ fontWeight:900, fontSize:'1.75rem', color, margin:0 }}>{value}</p>
            </div>
            <div style={{ width:44, height:44, borderRadius:10, background:`${color}15`, display:'flex', alignItems:'center', justifyContent:'center' }}>
              <Icon size={22} style={{ color }}/>
            </div>
          </div>
        ))}
      </div>

      {/* 2-col Section */}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(300px,1fr))', gap:'1rem', marginBottom:'1.5rem' }}>
        {/* Top Performers */}
        <div style={{ ...glass, padding:'1.25rem' }}>
          <h2 style={{ fontWeight:800, color:'var(--text-primary)', marginBottom:'1rem', fontSize:'1rem', display:'flex', alignItems:'center', gap:8 }}>
            <TrendingUp size={18} style={{ color:'#a78bfa' }}/> Top Performers
          </h2>
          <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
            {TOP_PERFORMERS.map(({ medal, name, location, score, color, bg, border }) => (
              <div key={name} style={{ display:'flex', justifyContent:'space-between', alignItems:'center', background:bg, border:`1px solid ${border}`, borderRadius:10, padding:'0.75rem' }}>
                <div style={{ display:'flex', alignItems:'center', gap:10 }}>
                  <span style={{ fontSize:'1.3rem' }}>{medal}</span>
                  <div>
                    <p style={{ fontWeight:700, color:'var(--text-primary)', margin:'0 0 2px', fontSize:'0.875rem' }}>{name}</p>
                    <p style={{ fontSize:'0.75rem', color:'var(--text-muted)', margin:0 }}>{location}</p>
                  </div>
                </div>
                <div style={{ textAlign:'right' }}>
                  <p style={{ fontWeight:900, color, fontSize:'1.2rem', margin:0 }}>{score}</p>
                  <p style={{ fontSize:'0.7rem', color:'var(--text-muted)', margin:0 }}>Trust Score</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Agent Activity */}
        <div style={{ ...glass, padding:'1.25rem' }}>
          <h2 style={{ fontWeight:800, color:'var(--text-primary)', marginBottom:'1rem', fontSize:'1rem', display:'flex', alignItems:'center', gap:8 }}>
            <ShieldCheck size={18} style={{ color:'#a78bfa' }}/> Agent Activity
          </h2>
          <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
            {AGENT_ACTIVITY.map(({ name, tag, color, bg, border, stat }) => (
              <div key={name} style={{ background:bg, border:`1px solid ${border}`, borderRadius:10, padding:'0.85rem' }}>
                <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:5 }}>
                  <span style={{ fontWeight:700, color, fontSize:'0.875rem' }}>{name}</span>
                  <span style={{ padding:'2px 8px', background:`${color}18`, border:`1px solid ${color}30`, borderRadius:99, fontSize:'0.68rem', fontWeight:700, color }}>{tag}</span>
                </div>
                <p style={{ fontSize:'0.8rem', color:'var(--text-secondary)', margin:0 }}>{stat}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Audit Logs Table */}
      <div style={{ ...glass, padding:'1.25rem' }}>
        <h2 style={{ fontWeight:800, color:'var(--text-primary)', marginBottom:'1rem', fontSize:'1rem', display:'flex', alignItems:'center', gap:8 }}>
          <ShieldCheck size={18} style={{ color:'#a78bfa' }}/> Agent Vishwas Audit Logs
        </h2>
        {logs.length===0 ? (
          <p style={{ textAlign:'center', color:'var(--text-muted)', padding:'2rem 0' }}>No audit logs available</p>
        ) : (
          <div style={{ overflowX:'auto' }}>
            <table style={{ width:'100%', borderCollapse:'collapse', fontSize:'0.85rem' }}>
              <thead>
                <tr style={{ borderBottom:'1px solid rgba(139,92,246,0.15)' }}>
                  {['Log ID','Agent','Action','Details','Time'].map(h=>(
                    <th key={h} style={{ padding:'0.6rem 0.75rem', textAlign:'left', color:'var(--text-muted)', fontWeight:700, fontSize:'0.72rem', textTransform:'uppercase', letterSpacing:'0.06em' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {logs.map((log,idx)=>(
                  <tr key={idx} style={{ borderBottom:'1px solid rgba(255,255,255,0.04)', transition:'background 0.15s' }}
                    onMouseEnter={e=>e.currentTarget.style.background='rgba(139,92,246,0.05)'}
                    onMouseLeave={e=>e.currentTarget.style.background='transparent'}>
                    <td style={{ padding:'0.7rem 0.75rem', fontFamily:'monospace', color:'var(--text-muted)', fontSize:'0.78rem' }}>{log.id}</td>
                    <td style={{ padding:'0.7rem 0.75rem' }}>
                      <span style={{ padding:'2px 8px', background:'rgba(139,92,246,0.12)', border:'1px solid rgba(139,92,246,0.25)', borderRadius:99, fontSize:'0.68rem', fontWeight:800, color:'#c4b5fd', textTransform:'uppercase' }}>{log.agent}</span>
                    </td>
                    <td style={{ padding:'0.7rem 0.75rem', fontWeight:600, color:'var(--text-secondary)' }}>{log.action}</td>
                    <td style={{ padding:'0.7rem 0.75rem', color:'var(--text-muted)', maxWidth:200, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{log.details}</td>
                    <td style={{ padding:'0.7rem 0.75rem', color:'var(--text-muted)', fontSize:'0.78rem', whiteSpace:'nowrap' }}>{log.time}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;
