import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { productsAPI, marketAPI } from '../services/api';
import { Loader2, ArrowLeft, Save, Sparkles } from 'lucide-react';

const glass = { background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: '1.25rem', backdropFilter: 'blur(16px)', WebkitBackdropFilter: 'blur(16px)' };
const inputStyle = { width: '100%', padding: '0.85rem 1rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(139,92,246,0.22)', borderRadius: 12, outline: 'none', color: 'var(--text-primary)', fontSize: '0.95rem', transition: 'all 0.2s' };
const labelStyle = { display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 };

const ProductEdit = () => {
  const { productId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [marketAnalysis, setMarketAnalysis] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: 'Handicrafts',
    quantity: '',
    unit: 'pcs',
    price: '',
    district: user?.district || 'Hyderabad'
  });

  useEffect(() => {
    fetchProduct();
  }, [productId]);

  const fetchProduct = async () => {
    try {
      setLoading(true);
      const response = await productsAPI.getById(productId);
      const product = response.data;
      if (product.seller_id !== user?.id) {
        alert('You can only edit your own products');
        navigate('/marketplace');
        return;
      }
      setFormData({
        name: product.name || '',
        description: product.description || '',
        category: product.category || 'Handicrafts',
        quantity: product.quantity?.toString() || product.stock?.toString() || '',
        unit: product.unit || 'pcs',
        price: product.price?.toString() || '',
        district: product.district || user?.district || 'Hyderabad'
      });
    } catch {
      navigate('/marketplace');
    } finally {
      setLoading(false);
    }
  };

  const handlePredictDemand = async () => {
    if (!formData.name) {
      alert('Please enter a product name first');
      return;
    }
    try {
      setAnalyzing(true);
      const r = await marketAPI.analyze(formData.name, formData.category, formData.district, formData.price ? parseFloat(formData.price) : null);
      setMarketAnalysis(r.data);
      if (r.data.recommended_price_min) {
        const avg = Math.round((r.data.recommended_price_min + (r.data.recommended_price_max || r.data.recommended_price_min)) / 2);
        setFormData(prev => ({ ...prev, price: avg.toString() }));
      }
    } catch {
      alert('AI analysis failed');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name?.trim() || !formData.quantity || !formData.price) {
      alert('Please fill in all required fields');
      return;
    }
    try {
      setSaving(true);
      const pd = new FormData();
      pd.append('name', formData.name.trim());
      pd.append('description', formData.description?.trim() || '');
      pd.append('category', formData.category);
      pd.append('quantity', parseInt(formData.quantity));
      pd.append('unit', formData.unit);
      pd.append('price', parseFloat(formData.price));
      pd.append('district', formData.district);
      await productsAPI.update(productId, pd);
      alert('Product updated!');
      navigate(`/products/${productId}`);
    } catch {
      alert('Update failed');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return (
    <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
      <div style={{ width: 36, height: 36, borderRadius: '50%', border: '3px solid rgba(139,92,246,0.2)', borderTopColor: '#8b5cf6', margin: '0 auto 12px', animation: 'spin 0.7s linear infinite' }} />
      Loading...
    </div>
  );

  return (
    <div className="animate-fade-in" style={{ padding: '1.5rem', maxWidth: 700, margin: '0 auto', paddingBottom: '6rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 15, marginBottom: '2rem' }}>
        <button onClick={() => navigate(`/products/${productId}`)} style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 10, color: 'var(--text-muted)', cursor: 'pointer', padding: '0.5rem' }}><ArrowLeft size={20} /></button>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 900, color: 'var(--text-primary)', margin: 0 }}>Edit Product</h1>
      </div>

      <div style={{ ...glass, padding: '2rem' }}>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div>
            <label style={labelStyle}>Product Name</label>
            <input type="text" required value={formData.name} onChange={e => setFormData(prev => ({ ...prev, name: e.target.value }))} style={inputStyle} placeholder="e.g. Handmade Silk Saree" onFocus={e => e.target.style.border = '1px solid #8b5cf6'} onBlur={e => e.target.style.border = '1px solid rgba(139,92,246,0.22)'} />
          </div>

          <div>
            <label style={labelStyle}>Description</label>
            <textarea rows="3" value={formData.description} onChange={e => setFormData(prev => ({ ...prev, description: e.target.value }))} style={{ ...inputStyle, resize: 'none' }} placeholder="Describe your product heritage..." />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <label style={labelStyle}>Category</label>
              <select value={formData.category} onChange={e => setFormData(prev => ({ ...prev, category: e.target.value }))} style={inputStyle}>
                {['Handicrafts', 'Textiles', 'Food Products', 'Organic Products', 'Personal Care', 'Home Decor', 'Agro Products'].map(c => <option key={c} value={c} style={{ background: '#110c22' }}>{c}</option>)}
              </select>
            </div>
            <div>
              <label style={labelStyle}>District</label>
              <input type="text" value={formData.district} onChange={e => setFormData(prev => ({ ...prev, district: e.target.value }))} style={inputStyle} />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
            <div>
              <label style={labelStyle}>Quantity</label>
              <input type="number" required value={formData.quantity} onChange={e => setFormData(prev => ({ ...prev, quantity: e.target.value }))} style={inputStyle} />
            </div>
            <div>
              <label style={labelStyle}>Unit</label>
              <select value={formData.unit} onChange={e => setFormData(prev => ({ ...prev, unit: e.target.value }))} style={inputStyle}>
                {['pcs', 'kg', 'g', 'l', 'meters'].map(u => <option key={u} value={u} style={{ background: '#110c22' }}>{u}</option>)}
              </select>
            </div>
            <div>
              <label style={labelStyle}>Price (₹)</label>
              <div style={{ position: 'relative' }}>
                <input type="number" required value={formData.price} onChange={e => setFormData(prev => ({ ...prev, price: e.target.value }))} style={inputStyle} />
                <button type="button" onClick={handlePredictDemand} disabled={analyzing} style={{ position: 'absolute', top: '50%', right: 8, transform: 'translateY(-50%)', background: 'rgba(16,185,129,0.15)', border: '1px solid rgba(16,185,129,0.3)', borderRadius: 6, color: '#6ee7b7', fontSize: '0.65rem', padding: '2px 6px', fontWeight: 800, cursor: 'pointer' }}>
                  {analyzing ? <Loader2 size={12} className="animate-spin" /> : 'AI Price'}
                </button>
              </div>
            </div>
          </div>

          {marketAnalysis && (
            <div style={{ background: 'rgba(59,130,246,0.1)', border: '1px solid rgba(59,130,246,0.25)', borderRadius: 12, padding: '1rem' }}>
              <p style={{ fontSize: '0.75rem', fontWeight: 800, color: '#93c5fd', margin: '0 0 6px', display: 'flex', alignItems: 'center', gap: 5 }}><Sparkles size={14} /> Bazaar Buddhi Insights</p>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: '0 0 4px' }}>Demand: <strong style={{ color: '#fff' }}>{marketAnalysis.demand_level}</strong> ({marketAnalysis.demand_score}/100)</p>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>{marketAnalysis.suggestions?.[0]}</p>
            </div>
          )}

          <button type="submit" disabled={saving} style={{ marginTop: '1rem', padding: '1rem', background: 'linear-gradient(135deg,#7c3aed,#a855f7)', border: 'none', borderRadius: 12, color: '#fff', fontWeight: 800, fontSize: '1.1rem', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, boxShadow: '0 4px 15px rgba(139,92,246,0.4)', transition: 'all 0.2s' }} onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-2px)'} onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}>
            {saving ? <Loader2 size={24} className="animate-spin" /> : <Save size={20} />}
            {saving ? 'Saving...' : 'Update Product'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ProductEdit;
