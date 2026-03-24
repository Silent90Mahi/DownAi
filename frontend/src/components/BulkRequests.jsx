import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { suppliersAPI } from '../services/api';
import { Users, Clock, CheckCircle, Plus, MapPin } from 'lucide-react';

const glass = { background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: '1.1rem', backdropFilter: 'blur(16px)', WebkitBackdropFilter: 'blur(16px)' };

const BulkRequests = () => {
  const navigate = useNavigate();
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => { fetchRequests(); }, []);

  const fetchRequests = async () => {
    try { setLoading(true); const r = await suppliersAPI.getBulkRequests(); setRequests(r.data); }
    catch { console.error('Failed to fetch bulk requests'); }
    finally { setLoading(false); }
  };

  const joinRequest = async (id) => {
    const qty = prompt('Enter quantity you want to contribute:');
    if (!qty) return;
    try { await suppliersAPI.joinBulkRequest(id, parseInt(qty)); alert('Successfully joined!'); fetchRequests(); }
    catch (e) { alert('Failed: ' + (e.response?.data?.detail || 'Unknown error')); }
  };

  return (
    <div className="animate-fade-in" style={{ padding:'1.5rem', maxWidth:900, margin:'0 auto', paddingBottom:'6rem' }}>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:'1.75rem', flexWrap:'wrap', gap:'1rem' }}>
        <div>
          <h1 style={{ fontSize:'1.75rem', fontWeight:900, margin:'0 0 4px', background:'linear-gradient(135deg,#f8fafc 0%,#c4b5fd 100%)', WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent', backgroundClip:'text' }}>Bulk Purchase Requests</h1>
          <p style={{ color:'var(--text-muted)', fontSize:'0.875rem', margin:0 }}>Save money by buying raw materials together</p>
        </div>
        <button onClick={()=>{/* Open create modal */}} style={{ display:'flex', alignItems:'center', gap:6, padding:'0.55rem 1.1rem', background:'linear-gradient(135deg,#7c3aed,#a855f7)', border:'none', borderRadius:10, cursor:'pointer', color:'#fff', fontSize:'0.875rem', fontWeight:700, boxShadow:'0 4px 12px rgba(139,92,246,0.35)' }}>
          <Plus size={16}/> Create Request
        </button>
      </div>

      {/* Savings Banner */}
      <div style={{ background:'linear-gradient(135deg,rgba(16,185,129,0.15) 0%,rgba(139,92,246,0.12) 100%)', border:'1px solid rgba(16,185,129,0.25)', borderRadius:'1.1rem', padding:'1.25rem 1.5rem', marginBottom:'1.5rem', display:'flex', justifyContent:'space-between', alignItems:'center' }}>
        <div>
          <h2 style={{ fontWeight:800, color:'#6ee7b7', fontSize:'1.05rem', margin:'0 0 4px' }}>💰 Group Buying = Group Saving</h2>
          <p style={{ color:'var(--text-secondary)', margin:0, fontSize:'0.875rem' }}>SHGs save 15–25% by purchasing raw materials in bulk</p>
        </div>
        <div style={{ textAlign:'right' }}>
          <p style={{ fontWeight:900, fontSize:'2rem', color:'#6ee7b7', margin:0 }}>{requests.length}</p>
          <p style={{ fontSize:'0.75rem', color:'var(--text-muted)', margin:0 }}>Active Requests</p>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign:'center', padding:'3rem', color:'var(--text-muted)' }}>
          <div style={{ width:36, height:36, borderRadius:'50%', border:'3px solid rgba(139,92,246,0.2)', borderTopColor:'#8b5cf6', margin:'0 auto 12px', animation:'spin 0.7s linear infinite' }}/>
          Loading...
        </div>
      ) : requests.length===0 ? (
        <div style={{ textAlign:'center', padding:'3rem', ...glass }}>
          <Users size={48} style={{ color:'rgba(139,92,246,0.25)', margin:'0 auto 12px' }}/>
          <p style={{ fontWeight:600, color:'var(--text-muted)', margin:'0 0 6px' }}>No bulk requests yet</p>
          <p style={{ fontSize:'0.85rem', color:'var(--text-muted)', margin:0 }}>Start a request and invite other SHGs to join</p>
        </div>
      ) : (
        <div style={{ display:'flex', flexDirection:'column', gap:'0.9rem', marginBottom:'1.5rem' }}>
          {requests.map(req=>{
            const pct = Math.min((req.current_quantity/req.target_quantity)*100,100);
            return (
              <div key={req.id} style={{ ...glass, padding:'1.25rem' }}>
                <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:'0.9rem', flexWrap:'wrap', gap:8 }}>
                  <div style={{ flex:1 }}>
                    <h3 style={{ fontWeight:800, color:'var(--text-primary)', margin:'0 0 4px', fontSize:'1rem' }}>{req.title}</h3>
                    <p style={{ fontSize:'0.82rem', color:'var(--text-secondary)', margin:'0 0 6px' }}>{req.description}</p>
                    <p style={{ display:'flex', alignItems:'center', gap:8, fontSize:'0.75rem', color:'var(--text-muted)', margin:0 }}>
                      <MapPin size={11}/>{req.district} {req.expires_at && <><Clock size={11}/> Expires: {new Date(req.expires_at).toLocaleDateString()}</>}
                    </p>
                  </div>
                  <div style={{ textAlign:'right' }}>
                    <p style={{ fontSize:'0.8rem', fontWeight:700, color:'#6ee7b7', margin:'0 0 5px' }}>Save {req.expected_savings}%</p>
                    <span style={{ padding:'3px 10px', borderRadius:99, fontSize:'0.72rem', fontWeight:700, background:req.status==='Open'?'rgba(16,185,129,0.12)':req.status==='Completed'?'rgba(59,130,246,0.12)':'rgba(255,255,255,0.06)', color:req.status==='Open'?'#6ee7b7':req.status==='Completed'?'#93c5fd':'var(--text-muted)', border:`1px solid ${req.status==='Open'?'rgba(16,185,129,0.3)':req.status==='Completed'?'rgba(59,130,246,0.3)':'rgba(255,255,255,0.08)'}` }}>
                      {req.status}
                    </span>
                  </div>
                </div>
                {/* Progress Bar */}
                <div style={{ marginBottom:'0.9rem' }}>
                  <div style={{ display:'flex', justifyContent:'space-between', fontSize:'0.78rem', color:'var(--text-muted)', marginBottom:6 }}>
                    <span>Progress</span><span>{req.current_quantity}/{req.target_quantity}</span>
                  </div>
                  <div style={{ height:8, background:'rgba(255,255,255,0.06)', borderRadius:99, overflow:'hidden' }}>
                    <div style={{ height:'100%', width:`${pct}%`, background:'linear-gradient(90deg,#7c3aed,#10b981)', borderRadius:99, transition:'width 0.6s ease' }}/>
                  </div>
                  <p style={{ fontSize:'0.72rem', color:'var(--text-muted)', textAlign:'right', margin:'4px 0 0' }}>{req.completion_percentage}% complete</p>
                </div>
                <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between' }}>
                  <span style={{ display:'flex', alignItems:'center', gap:7, fontSize:'0.82rem', color:'var(--text-muted)' }}>
                    <Users size={15}/>{req.current_participants} participants
                  </span>
                  {req.status==='Open' && req.completion_percentage<100 && (
                    <button onClick={()=>joinRequest(req.id)} style={{ padding:'6px 18px', background:'rgba(139,92,246,0.15)', border:'1px solid rgba(139,92,246,0.35)', borderRadius:8, color:'#c4b5fd', fontWeight:700, fontSize:'0.82rem', cursor:'pointer' }}>
                      Join Request
                    </button>
                  )}
                  {req.status==='Completed' && (
                    <span style={{ display:'flex', alignItems:'center', gap:6, color:'#6ee7b7', fontWeight:700, fontSize:'0.82rem' }}>
                      <CheckCircle size={16}/> Order Placed!
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* How It Works */}
      <div style={{ background:'rgba(59,130,246,0.07)', border:'1px solid rgba(59,130,246,0.2)', borderRadius:'1.1rem', padding:'1.25rem' }}>
        <h3 style={{ fontWeight:700, color:'#93c5fd', marginBottom:'0.75rem', fontSize:'0.95rem' }}>How Bulk Purchasing Works</h3>
        <ol style={{ padding:0, margin:0, listStyle:'none', display:'flex', flexDirection:'column', gap:8 }}>
          {['Create a bulk request for the materials you need','Other SHGs join your request','Once target quantity is reached, place a single bulk order','Everyone gets their materials at the discounted bulk price'].map((step,i)=>(
            <li key={i} style={{ display:'flex', alignItems:'flex-start', gap:10, fontSize:'0.82rem', color:'var(--text-secondary)' }}>
              <span style={{ width:22, height:22, borderRadius:'50%', background:'rgba(59,130,246,0.2)', border:'1px solid rgba(59,130,246,0.3)', display:'flex', alignItems:'center', justifyContent:'center', fontSize:'0.7rem', fontWeight:800, color:'#93c5fd', flexShrink:0 }}>{i+1}</span>
              {step}
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
};

export default BulkRequests;
