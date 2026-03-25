import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { productsAPI, ordersAPI, paymentsAPI } from '../services/api';
import { ArrowLeft, Package, CreditCard, Wallet, CheckCircle, MapPin, Phone, User } from 'lucide-react';

const glass = {
  background: 'rgba(255,255,255,0.04)',
  border: '1px solid rgba(139,92,246,0.2)',
  borderRadius: '1.1rem',
  backdropFilter: 'blur(16px)',
  WebkitBackdropFilter: 'blur(16px)'
};

const Checkout = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const productId = searchParams.get('productId');
  
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [orderId, setOrderId] = useState(null);
  
  const [formData, setFormData] = useState({
    quantity: 1,
    delivery_name: user?.name || '',
    delivery_phone: user?.phone || '',
    delivery_address: user?.address || '',
    delivery_city: '',
    delivery_district: user?.district || '',
    delivery_pincode: user?.pincode || '',
    delivery_notes: '',
    payment_method: 'UPI',
    use_coins: false,
    coins_to_use: 0
  });

  useEffect(() => {
    if (productId) {
      fetchProduct();
    } else {
      navigate('/marketplace');
    }
  }, [productId]);

  useEffect(() => {
    if (user) {
      setFormData(prev => ({
        ...prev,
        delivery_name: prev.delivery_name || user.name || '',
        delivery_phone: prev.delivery_phone || user.phone || '',
        delivery_district: prev.delivery_district || user.district || '',
        delivery_address: prev.delivery_address || user.address || '',
        delivery_pincode: prev.delivery_pincode || user.pincode || ''
      }));
    }
  }, [user]);

  const fetchProduct = async () => {
    try {
      setLoading(true);
      const response = await productsAPI.getById(productId);
      setProduct(response.data);
    } catch (error) {
      console.error('Failed to fetch product:', error);
      navigate('/marketplace');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const calculateTotal = () => {
    if (!product) return { subtotal: 0, coinDiscount: 0, total: 0 };
    const subtotal = product.price * formData.quantity;
    const coinDiscount = formData.use_coins ? Math.min(formData.coins_to_use, subtotal * 0.1) : 0;
    const total = subtotal - coinDiscount;
    return { subtotal, coinDiscount, total };
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!product) return;

    try {
      setSubmitting(true);
      
      const orderData = {
        items: [{
          product_id: parseInt(productId),
          quantity: parseInt(formData.quantity)
        }],
        delivery_name: formData.delivery_name,
        delivery_phone: formData.delivery_phone,
        delivery_address: formData.delivery_address,
        delivery_city: formData.delivery_city,
        delivery_district: formData.delivery_district,
        delivery_pincode: formData.delivery_pincode,
        delivery_notes: formData.delivery_notes,
        payment_method: formData.payment_method,
        coins_used: formData.use_coins ? formData.coins_to_use : 0
      };

      const response = await ordersAPI.create(orderData);
      setOrderId(response.data.id);
      setSuccess(true);
    } catch (error) {
      console.error('Failed to create order:', error);
      alert('Failed to place order: ' + (error.response?.data?.detail || 'Unknown error'));
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
        <div style={{ width: 36, height: 36, borderRadius: '50%', border: '3px solid rgba(139,92,246,0.2)', borderTopColor: '#8b5cf6', margin: '0 auto 12px', animation: 'spin 0.7s linear infinite' }} />
        Loading checkout...
      </div>
    );
  }

  if (success) {
    return (
      <div className="animate-fade-in" style={{ padding: '2rem', maxWidth: 600, margin: '0 auto', textAlign: 'center' }}>
        <div style={{ ...glass, padding: '3rem' }}>
          <div style={{ width: 80, height: 80, borderRadius: '50%', background: 'linear-gradient(135deg, #10b981, #34d399)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem', boxShadow: '0 0 30px rgba(16,185,129,0.4)' }}>
            <CheckCircle size={40} color="#fff" />
          </div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 900, color: '#6ee7b7', margin: '0 0 0.5rem' }}>Order Placed!</h1>
          <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>Your order has been placed successfully</p>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>Order ID: #{orderId}</p>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
            <button onClick={() => navigate(`/orders/${orderId}`)} style={{ padding: '0.75rem 1.5rem', background: 'linear-gradient(135deg, #7c3aed, #a855f7)', border: 'none', borderRadius: 10, color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
              View Order
            </button>
            <button onClick={() => navigate('/marketplace')} style={{ padding: '0.75rem 1.5rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(139,92,246,0.3)', borderRadius: 10, color: '#c4b5fd', fontWeight: 600, cursor: 'pointer' }}>
              Continue Shopping
            </button>
          </div>
        </div>
      </div>
    );
  }

  const { subtotal, coinDiscount, total } = calculateTotal();

  return (
    <div className="animate-fade-in" style={{ padding: '1.5rem', maxWidth: 900, margin: '0 auto', paddingBottom: '6rem' }}>
      <button onClick={() => navigate(-1)} style={{ display: 'inline-flex', alignItems: 'center', gap: 7, color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.875rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 10, padding: '0.5rem 1rem', cursor: 'pointer', marginBottom: '1rem' }}>
        <ArrowLeft size={15} /> Back
      </button>

      <h1 style={{ fontSize: '1.75rem', fontWeight: 900, margin: '0 0 1.5rem', background: 'linear-gradient(135deg, #f8fafc 0%, #c4b5fd 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
        Checkout
      </h1>

      <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '1.5rem' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Product Summary */}
          <div style={{ ...glass, padding: '1.25rem' }}>
            <h2 style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Package size={18} style={{ color: '#a78bfa' }} /> Product Details
            </h2>
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
              <div style={{ width: 80, height: 80, borderRadius: 12, background: 'rgba(139,92,246,0.1)', border: '1px solid rgba(139,92,246,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <Package size={32} style={{ color: '#8b5cf6' }} />
              </div>
              <div style={{ flex: 1 }}>
                <h3 style={{ fontWeight: 700, color: 'var(--text-primary)', margin: '0 0 4px' }}>{product?.name}</h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: '0 0 8px' }}>{product?.category}</p>
                <p style={{ fontWeight: 900, color: '#a78bfa', fontSize: '1.25rem', margin: 0 }}>₹{product?.price?.toLocaleString()}</p>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <button type="button" onClick={() => setFormData(prev => ({ ...prev, quantity: Math.max(1, prev.quantity - 1) }))} style={{ width: 32, height: 32, borderRadius: 8, border: '1px solid rgba(139,92,246,0.3)', background: 'rgba(139,92,246,0.1)', color: '#c4b5fd', cursor: 'pointer', fontWeight: 700, fontSize: '1.1rem' }}>-</button>
                <span style={{ fontWeight: 700, color: 'var(--text-primary)', minWidth: 30, textAlign: 'center' }}>{formData.quantity}</span>
                <button type="button" onClick={() => setFormData(prev => ({ ...prev, quantity: Math.min(product?.stock || 10, prev.quantity + 1) }))} style={{ width: 32, height: 32, borderRadius: 8, border: '1px solid rgba(139,92,246,0.3)', background: 'rgba(139,92,246,0.1)', color: '#c4b5fd', cursor: 'pointer', fontWeight: 700, fontSize: '1.1rem' }}>+</button>
              </div>
            </div>
          </div>

          {/* Delivery Details */}
          <div style={{ ...glass, padding: '1.25rem' }}>
            <h2 style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: 8 }}>
              <MapPin size={18} style={{ color: '#a78bfa' }} /> Delivery Address
            </h2>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4, fontWeight: 600 }}>
                  <User size={12} style={{ marginRight: 4 }} /> Full Name *
                </label>
                <input type="text" name="delivery_name" value={formData.delivery_name} onChange={handleChange} required style={{ width: '100%', padding: '0.6rem 0.9rem', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 8, color: 'var(--text-primary)', fontSize: '0.9rem' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4, fontWeight: 600 }}>
                  <Phone size={12} style={{ marginRight: 4 }} /> Phone *
                </label>
                <input type="tel" name="delivery_phone" value={formData.delivery_phone} onChange={handleChange} required style={{ width: '100%', padding: '0.6rem 0.9rem', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 8, color: 'var(--text-primary)', fontSize: '0.9rem' }} />
              </div>
              <div style={{ gridColumn: '1 / -1' }}>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4, fontWeight: 600 }}>Address *</label>
                <textarea name="delivery_address" value={formData.delivery_address} onChange={handleChange} required rows={2} style={{ width: '100%', padding: '0.6rem 0.9rem', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 8, color: 'var(--text-primary)', fontSize: '0.9rem', resize: 'none' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4, fontWeight: 600 }}>City *</label>
                <input type="text" name="delivery_city" value={formData.delivery_city} onChange={handleChange} required style={{ width: '100%', padding: '0.6rem 0.9rem', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 8, color: 'var(--text-primary)', fontSize: '0.9rem' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4, fontWeight: 600 }}>District *</label>
                <input type="text" name="delivery_district" value={formData.delivery_district} onChange={handleChange} required style={{ width: '100%', padding: '0.6rem 0.9rem', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 8, color: 'var(--text-primary)', fontSize: '0.9rem' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4, fontWeight: 600 }}>Pincode *</label>
                <input type="text" name="delivery_pincode" value={formData.delivery_pincode} onChange={handleChange} required style={{ width: '100%', padding: '0.6rem 0.9rem', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 8, color: 'var(--text-primary)', fontSize: '0.9rem' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4, fontWeight: 600 }}>Notes (Optional)</label>
                <input type="text" name="delivery_notes" value={formData.delivery_notes} onChange={handleChange} placeholder="Any delivery instructions" style={{ width: '100%', padding: '0.6rem 0.9rem', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 8, color: 'var(--text-primary)', fontSize: '0.9rem' }} />
              </div>
            </div>
          </div>

          {/* Payment Method */}
          <div style={{ ...glass, padding: '1.25rem' }}>
            <h2 style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: 8 }}>
              <CreditCard size={18} style={{ color: '#a78bfa' }} /> Payment Method
            </h2>
            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              {['UPI', 'COD', 'Wallet', 'Card'].map(method => (
                <button key={method} type="button" onClick={() => setFormData(prev => ({ ...prev, payment_method: method }))} style={{ padding: '0.6rem 1.25rem', borderRadius: 10, border: formData.payment_method === method ? '1px solid rgba(139,92,246,0.5)' : '1px solid rgba(255,255,255,0.1)', background: formData.payment_method === method ? 'rgba(139,92,246,0.2)' : 'rgba(255,255,255,0.04)', color: formData.payment_method === method ? '#c4b5fd' : 'var(--text-muted)', fontWeight: 600, cursor: 'pointer', transition: 'all 0.2s' }}>
                  {method}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Order Summary */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ ...glass, padding: '1.25rem', position: 'sticky', top: '5rem' }}>
            <h2 style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '1rem', marginBottom: '1rem' }}>Order Summary</h2>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1rem', paddingBottom: '1rem', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                <span style={{ color: 'var(--text-muted)' }}>Subtotal ({formData.quantity} item)</span>
                <span style={{ color: 'var(--text-secondary)', fontWeight: 600 }}>₹{subtotal.toLocaleString()}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                <span style={{ color: 'var(--text-muted)' }}>Delivery</span>
                <span style={{ color: '#6ee7b7', fontWeight: 600 }}>FREE</span>
              </div>
              {coinDiscount > 0 && (
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Coin Discount</span>
                  <span style={{ color: '#6ee7b7', fontWeight: 600 }}>-₹{coinDiscount.toFixed(0)}</span>
                </div>
              )}
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
              <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>Total</span>
              <span style={{ fontWeight: 900, color: '#a78bfa', fontSize: '1.5rem' }}>₹{total.toLocaleString()}</span>
            </div>

            {user?.trust_coins > 0 && (
              <div style={{ marginBottom: '1rem', padding: '0.75rem', background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: 10 }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
                  <input type="checkbox" name="use_coins" checked={formData.use_coins} onChange={handleChange} style={{ width: 16, height: 16 }} />
                  <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                    Use Trust Coins ({user.trust_coins} available)
                  </span>
                </label>
                {formData.use_coins && (
                  <input type="number" name="coins_to_use" value={formData.coins_to_use} onChange={handleChange} min={0} max={Math.min(user.trust_coins, subtotal * 0.1)} placeholder="Coins to use" style={{ width: '100%', marginTop: '0.5rem', padding: '0.5rem', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(16,185,129,0.3)', borderRadius: 6, color: 'var(--text-primary)', fontSize: '0.85rem' }} />
                )}
              </div>
            )}

            <button type="submit" disabled={submitting} style={{ width: '100%', padding: '0.9rem', background: submitting ? 'rgba(139,92,246,0.3)' : 'linear-gradient(135deg, #7c3aed, #a855f7)', border: 'none', borderRadius: 12, color: '#fff', fontWeight: 800, fontSize: '1rem', cursor: submitting ? 'not-allowed' : 'pointer', boxShadow: '0 6px 20px rgba(139,92,246,0.4)', transition: 'all 0.2s' }}>
              {submitting ? 'Placing Order...' : 'Place Order'}
            </button>

            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textAlign: 'center', marginTop: '0.75rem' }}>
              By placing order, you agree to our terms & conditions
            </p>
          </div>
        </div>
      </form>
    </div>
  );
};

export default Checkout;
