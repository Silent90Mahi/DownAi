import { useState, useEffect } from 'react';
import { Users, Package, ArrowLeft, ShoppingBag, RefreshCw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { productsAPI } from '../services/api';

const CARD_STYLE = {
  background: 'rgba(255,255,255,0.04)',
  border: '1px solid rgba(139,92,246,0.18)',
  borderRadius: '1.25rem',
  padding: '1.5rem',
  backdropFilter: 'blur(16px)',
  WebkitBackdropFilter: 'blur(16px)',
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'space-between',
  transition: 'all 0.3s',
  boxShadow: '0 4px 16px rgba(0,0,0,0.35)',
};

const Marketplace = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const navigate = useNavigate();

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const response = await productsAPI.getAll({ status: 'Active' }).catch(() => ({ data: { items: [] } }));
      const productsData = response.data?.items || response.data || [];
      setProducts(Array.isArray(productsData) ? productsData : []);
    } catch (error) {
      console.error('Failed to fetch marketplace data:', error);
      setProducts([]);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchProducts();
    setRefreshing(false);
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  return (
    <div className="animate-fade-in" style={{ padding: '1.5rem', maxWidth: 1200, margin: '0 auto', paddingBottom: '6rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem' }}>
        <button
          onClick={() => navigate('/')}
          style={{
            display: 'flex', alignItems: 'center', gap: 6,
            padding: '0.5rem 1rem',
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid rgba(139,92,246,0.25)',
            borderRadius: 10,
            cursor: 'pointer',
            color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: 600,
            transition: 'all 0.2s',
          }}
        >
          <ArrowLeft size={15} /> Back
        </button>
        <div style={{ flex: 1 }}>
          <h1 style={{
            fontSize: '2rem', fontWeight: 900, margin: 0,
            background: 'linear-gradient(135deg, #f8fafc 0%, #c4b5fd 100%)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
          }}>
            Samagri & Jodi Marketplace
          </h1>
          <p style={{ color: 'var(--text-tertiary)', marginTop: '0.5rem' }}>
            Browse products from SHGs and sellers
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          style={{
            display: 'flex', alignItems: 'center', gap: 6,
            padding: '0.5rem 1rem',
            background: 'rgba(139,92,246,0.1)',
            border: '1px solid rgba(139,92,246,0.25)',
            borderRadius: 10,
            cursor: refreshing ? 'not-allowed' : 'pointer',
            color: '#c4b5fd', fontSize: '0.85rem', fontWeight: 600,
          }}
        >
          <RefreshCw size={15} className={refreshing ? 'animate-spin' : ''} /> Refresh
        </button>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          <div style={{ width: 36, height: 36, borderRadius: '50%', border: '3px solid rgba(139,92,246,0.2)', borderTopColor: '#8b5cf6', margin: '0 auto 12px', animation: 'spin 0.7s linear infinite' }} />
          Loading products...
        </div>
      ) : products.length === 0 ? (
        <div style={{
          textAlign: 'center', padding: '3rem',
          background: 'rgba(255,255,255,0.03)',
          border: '1px solid rgba(139,92,246,0.15)',
          borderRadius: '1.25rem',
        }}>
          <Package size={48} style={{ color: 'rgba(139,92,246,0.25)', margin: '0 auto 12px' }} />
          <p style={{ color: 'var(--text-muted)', fontWeight: 500, margin: 0 }}>No products available</p>
          <button
            onClick={() => navigate('/sell')}
            style={{
              marginTop: '1rem',
              padding: '0.75rem 1.5rem',
              background: 'linear-gradient(135deg, #7c3aed, #a855f7)',
              border: 'none',
              borderRadius: 10,
              color: '#fff',
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            List Your First Product
          </button>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
          {products.map((product) => (
            <div
              key={product.id}
              style={CARD_STYLE}
              onClick={() => navigate(`/products/${product.id}`)}
              onMouseEnter={e => {
                e.currentTarget.style.border = '1px solid rgba(139,92,246,0.4)';
                e.currentTarget.style.boxShadow = '0 12px 30px rgba(0,0,0,0.5), 0 0 20px rgba(139,92,246,0.15)';
                e.currentTarget.style.transform = 'translateY(-3px)';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.border = '1px solid rgba(139,92,246,0.18)';
                e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.35)';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                <span style={{
                  padding: '3px 10px',
                  background: 'rgba(255,255,255,0.06)',
                  border: '1px solid rgba(255,255,255,0.08)',
                  borderRadius: 6,
                  fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase',
                  letterSpacing: '0.07em', color: 'var(--text-muted)',
                }}>
                  {product.category}
                </span>
                <span style={{
                  padding: '3px 10px',
                  background: product.stock > 0 ? 'rgba(16,185,129,0.12)' : 'rgba(239,68,68,0.12)',
                  border: product.stock > 0 ? '1px solid rgba(16,185,129,0.25)' : '1px solid rgba(239,68,68,0.25)',
                  borderRadius: 6,
                  fontSize: '0.72rem', fontWeight: 700, 
                  color: product.stock > 0 ? '#6ee7b7' : '#fca5a5',
                }}>
                  {product.stock > 0 ? 'In Stock' : 'Out of Stock'}
                </span>
              </div>

              <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '1rem' }}>
                {product.name}
              </h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: '1.25rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: 'var(--text-tertiary)', borderBottom: '1px solid rgba(255,255,255,0.06)', paddingBottom: 8 }}>
                  <span>Available</span>
                  <span style={{ color: 'var(--text-secondary)', fontWeight: 700 }}>{product.stock || product.quantity} {product.unit}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: 'var(--text-tertiary)' }}>
                  <span>Price</span>
                  <span style={{ color: '#a78bfa', fontWeight: 900, fontSize: '1.05rem' }}>₹{product.price?.toLocaleString() || 'N/A'}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: 'var(--text-tertiary)' }}>
                  <span>Seller</span>
                  <span style={{ color: 'var(--text-secondary)', fontWeight: 600 }}>{product.seller_name || 'SHG'}</span>
                </div>
              </div>

              <button
                onClick={(e) => {
                  e.stopPropagation();
                  navigate(`/checkout?productId=${product.id}`);
                }}
                style={{
                  width: '100%', padding: '0.7rem',
                  background: 'linear-gradient(135deg, #7c3aed, #a855f7)',
                  border: 'none', borderRadius: 10,
                  color: '#fff', fontWeight: 700, fontSize: '0.9rem',
                  cursor: 'pointer',
                  boxShadow: '0 4px 12px rgba(139,92,246,0.3)',
                  transition: 'all 0.2s',
                }}
                onMouseEnter={e => (e.currentTarget.style.boxShadow = '0 6px 20px rgba(139,92,246,0.5)')}
                onMouseLeave={e => (e.currentTarget.style.boxShadow = '0 4px 12px rgba(139,92,246,0.3)')}
              >
                Place Order
              </button>
            </div>
          ))}
        </div>
      )}

      <div style={{ borderTop: '1px solid rgba(139,92,246,0.12)', paddingTop: '2rem' }}>
        <h2 style={{
          display: 'flex', alignItems: 'center', gap: 10,
          fontSize: '1.35rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '1.25rem',
        }}>
          <Users size={24} style={{ color: '#a78bfa' }} />
          Agent Samagri: Bulk Procurements
        </h2>

        <div style={{
          background: 'rgba(139,92,246,0.06)',
          border: '1px solid rgba(139,92,246,0.22)',
          borderRadius: '1.25rem',
          padding: '2.5rem',
          textAlign: 'center',
          backdropFilter: 'blur(16px)',
          position: 'relative',
          overflow: 'hidden',
        }}>
          <div style={{
            position: 'absolute', top: 0, left: 0, right: 0, height: 2,
            background: 'linear-gradient(90deg, #7c3aed, #a855f7, #e879f9)',
          }} />
          <p style={{ color: 'var(--text-secondary)', fontWeight: 500, fontSize: '1rem', marginBottom: '1.5rem', maxWidth: 500, margin: '0 auto 1.5rem' }}>
            Join other SHGs to buy raw materials in bulk. Lower costs by up to{' '}
            <span style={{ color: '#c4b5fd', fontWeight: 900, fontSize: '1.2rem' }}>30%</span>{' '}
            by grouping your orders together.
          </p>
          <button
            onClick={() => navigate('/bulk-requests')}
            style={{
              padding: '0.75rem 2rem',
              background: 'linear-gradient(135deg, #7c3aed, #a855f7)',
              border: 'none', borderRadius: 12,
              color: '#fff', fontWeight: 700, fontSize: '0.95rem',
              cursor: 'pointer',
              boxShadow: '0 6px 20px rgba(139,92,246,0.4)',
              transition: 'all 0.2s', display: 'inline-flex', alignItems: 'center', gap: 8,
            }}
          >
            <ShoppingBag size={18} />
            View Bulk Requests
          </button>
        </div>
      </div>
    </div>
  );
};

export default Marketplace;
