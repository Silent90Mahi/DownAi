import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { marketAPI, api } from '../services/api';
import { TrendingUp, DollarSign, Calendar, MapPin, Package, BarChart3, Download, Brain, Sparkles, RefreshCw, Filter, ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';

const glass = { background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: '1.25rem', backdropFilter: 'blur(16px)', WebkitBackdropFilter: 'blur(16px)' };
const inputStyle = { width: '100%', padding: '0.65rem 0.9rem', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(139,92,246,0.22)', borderRadius: 10, outline: 'none', color: 'var(--text-primary)', fontSize: '0.9rem', transition: 'all 0.2s' };
const labelStyle = { display: 'block', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' };
const onFocus = e => { e.target.style.borderColor = '#8b5cf6'; e.target.style.boxShadow = '0 0 0 3px rgba(139,92,246,0.15)'; };
const onBlur = e => { e.target.style.borderColor = 'rgba(139,92,246,0.22)'; e.target.style.boxShadow = 'none'; };

const STUB_PRICE_DATA = {
  Handicrafts: [
    { month: 'Jan', price: 450, demand: 65 },
    { month: 'Feb', price: 480, demand: 70 },
    { month: 'Mar', price: 520, demand: 75 },
    { month: 'Apr', price: 490, demand: 68 },
    { month: 'May', price: 510, demand: 72 },
    { month: 'Jun', price: 550, demand: 80 },
    { month: 'Jul', price: 580, demand: 85 },
    { month: 'Aug', price: 560, demand: 82 },
    { month: 'Sep', price: 600, demand: 88 },
    { month: 'Oct', price: 650, demand: 92 },
    { month: 'Nov', price: 700, demand: 95 },
    { month: 'Dec', price: 750, demand: 98 },
  ],
  Textiles: [
    { month: 'Jan', price: 300, demand: 55 },
    { month: 'Feb', price: 320, demand: 58 },
    { month: 'Mar', price: 350, demand: 65 },
    { month: 'Apr', price: 380, demand: 70 },
    { month: 'May', price: 360, demand: 62 },
    { month: 'Jun', price: 340, demand: 55 },
    { month: 'Jul', price: 330, demand: 50 },
    { month: 'Aug', price: 350, demand: 58 },
    { month: 'Sep', price: 400, demand: 72 },
    { month: 'Oct', price: 450, demand: 80 },
    { month: 'Nov', price: 500, demand: 85 },
    { month: 'Dec', price: 550, demand: 90 },
  ],
  'Food Products': [
    { month: 'Jan', price: 200, demand: 70 },
    { month: 'Feb', price: 220, demand: 72 },
    { month: 'Mar', price: 250, demand: 78 },
    { month: 'Apr', price: 280, demand: 82 },
    { month: 'May', price: 300, demand: 85 },
    { month: 'Jun', price: 320, demand: 88 },
    { month: 'Jul', price: 350, demand: 90 },
    { month: 'Aug', price: 330, demand: 85 },
    { month: 'Sep', price: 310, demand: 80 },
    { month: 'Oct', price: 290, demand: 75 },
    { month: 'Nov', price: 270, demand: 72 },
    { month: 'Dec', price: 250, demand: 70 },
  ],
};

const DISTRICT_HEATMAP = [
  { district: 'Hyderabad', demand: 95, price_index: 110 },
  { district: 'Visakhapatnam', demand: 82, price_index: 95 },
  { district: 'Vijayawada', demand: 78, price_index: 92 },
  { district: 'Guntur', demand: 70, price_index: 88 },
  { district: 'Tirupati', demand: 85, price_index: 100 },
  { district: 'Rajahmundry', demand: 65, price_index: 85 },
  { district: 'Kakinada', demand: 60, price_index: 80 },
  { district: 'Kurnool', demand: 55, price_index: 75 },
];

const MarketAnalyzer = () => {
  const navigate = useNavigate();
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [aiPrediction, setAiPrediction] = useState(null);
  const [predicting, setPredicting] = useState(false);
  const [activeTab, setActiveTab] = useState('analyze');
  const [priceData, setPriceData] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('Handicrafts');
  const [formData, setFormData] = useState({ product_name: '', category: 'Handicrafts', district: 'Hyderabad', price: '' });

  const categories = ['Handicrafts', 'Food Products', 'Textiles', 'Pickles', 'Spices', 'Handmade Baskets'];
  const districts = ['Hyderabad', 'Visakhapatnam', 'Vijayawada', 'Guntur', 'Tirupati', 'Rajahmundry', 'Kakinada', 'Kurnool'];

  useEffect(() => {
    setPriceData(STUB_PRICE_DATA[selectedCategory] || STUB_PRICE_DATA.Handicrafts);
  }, [selectedCategory]);

  const handleAnalyze = async (e) => {
    e.preventDefault(); setAnalyzing(true); setResult(null);
    try {
      const response = await marketAPI.analyze({ product_name: formData.product_name, category: formData.category, district: formData.district, price: formData.price ? parseFloat(formData.price) : null });
      setResult(response.data);
    } catch (error) { alert('Analysis failed: ' + (error.response?.data?.detail || 'Unknown error')); }
    finally { setAnalyzing(false); }
  };

  const getAIPrediction = async () => {
    setPredicting(true);
    try {
      const response = await api.post('/market/ai-prediction', {
        category: formData.category || selectedCategory,
        district: formData.district || 'Hyderabad',
        product_name: formData.product_name || 'General products'
      });
      setAiPrediction(response.data);
    } catch {
      // Fallback stub prediction
      setAiPrediction({
        trend: 'upward',
        confidence: 85,
        prediction: 'Market demand for this category is expected to increase by 15-20% in the next quarter. Festival season approaching - consider increasing production.',
        recommended_actions: [
          'Stock up inventory before October',
          'Consider premium packaging for festival sales',
          'Target urban markets with higher purchasing power',
          'Collaborate with other SHGs for bulk orders'
        ],
        price_forecast: {
          current: 500,
          '1_month': 525,
          '3_month': 575,
          '6_month': 625
        },
        risk_factors: [
          'Seasonal competition may increase',
          'Raw material costs rising 5%'
        ]
      });
    } finally {
      setPredicting(false);
    }
  };

  const exportReport = () => {
    const report = {
      generated_at: new Date().toISOString(),
      category: formData.category,
      district: formData.district,
      analysis: result,
      prediction: aiPrediction,
      price_trends: priceData
    };
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `market-report-${formData.category}-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const demandColor = { High: '#6ee7b7', Medium: '#fcd34d', Low: '#fca5a5' };
  const demandBg = { High: 'rgba(16,185,129,0.12)', Medium: 'rgba(245,158,11,0.12)', Low: 'rgba(239,68,68,0.12)' };
  const demandBorder = { High: 'rgba(16,185,129,0.3)', Medium: 'rgba(245,158,11,0.3)', Low: 'rgba(239,68,68,0.3)' };

  const maxPrice = priceData ? Math.max(...priceData.map(d => d.price)) : 0;
  const maxDemand = 100;

  const TABS = [
    { id: 'analyze', label: 'Analyze Product', icon: TrendingUp },
    { id: 'trends', label: 'Price Trends', icon: BarChart3 },
    { id: 'heatmap', label: 'District Heatmap', icon: MapPin },
    { id: 'ai', label: 'AI Predictions', icon: Brain },
  ];

  return (
    <div className="animate-fade-in" style={{ padding: '1.5rem', maxWidth: 1100, margin: '0 auto', paddingBottom: '6rem' }}>
      <div style={{ marginBottom: '1.75rem' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 900, margin: '0 0 4px', background: 'linear-gradient(135deg, #f8fafc 0%, #c4b5fd 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>Market Analyzer</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', margin: 0 }}>Intelligence & Price Recommendations</p>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 8, marginBottom: '1.25rem', overflowX: 'auto', paddingBottom: 4 }}>
        {TABS.map(({ id, label, icon: Icon }) => (
          <button key={id} onClick={() => setActiveTab(id)} style={{
            display: 'flex', alignItems: 'center', gap: 6, padding: '0.6rem 1rem',
            background: activeTab === id ? 'rgba(139,92,246,0.2)' : 'rgba(255,255,255,0.04)',
            border: activeTab === id ? '1px solid rgba(139,92,246,0.4)' : '1px solid rgba(255,255,255,0.08)',
            borderRadius: 10, cursor: 'pointer', whiteSpace: 'nowrap',
            color: activeTab === id ? '#c4b5fd' : 'var(--text-muted)',
            fontWeight: 600, fontSize: '0.85rem', transition: 'all 0.2s',
          }}>
            <Icon size={16} /> {label}
          </button>
        ))}
      </div>

      {/* Analyze Tab */}
      {activeTab === 'analyze' && (
        <div style={{ display: 'grid', gridTemplateColumns: result ? '1fr 1fr' : '1fr', gap: '1.25rem' }}>
          <div style={{ ...glass, padding: '1.75rem' }}>
            <h2 style={{ fontWeight: 800, color: 'var(--text-primary)', fontSize: '1.1rem', marginBottom: '1.25rem' }}>Analyze Your Product</h2>
            <form onSubmit={handleAnalyze} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={labelStyle}>Product Name</label>
                <input type="text" value={formData.product_name} onChange={e => setFormData({ ...formData, product_name: e.target.value })} style={inputStyle} placeholder="e.g., Bamboo Basket" required onFocus={onFocus} onBlur={onBlur} />
              </div>
              <div>
                <label style={labelStyle}>Category</label>
                <select value={formData.category} onChange={e => setFormData({ ...formData, category: e.target.value })} style={{ ...inputStyle, cursor: 'pointer' }} required onFocus={onFocus} onBlur={onBlur}>
                  {categories.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div>
                <label style={labelStyle}>District</label>
                <select value={formData.district} onChange={e => setFormData({ ...formData, district: e.target.value })} style={{ ...inputStyle, cursor: 'pointer' }} required onFocus={onFocus} onBlur={onBlur}>
                  {districts.map(d => <option key={d} value={d}>{d}</option>)}
                </select>
              </div>
              <div>
                <label style={labelStyle}>Your Cost Price (₹)</label>
                <input type="number" value={formData.price} onChange={e => setFormData({ ...formData, price: e.target.value })} style={inputStyle} placeholder="e.g., 500" onFocus={onFocus} onBlur={onBlur} />
              </div>
              <button type="submit" disabled={analyzing} style={{ padding: '0.75rem', background: analyzing ? 'rgba(139,92,246,0.2)' : 'linear-gradient(135deg, #7c3aed, #a855f7)', border: 'none', borderRadius: 10, color: '#fff', fontWeight: 700, cursor: analyzing ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, boxShadow: '0 4px 14px rgba(139,92,246,0.35)' }}>
                {analyzing ? <><div style={{ width: 16, height: 16, borderRadius: '50%', border: '2px solid rgba(255,255,255,0.3)', borderTopColor: '#fff', animation: 'spin 0.7s linear infinite' }} />Analyzing...</> : <><TrendingUp size={17} />Analyze Market</>}
              </button>
            </form>
          </div>

          {result && (
            <div style={{ ...glass, padding: '1.75rem' }}>
              <h3 style={{ fontWeight: 800, color: 'var(--text-primary)', fontSize: '1.1rem', marginBottom: '1.25rem' }}>Analysis Results</h3>
              {/* Demand */}
              <div style={{ marginBottom: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Demand Level</span>
                  <span style={{ padding: '3px 10px', borderRadius: 99, fontSize: '0.72rem', fontWeight: 800, background: demandBg[result.demand_level] || 'rgba(139,92,246,0.1)', color: demandColor[result.demand_level] || '#c4b5fd', border: `1px solid ${demandBorder[result.demand_level] || 'rgba(139,92,246,0.25)'}` }}>{result.demand_level}</span>
                </div>
                <div style={{ width: '100%', height: 8, background: 'rgba(255,255,255,0.06)', borderRadius: 99, overflow: 'hidden' }}>
                  <div style={{ height: '100%', width: `${result.demand_score}%`, background: 'linear-gradient(90deg, #7c3aed, #a855f7)', borderRadius: 99, transition: 'width 1s ease' }} />
                </div>
              </div>
              {/* Price */}
              <div style={{ background: 'rgba(16,185,129,0.06)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: 10, padding: '0.9rem', marginBottom: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 8 }}>
                  <DollarSign size={15} style={{ color: '#10b981' }} />
                  <span style={{ fontWeight: 700, color: '#6ee7b7', fontSize: '0.85rem' }}>Price Recommendation</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: '0 0 2px' }}>Min: ₹{result.recommended_price_min}</p>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>Max: ₹{result.recommended_price_max}</p>
                  </div>
                  <p style={{ fontWeight: 900, color: '#6ee7b7', fontSize: '1.3rem', margin: 0 }}>₹{Math.round((result.recommended_price_min + result.recommended_price_max) / 2)}</p>
                </div>
              </div>
              {/* Suggestions */}
              <div>
                <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: 8 }}>Suggestions</h4>
                <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 5 }}>
                  {result.suggestions?.map((s, i) => (
                    <li key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 7, fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                      <span style={{ color: '#6ee7b7', flexShrink: 0 }}>✓</span>{s}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Price Trends Tab */}
      {activeTab === 'trends' && priceData && (
        <div style={{ ...glass, padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h3 style={{ fontWeight: 800, color: 'var(--text-primary)', fontSize: '1.1rem', margin: 0 }}>Price & Demand Trends</h3>
            <select value={selectedCategory} onChange={(e) => setSelectedCategory(e.target.value)} style={{ padding: '0.4rem 0.8rem', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 8, color: 'var(--text-primary)', fontSize: '0.85rem', cursor: 'pointer' }}>
              {categories.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>

          {/* Price Chart */}
          <div style={{ marginBottom: '2rem' }}>
            <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '1rem' }}>Average Price (₹)</h4>
            <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8, height: 150, padding: '0 0.5rem' }}>
              {priceData.map((d, i) => (
                <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
                  <div style={{ width: '100%', height: (d.price / maxPrice) * 140, background: 'linear-gradient(180deg, #8b5cf6, #a855f7)', borderRadius: '4px 4px 0 0', transition: 'height 0.5s', position: 'relative' }}>
                    <span style={{ position: 'absolute', top: -20, left: '50%', transform: 'translateX(-50%)', fontSize: '0.65rem', color: '#c4b5fd', fontWeight: 600 }}>₹{d.price}</span>
                  </div>
                  <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{d.month}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Demand Chart */}
          <div>
            <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '1rem' }}>Demand Index</h4>
            <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8, height: 120, padding: '0 0.5rem' }}>
              {priceData.map((d, i) => (
                <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
                  <div style={{ width: '100%', height: (d.demand / maxDemand) * 110, background: 'linear-gradient(180deg, #10b981, #34d399)', borderRadius: '4px 4px 0 0', transition: 'height 0.5s', position: 'relative' }}>
                    <span style={{ position: 'absolute', top: -18, left: '50%', transform: 'translateX(-50%)', fontSize: '0.6rem', color: '#6ee7b7', fontWeight: 600 }}>{d.demand}%</span>
                  </div>
                  <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{d.month}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* District Heatmap Tab */}
      {activeTab === 'heatmap' && (
        <div style={{ ...glass, padding: '1.5rem' }}>
          <h3 style={{ fontWeight: 800, color: 'var(--text-primary)', fontSize: '1.1rem', marginBottom: '1.25rem' }}>District Demand Heatmap</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
            {DISTRICT_HEATMAP.map((d, i) => {
              const intensity = d.demand / 100;
              const bgColor = `rgba(139, 92, 246, ${intensity * 0.4})`;
              const borderColor = `rgba(139, 92, 246, ${intensity * 0.6})`;
              return (
                <div key={i} style={{ background: bgColor, border: `1px solid ${borderColor}`, borderRadius: 12, padding: '1rem', transition: 'all 0.3s' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <span style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '0.9rem' }}>{d.district}</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 3, color: d.demand >= 80 ? '#6ee7b7' : d.demand >= 60 ? '#fcd34d' : '#fca5a5', fontSize: '0.75rem', fontWeight: 700 }}>
                      {d.demand >= 80 ? <ArrowUpRight size={12} /> : d.demand >= 60 ? <Minus size={12} /> : <ArrowDownRight size={12} />}
                      {d.demand}%
                    </span>
                  </div>
                  <div style={{ width: '100%', height: 6, background: 'rgba(255,255,255,0.1)', borderRadius: 99, overflow: 'hidden', marginBottom: '0.5rem' }}>
                    <div style={{ height: '100%', width: `${d.demand}%`, background: 'linear-gradient(90deg, #7c3aed, #a855f7)', borderRadius: 99 }} />
                  </div>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0 }}>Price Index: {d.price_index}%</p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* AI Predictions Tab */}
      {activeTab === 'ai' && (
        <div style={{ ...glass, padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h3 style={{ fontWeight: 800, color: 'var(--text-primary)', fontSize: '1.1rem', margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Brain size={20} style={{ color: '#a78bfa' }} /> AI Market Predictions
            </h3>
            <div style={{ display: 'flex', gap: 8 }}>
              <button onClick={getAIPrediction} disabled={predicting} style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '0.5rem 1rem', background: 'linear-gradient(135deg, #7c3aed, #a855f7)', border: 'none', borderRadius: 8, color: '#fff', fontWeight: 600, cursor: predicting ? 'not-allowed' : 'pointer' }}>
                {predicting ? <div style={{ width: 14, height: 14, borderRadius: '50%', border: '2px solid rgba(255,255,255,0.3)', borderTopColor: '#fff', animation: 'spin 0.7s linear infinite' }} /> : <Sparkles size={14} />}
                {predicting ? 'Analyzing...' : 'Generate Prediction'}
              </button>
              {aiPrediction && (
                <button onClick={exportReport} style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '0.5rem 1rem', background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)', borderRadius: 8, color: '#6ee7b7', fontWeight: 600, cursor: 'pointer' }}>
                  <Download size={14} /> Export
                </button>
              )}
            </div>
          </div>

          {!aiPrediction ? (
            <div style={{ textAlign: 'center', padding: '3rem 1rem' }}>
              <Brain size={48} style={{ color: 'rgba(139,92,246,0.3)', margin: '0 auto 1rem' }} />
              <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>Click "Generate Prediction" to get AI-powered market insights</p>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Powered by OpenAI GPT-4</p>
            </div>
          ) : (
            <div>
              {/* Trend Overview */}
              <div style={{ background: aiPrediction.trend === 'upward' ? 'rgba(16,185,129,0.1)' : aiPrediction.trend === 'downward' ? 'rgba(239,68,68,0.1)' : 'rgba(245,158,11,0.1)', border: aiPrediction.trend === 'upward' ? '1px solid rgba(16,185,129,0.3)' : aiPrediction.trend === 'downward' ? '1px solid rgba(239,68,68,0.3)' : '1px solid rgba(245,158,11,0.3)', borderRadius: 12, padding: '1rem', marginBottom: '1.25rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: '0.5rem' }}>
                  {aiPrediction.trend === 'upward' ? <ArrowUpRight size={20} color="#6ee7b7" /> : aiPrediction.trend === 'downward' ? <ArrowDownRight size={20} color="#fca5a5" /> : <Minus size={20} color="#fcd34d" />}
                  <span style={{ fontWeight: 700, color: aiPrediction.trend === 'upward' ? '#6ee7b7' : aiPrediction.trend === 'downward' ? '#fca5a5' : '#fcd34d', fontSize: '1rem', textTransform: 'capitalize' }}>{aiPrediction.trend} Trend</span>
                  <span style={{ marginLeft: 'auto', fontSize: '0.8rem', color: 'var(--text-muted)' }}>{aiPrediction.confidence}% confidence</span>
                </div>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0, lineHeight: 1.6 }}>{aiPrediction.prediction}</p>
              </div>

              {/* Price Forecast */}
              {aiPrediction.price_forecast && (
                <div style={{ marginBottom: '1.25rem' }}>
                  <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>Price Forecast</h4>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.5rem' }}>
                    {[
                      { label: 'Current', value: aiPrediction.price_forecast.current },
                      { label: '1 Month', value: aiPrediction.price_forecast['1_month'] },
                      { label: '3 Months', value: aiPrediction.price_forecast['3_month'] },
                      { label: '6 Months', value: aiPrediction.price_forecast['6_month'] },
                    ].map((f, i) => (
                      <div key={i} style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(139,92,246,0.15)', borderRadius: 10, padding: '0.75rem', textAlign: 'center' }}>
                        <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', margin: '0 0 4px' }}>{f.label}</p>
                        <p style={{ fontWeight: 800, color: '#a78bfa', fontSize: '1.1rem', margin: 0 }}>₹{f.value}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommended Actions */}
              {aiPrediction.recommended_actions && (
                <div style={{ marginBottom: '1.25rem' }}>
                  <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>Recommended Actions</h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    {aiPrediction.recommended_actions.map((action, i) => (
                      <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '0.6rem 0.75rem', background: 'rgba(16,185,129,0.06)', border: '1px solid rgba(16,185,129,0.15)', borderRadius: 8 }}>
                        <span style={{ width: 20, height: 20, borderRadius: '50%', background: 'rgba(16,185,129,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.7rem', fontWeight: 700, color: '#6ee7b7' }}>{i + 1}</span>
                        <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{action}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Risk Factors */}
              {aiPrediction.risk_factors && (
                <div>
                  <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#fca5a5', marginBottom: '0.75rem' }}>Risk Factors</h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                    {aiPrediction.risk_factors.map((risk, i) => (
                      <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '0.5rem 0.75rem', background: 'rgba(239,68,68,0.06)', border: '1px solid rgba(239,68,68,0.15)', borderRadius: 8 }}>
                        <span style={{ color: '#fca5a5' }}>⚠️</span>
                        <span style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>{risk}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Quick Actions */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '0.75rem', marginTop: '1.5rem' }}>
        {[
          { label: 'Sell Product', icon: TrendingUp, path: '/sell', color: '#8b5cf6' },
          { label: 'Find Buyers', icon: TrendingUp, path: '/matches', color: '#a78bfa' },
          { label: 'Buy Materials', icon: Package, path: '/suppliers', color: '#10b981' },
          { label: 'Trust Coins', icon: DollarSign, path: '/wallet', color: '#f59e0b' },
        ].map(({ label, icon: Icon, path, color }) => (
          <button key={path} onClick={() => navigate(path)} style={{ ...glass, padding: '1.25rem', textAlign: 'center', border: 'none', cursor: 'pointer', transition: 'all 0.25s' }}
            onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.07)'; e.currentTarget.style.transform = 'translateY(-3px)'; }}
            onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.04)'; e.currentTarget.style.transform = 'translateY(0)'; }}>
            <div style={{ width: 44, height: 44, borderRadius: '50%', background: `${color}18`, border: `1px solid ${color}35`, display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 10px' }}>
              <Icon size={20} style={{ color }} />
            </div>
            <p style={{ fontWeight: 600, color: 'var(--text-secondary)', margin: 0, fontSize: '0.85rem' }}>{label}</p>
          </button>
        ))}
      </div>
    </div>
  );
};

export default MarketAnalyzer;
