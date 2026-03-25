import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { productsAPI, ordersAPI } from '../services/api';
import { ArrowLeft, Package, MapPin, Phone, User, ShoppingCart, Edit, Trash2 } from 'lucide-react';

const glass = { background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: '1.25rem', backdropFilter: 'blur(16px)', WebkitBackdropFilter: 'blur(16px)' };

const ProductDetail = () => {
  const { productId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [ordering, setOrdering] = useState(false);
  const [quantity, setQuantity] = useState(1);

  useEffect(() => {
    fetchProduct();
  }, [productId]);

  const fetchProduct = async () => {
    try {
      setLoading(true);
      const response = await productsAPI.getById(productId);
      setProduct(response.data);
    } catch (error) {
      console.error('Failed to fetch product:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOrder = async () => {
    try {
      setOrdering(true);
      const orderData = {
        items: [{
          product_id: product.id,
          product_name: product.name,
          quantity: quantity,
          unit_price: product.price,
          total_price: product.price * quantity
        }],
        delivery_name: user?.name || '',
        delivery_phone: user?.phone || '',
        delivery_address: user?.address || '',
        delivery_city: user?.district || '',
        delivery_district: user?.district || '',
        delivery_pincode: user?.pincode || '500001',
        payment_method: 'UPI'
      };

      const response = await ordersAPI.create(orderData);
      alert('Order placed successfully!');
      navigate(`/orders/${response.data.id}`);
    } catch (error) {
      alert('Failed to place order: ' + (error.response?.data?.detail || 'Unknown error'));
    } finally {
      setOrdering(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this product?')) return;
    try {
      await productsAPI.delete(productId);
      alert('Product deleted successfully');
      navigate('/my-products');
    } catch (error) {
      alert('Failed to delete product: ' + (error.response?.data?.detail || 'Unknown error'));
    }
  };

  if (loading) return (
    <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
      <div style={{ width: 36, height: 36, borderRadius: '50%', border: '3px solid rgba(139,92,246,0.2)', borderTopColor: '#8b5cf6', margin: '0 auto 12px', animation: 'spin 0.7s linear infinite' }} />
      Loading product details...
    </div>
  );

  if (!product) return (
    <div style={{ textAlign: 'center', padding: '3rem' }}>
      <p style={{ color: 'var(--text-muted)', marginBottom: 16, fontSize: '1.1rem' }}>Product not found</p>
      <button onClick={() => navigate('/marketplace')} style={{ color: '#a78bfa', fontWeight: 700, background: 'rgba(139,92,246,0.1)', border: '1px solid rgba(139,92,246,0.2)', padding: '0.6rem 1.25rem', borderRadius: 10, cursor: 'pointer' }}>
        Back to Marketplace
      </button>
    </div>
  );

  const isOwner = product.seller_id === user?.id;
  const totalPrice = product.price * quantity;

  return (
    <div className="animate-fade-in" style={{ padding: '1.5rem', maxWidth: 1000, margin: '0 auto', paddingBottom: '6rem' }}>
      {/* Back Button */}
      <button
        onClick={() => navigate(-1)}
        style={{ display: 'inline-flex', alignItems: 'center', gap: 7, color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.875rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 10, padding: '0.5rem 1rem', cursor: 'pointer', marginBottom: '1.5rem' }}
      >
        <ArrowLeft size={16} /> Back
      </button>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
        {/* Left: Product Media */}
        <div style={{ ...glass, overflow: 'hidden', height: 'fit-content' }}>
          {product.image_url ? (
            <img src={product.image_url} alt={product.name} style={{ width: '100%', height: 400, objectFit: 'cover' }} />
          ) : (
            <div style={{ width: '100%', height: 400, background: 'linear-gradient(135deg,rgba(139,92,246,0.12),rgba(168,85,247,0.08))', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Package size={80} style={{ color: 'rgba(139,92,246,0.3)' }} />
            </div>
          )}
        </div>

        {/* Right: Product Info & Actions */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ ...glass, padding: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
              <span style={{ padding: '4px 12px', background: 'rgba(139,92,246,0.12)', border: '1px solid rgba(139,92,246,0.25)', borderRadius: 99, fontSize: '0.7rem', fontWeight: 800, color: '#c4b5fd', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                {product.category}
              </span>
              {isOwner && (
                <div style={{ display: 'flex', gap: 8 }}>
                  <button onClick={() => navigate(`/products/${product.id}/edit`)} style={{ p: 8, background: 'rgba(59,130,246,0.1)', border: '1px solid rgba(59,130,246,0.2)', borderRadius: 8, color: '#93c5fd', cursor: 'pointer', display: 'flex', alignItems: 'center', padding: '6px' }}><Edit size={16} /></button>
                  <button onClick={handleDelete} style={{ p: 8, background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 8, color: '#fca5a5', cursor: 'pointer', display: 'flex', alignItems: 'center', padding: '6px' }}><Trash2 size={16} /></button>
                </div>
              )}
            </div>

            <h1 style={{ fontSize: '2rem', fontWeight: 900, color: 'var(--text-primary)', margin: '0 0 10px' }}>{product.name}</h1>
            <p style={{ color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: '1.5rem', fontSize: '0.95rem' }}>{product.description || 'No description available'}</p>

            <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: '1.5rem' }}>
              <span style={{ fontSize: '2.5rem', fontWeight: 900, color: '#a78bfa' }}>₹{product.price?.toLocaleString()}</span>
              <span style={{ color: 'var(--text-muted)', fontSize: '1rem' }}>per {product.unit}</span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', padding: '1rem 0', borderBlock: '1px solid rgba(255,255,255,0.06)', marginBottom: '1.5rem' }}>
              <div>
                <p style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 4 }}>Stock Available</p>
                <p style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-secondary)' }}>{product.quantity} {product.unit}</p>
              </div>
              <div>
                <p style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 4 }}>Status</p>
                <span style={{ padding: '3px 10px', borderRadius: 99, fontSize: '0.75rem', fontWeight: 800, background: product.status === 'Available' ? 'rgba(16,185,129,0.12)' : 'rgba(239,68,68,0.12)', border: `1px solid ${product.status === 'Available' ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)'}`, color: product.status === 'Available' ? '#6ee7b7' : '#fca5a5' }}>
                  {product.status}
                </span>
              </div>
            </div>

            {!isOwner && product.status === 'Available' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: 8 }}>Quantity to Order</label>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <div style={{ display: 'flex', alignItems: 'center', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(139,92,246,0.3)', borderRadius: 10, overflow: 'hidden' }}>
                      <button onClick={() => setQuantity(Math.max(1, quantity - 1))} style={{ width: 40, height: 40, border: 'none', background: 'transparent', color: '#fff', fontSize: '1.2rem', cursor: 'pointer', transition: 'background 0.2s' }} onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'} onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>-</button>
                      <input type="number" value={quantity} onChange={e => setQuantity(Math.max(1, Math.min(product.quantity, parseInt(e.target.value) || 1)))} style={{ width: 60, height: 40, border: 'none', background: 'transparent', color: '#fff', textAlign: 'center', fontWeight: 800, fontSize: '1rem', outline: 'none' }} />
                      <button onClick={() => setQuantity(Math.min(product.quantity, quantity + 1))} style={{ width: 40, height: 40, border: 'none', background: 'transparent', color: '#fff', fontSize: '1.2rem', cursor: 'pointer', transition: 'background 0.2s' }} onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'} onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>+</button>
                    </div>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>{product.unit}</span>
                  </div>
                </div>

                <div style={{ background: 'rgba(139,92,246,0.08)', borderRadius: 12, padding: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', border: '1px solid rgba(139,92,246,0.15)' }}>
                  <span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Total Price:</span>
                  <span style={{ color: '#c4b5fd', fontWeight: 900, fontSize: '1.3rem' }}>₹{totalPrice.toLocaleString()}</span>
                </div>

                <button onClick={handleOrder} disabled={ordering} style={{ width: '100%', padding: '1rem', background: 'linear-gradient(135deg,#7c3aed,#a855f7)', border: 'none', borderRadius: 12, color: '#fff', fontWeight: 800, fontSize: '1.1rem', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, boxShadow: '0 4px 15px rgba(139,92,246,0.4)', transition: 'transform 0.2s' }} onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-2px)'} onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}>
                  <ShoppingCart size={20} />
                  {ordering ? 'Processing...' : 'Place Order Now'}
                </button>
              </div>
            )}
          </div>

          {/* Seller / Location Info */}
          <div style={{ ...glass, padding: '1.25rem' }}>
            <h2 style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '1rem' }}>Seller & Logistics</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'rgba(139,92,246,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><User size={18} style={{ color: '#a78bfa' }} /></div>
                <div>
                  <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 2 }}>Owned By</p>
                  <p style={{ fontWeight: 700, color: 'var(--text-secondary)', margin: 0 }}>{product.seller_name || 'SHG Member'}</p>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'rgba(139,92,246,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><MapPin size={18} style={{ color: '#a78bfa' }} /></div>
                <div>
                  <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 2 }}>District Location</p>
                  <p style={{ fontWeight: 700, color: 'var(--text-secondary)', margin: 0 }}>{product.district || 'Andhra Pradesh'}</p>
                </div>
              </div>
              {!isOwner && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'rgba(139,92,246,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Phone size={18} style={{ color: '#a78bfa' }} /></div>
                  <div>
                    <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 2 }}>Communication</p>
                    <p style={{ fontWeight: 700, color: 'var(--text-secondary)', margin: 0 }}>Verified via Ooumph Network</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetail;
