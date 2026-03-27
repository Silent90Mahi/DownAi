import { useState } from 'react';
import { ArrowRight, Tag, Loader2, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { productsAPI, marketAPI } from '../services/api';

const fieldStyle = {
  width: '100%', padding: '0.7rem 1rem',
  background: 'rgba(255,255,255,0.06)',
  border: '1px solid rgba(139,92,246,0.22)',
  borderRadius: 10, outline: 'none',
  color: 'var(--text-primary)', fontSize: '0.9rem',
  transition: 'all 0.2s',
};
const labelStyle = {
  display: 'block', fontSize: '0.75rem', fontWeight: 700,
  color: 'var(--text-muted)', textTransform: 'uppercase',
  letterSpacing: '0.07em', marginBottom: '0.4rem',
};
const onFocus = e => { e.target.style.borderColor = '#8b5cf6'; e.target.style.boxShadow = '0 0 0 3px rgba(139,92,246,0.15)'; };
const onBlur  = e => { e.target.style.borderColor = 'rgba(139,92,246,0.22)'; e.target.style.boxShadow = 'none'; };

const SellProduct = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    name: '', description: '', category: 'Handicrafts',
    quantity: '', unit: 'pcs', price: '', district: user?.district || 'Hyderabad',
  });
  const [analyzing, setAnalyzing] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [marketAnalysis, setMarketAnalysis] = useState(null);

  const f = (k) => (e) => setFormData(p => ({ ...p, [k]: e.target.value }));

  const handlePredictDemand = async () => {
    if (!formData.name) { alert('Please enter a product name first'); return; }
    try {
      setAnalyzing(true);
      const response = await marketAPI.analyze(formData.name, formData.category, formData.district, formData.price ? parseFloat(formData.price) : null);
      setMarketAnalysis(response.data);
      if (response.data.recommended_price_min) {
        const avg = Math.round((response.data.recommended_price_min + (response.data.recommended_price_max || response.data.recommended_price_min)) / 2);
        setFormData(p => ({ ...p, price: avg.toString() }));
      }
    } catch { console.error('Market analysis failed'); }
    finally { setAnalyzing(false); }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name?.trim())              { alert('Please enter a product name'); return; }
    if (!formData.category)                  { alert('Please select a category'); return; }
    if (!formData.quantity || parseInt(formData.quantity) <= 0) { alert('Please enter a valid quantity'); return; }
    if (!formData.price || parseFloat(formData.price) <= 0)     { alert('Please enter a valid price'); return; }
    try {
      setSubmitting(true);
      const productData = new FormData();
      productData.append('name', formData.name.trim());
      productData.append('description', formData.description?.trim() || '');
      productData.append('category', formData.category);
      productData.append('quantity', parseInt(formData.quantity));
      productData.append('unit', formData.unit);
      productData.append('price', parseFloat(formData.price));
      productData.append('district', formData.district);
      await productsAPI.create(productData);
      setSubmitted(true);
      setTimeout(() => navigate('/marketplace'), 2000);
    } catch (error) {
      const msg = error.response?.data?.detail || 'Unknown error';
      alert('Failed: ' + (Array.isArray(msg) ? msg.map(e => `${e.msg}: ${e.loc?.join('.') || 'field'}`).join('\n') : msg));
    } finally { setSubmitting(false); }
  };

  if (submitted) return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '4rem 2rem', background: 'rgba(16,185,129,0.06)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: '1.5rem', textAlign: 'center', maxWidth: 480, margin: '3rem auto' }}>
      <div style={{ width: 64, height: 64, borderRadius: '50%', background: 'rgba(16,185,129,0.15)', border: '2px solid rgba(16,185,129,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem', boxShadow: '0 0 20px rgba(16,185,129,0.2)' }}>
        <svg width="30" height="30" fill="none" stroke="#6ee7b7" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" /></svg>
      </div>
      <h2 style={{ fontSize: '1.5rem', fontWeight: 900, color: '#6ee7b7', marginBottom: '0.5rem' }}>Product Listed!</h2>
      <p style={{ color: 'var(--text-muted)', margin: 0 }}>Agent Jodi is matching your product with buyers...</p>
    </div>
  );

  return (
    <div className="animate-fade-in" style={{ maxWidth: 680, margin: '0 auto', padding: '1.5rem', paddingBottom: '6rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.75rem' }}>
        <button onClick={() => navigate('/')} style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '0.5rem 1rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(139,92,246,0.25)', borderRadius: 10, cursor: 'pointer', color: 'var(--text-secondary)', fontWeight: 600, fontSize: '0.85rem' }}>
          <ArrowLeft size={15} /> Back
        </button>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 900, margin: 0, background: 'linear-gradient(135deg, #f8fafc 0%, #c4b5fd 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>List a Product</h1>
      </div>

      <div style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: '1.25rem', padding: '2rem', backdropFilter: 'blur(16px)' }}>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.1rem' }}>
          <div>
            <label style={labelStyle}>Product Name</label>
            <input type="text" required value={formData.name} onChange={f('name')} style={fieldStyle} placeholder="Product Name" onFocus={onFocus} onBlur={onBlur} />
          </div>

          <div>
            <label style={labelStyle}>Description</label>
            <textarea rows="3" required value={formData.description} onChange={f('description')} style={{ ...fieldStyle, resize: 'none' }} placeholder="Describe your product" onFocus={onFocus} onBlur={onBlur} />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <div>
              <label style={labelStyle}>Category</label>
              <select value={formData.category} onChange={f('category')} style={{ ...fieldStyle, cursor: 'pointer' }} onFocus={onFocus} onBlur={onBlur}>
                {['Handicrafts','Textiles','Food Products','Organic Products','Personal Care','Home Decor','Agro Products'].map(c => <option key={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label style={labelStyle}>District</label>
              <input type="text" value={formData.district} onChange={f('district')} style={fieldStyle} placeholder="Your district" onFocus={onFocus} onBlur={onBlur} />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.75rem' }}>
            <div>
              <label style={labelStyle}>Quantity</label>
              <input type="number" required value={formData.quantity} onChange={f('quantity')} style={fieldStyle} placeholder="100" onFocus={onFocus} onBlur={onBlur} />
            </div>
            <div>
              <label style={labelStyle}>Unit</label>
              <select value={formData.unit} onChange={f('unit')} style={{ ...fieldStyle, cursor: 'pointer' }} onFocus={onFocus} onBlur={onBlur}>
                <option value="pcs">Pcs</option>
                <option value="kg">Kg</option>
                <option value="g">Grams</option>
                <option value="l">Liters</option>
                <option value="ml">ml</option>
                <option value="meters">Meters</option>
              </select>
            </div>
            <div>
              <label style={{ ...labelStyle, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>Price (₹)</span>
                {analyzing ? (
                  <Loader2 size={12} style={{ animation: 'spin 0.7s linear infinite', color: '#a78bfa' }} />
                ) : (
                  <button type="button" onClick={handlePredictDemand} style={{ fontSize: '0.68rem', fontWeight: 700, color: '#c4b5fd', background: 'rgba(139,92,246,0.15)', border: 'none', borderRadius: 99, padding: '2px 8px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 3 }}>
                    <Tag size={9} /> AI Price
                  </button>
                )}
              </label>
              <input type="number" required value={formData.price} onChange={f('price')} style={fieldStyle} placeholder="3500" onFocus={onFocus} onBlur={onBlur} />
            </div>
          </div>

          {marketAnalysis && (
            <div style={{ background: 'rgba(139,92,246,0.08)', border: '1px solid rgba(139,92,246,0.25)', borderRadius: 10, padding: '0.9rem 1rem' }}>
              <p style={{ fontSize: '0.8rem', fontWeight: 700, color: '#a78bfa', margin: '0 0 6px' }}>🤖 Agent Bazaar Buddhi Analysis:</p>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', margin: '0 0 3px' }}>Demand Level: <strong style={{ color: '#c4b5fd' }}>{marketAnalysis.demand_level}</strong> (Score: {marketAnalysis.demand_score}/100)</p>
              {marketAnalysis.recommended_price_min && (<p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', margin: '0 0 3px' }}>Recommended: ₹{marketAnalysis.recommended_price_min} — ₹{marketAnalysis.recommended_price_max}</p>)}
              {marketAnalysis.suggestions && (<p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0 }}>{marketAnalysis.suggestions[0]}</p>)}
            </div>
          )}

          <button
            type="submit" disabled={submitting}
            style={{ width: '100%', padding: '0.9rem', marginTop: '0.5rem', background: 'linear-gradient(135deg, #7c3aed, #a855f7)', border: 'none', borderRadius: 12, color: '#fff', fontWeight: 800, fontSize: '1rem', cursor: submitting ? 'not-allowed' : 'pointer', opacity: submitting ? 0.7 : 1, boxShadow: '0 4px 20px rgba(139,92,246,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, transition: 'all 0.25s' }}
            onMouseEnter={e => !submitting && (e.currentTarget.style.boxShadow = '0 6px 28px rgba(139,92,246,0.6)')}
            onMouseLeave={e => (e.currentTarget.style.boxShadow = '0 4px 20px rgba(139,92,246,0.4)')}
          >
            {submitting ? 'Listing Product...' : <><span>List to Market</span><ArrowRight size={18} /></>}
          </button>
        </form>
      </div>
    </div>
  );
};

export default SellProduct;
