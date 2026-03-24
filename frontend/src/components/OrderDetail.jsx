import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ordersAPI, paymentsAPI } from '../services/api';
import { ArrowLeft, Package, Phone, MapPin } from 'lucide-react';

const glass = { background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: '1.1rem', backdropFilter: 'blur(16px)', WebkitBackdropFilter: 'blur(16px)' };

const OrderDetail = () => {
  const { orderId } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchOrder(); }, [orderId]);

  const fetchOrder = async () => {
    try { setLoading(true); const r = await ordersAPI.getById(orderId); setOrder(r.data); }
    catch { console.error('Failed to fetch order'); }
    finally { setLoading(false); }
  };

  const handlePayment = async () => {
    try { await paymentsAPI.initiate(orderId, false, 0); alert('Payment initiated! (In production, this would open UPI app)'); fetchOrder(); }
    catch (e) { alert('Payment failed: ' + (e.response?.data?.detail || 'Unknown error')); }
  };

  if (loading) return (
    <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
      <div style={{ width: 36, height: 36, borderRadius: '50%', border: '3px solid rgba(139,92,246,0.2)', borderTopColor: '#8b5cf6', margin: '0 auto 12px', animation: 'spin 0.7s linear infinite' }} />
      Loading order...
    </div>
  );

  if (!order) return (
    <div style={{ textAlign: 'center', padding: '3rem' }}>
      <p style={{ color: 'var(--text-muted)', marginBottom: 12 }}>Order not found</p>
      <button onClick={() => navigate('/orders')} style={{ color: '#a78bfa', fontWeight: 600, background: 'none', border: 'none', cursor: 'pointer' }}>Back to Orders</button>
    </div>
  );

  const STATUS_STEPS = ['Placed', 'Confirmed', 'Shipped', 'Delivered'];
  const stepIdx = STATUS_STEPS.indexOf(order.order_status);
  const pct = ((stepIdx + 1) / STATUS_STEPS.length) * 100;

  return (
    <div className="animate-fade-in" style={{ padding: '1.5rem', maxWidth: 800, margin: '0 auto', paddingBottom: '6rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <button onClick={() => navigate('/orders')} style={{ display: 'inline-flex', alignItems: 'center', gap: 7, color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.875rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 10, padding: '0.5rem 1rem', cursor: 'pointer', alignSelf: 'flex-start' }}>
        <ArrowLeft size={15} /> Back to Orders
      </button>

      {/* Order Header */}
      <div style={{ ...glass, padding: '1.25rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1 style={{ fontWeight: 900, color: 'var(--text-primary)', fontSize: '1.3rem', margin: '0 0 5px' }}>Order #{order.order_number}</h1>
          <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.875rem' }}>Placed on {new Date(order.created_at).toLocaleDateString()}</p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <p style={{ fontWeight: 900, color: '#a78bfa', fontSize: '1.5rem', margin: '0 0 4px' }}>₹{order.final_amount?.toLocaleString() || 0}</p>
          <span style={{ padding: '3px 10px', borderRadius: 99, fontSize: '0.72rem', fontWeight: 800, background: order.payment_status === 'Completed' ? 'rgba(16,185,129,0.12)' : 'rgba(245,158,11,0.12)', color: order.payment_status === 'Completed' ? '#6ee7b7' : '#fcd34d', border: `1px solid ${order.payment_status === 'Completed' ? 'rgba(16,185,129,0.3)' : 'rgba(245,158,11,0.3)'}` }}>
            {order.payment_status}
          </span>
        </div>
      </div>

      {/* Status Timeline */}
      <div style={{ ...glass, padding: '1.25rem' }}>
        <h2 style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '1rem', marginBottom: '1.25rem' }}>Order Status</h2>
        <div style={{ position: 'relative', display: 'flex', justifyContent: 'space-between' }}>
          {/* Track line */}
          <div style={{ position: 'absolute', top: 18, left: 0, width: '100%', height: 2, background: 'rgba(255,255,255,0.06)' }}>
            <div style={{ height: '100%', width: `${pct}%`, background: 'linear-gradient(90deg,#7c3aed,#a855f7)', transition: 'width 0.6s ease' }} />
          </div>
          {STATUS_STEPS.map((step, i) => {
            const done = i <= stepIdx;
            return (
              <div key={step} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', zIndex: 1 }}>
                <div style={{ width: 36, height: 36, borderRadius: '50%', background: done ? 'linear-gradient(135deg,#7c3aed,#a855f7)' : 'rgba(255,255,255,0.06)', border: `2px solid ${done ? '#a855f7' : 'rgba(255,255,255,0.1)'}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, color: done ? '#fff' : 'var(--text-muted)', fontSize: '0.85rem', boxShadow: done ? '0 0 12px rgba(168,85,247,0.4)' : 'none', transition: 'all 0.3s' }}>
                  {i + 1}
                </div>
                <p style={{ fontSize: '0.72rem', fontWeight: 600, marginTop: 8, color: done ? '#c4b5fd' : 'var(--text-muted)', textAlign: 'center' }}>{step}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Items */}
      <div style={{ ...glass, padding: '1.25rem' }}>
        <h2 style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '1rem', marginBottom: '0.9rem' }}>Order Items</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {order.items?.map((item, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 12, background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 10, padding: '0.75rem' }}>
              <div style={{ width: 52, height: 52, borderRadius: 10, background: 'rgba(139,92,246,0.1)', border: '1px solid rgba(139,92,246,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <Package size={22} style={{ color: '#8b5cf6' }} />
              </div>
              <div style={{ flex: 1 }}>
                <p style={{ fontWeight: 700, color: 'var(--text-primary)', margin: '0 0 3px', fontSize: '0.9rem' }}>{item.product_name}</p>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0 }}>Qty: {item.quantity}</p>
              </div>
              <div style={{ textAlign: 'right' }}>
                <p style={{ fontWeight: 800, color: '#a78bfa', margin: '0 0 3px' }}>₹{item.total_price?.toLocaleString() || 0}</p>
                <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', margin: 0 }}>₹{item.unit_price} each</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Delivery */}
      <div style={{ ...glass, padding: '1.25rem' }}>
        <h2 style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '1rem', marginBottom: '0.9rem' }}>Delivery Address</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(200px,1fr))', gap: '0.9rem' }}>
          <div>
            <p style={{ fontWeight: 700, color: 'var(--text-secondary)', margin: '0 0 5px' }}>{order.delivery_name}</p>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', margin: 0 }}>{order.delivery_address}</p>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <p style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.875rem', color: 'var(--text-secondary)', margin: 0 }}>
              <Phone size={14} style={{ color: '#a78bfa' }} />{order.delivery_phone}
            </p>
            <p style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.875rem', color: 'var(--text-secondary)', margin: 0 }}>
              <MapPin size={14} style={{ color: '#a78bfa' }} />{order.delivery_city}, {order.delivery_district} - {order.delivery_pincode}
            </p>
            {order.tracking_number && <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 6, padding: '3px 8px', display: 'inline-block' }}>Tracking: {order.tracking_number}</span>}
          </div>
        </div>
      </div>

      {/* Pay Now */}
      {order.payment_status !== 'Completed' && (
        <div style={{ background: 'linear-gradient(135deg,rgba(139,92,246,0.2),rgba(168,85,247,0.15))', border: '1px solid rgba(139,92,246,0.35)', borderRadius: '1.1rem', padding: '1.25rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <h3 style={{ fontWeight: 800, color: '#c4b5fd', margin: '0 0 4px', fontSize: '1rem' }}>Complete Payment</h3>
            <p style={{ color: 'var(--text-secondary)', margin: 0, fontSize: '0.875rem' }}>Amount: ₹{order.final_amount?.toLocaleString() || 0}</p>
          </div>
          <button onClick={handlePayment} style={{ padding: '0.65rem 1.5rem', background: 'linear-gradient(135deg,#7c3aed,#a855f7)', border: 'none', borderRadius: 10, color: '#fff', fontWeight: 800, fontSize: '1rem', cursor: 'pointer', boxShadow: '0 4px 14px rgba(139,92,246,0.4)' }}>
            Pay Now
          </button>
        </div>
      )}
    </div>
  );
};

export default OrderDetail;
