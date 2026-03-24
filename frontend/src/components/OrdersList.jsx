import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ordersAPI } from '../services/api';
import { Package, Truck, CheckCircle, Clock, X } from 'lucide-react';

const STATUS_CONFIG = {
  Placed:    { color: '#60a5fa', bg: 'rgba(59,130,246,0.12)',   border: 'rgba(59,130,246,0.3)'  },
  Confirmed: { color: '#6ee7b7', bg: 'rgba(16,185,129,0.12)',  border: 'rgba(16,185,129,0.3)' },
  Shipped:   { color: '#c4b5fd', bg: 'rgba(139,92,246,0.12)',  border: 'rgba(139,92,246,0.3)' },
  Delivered: { color: '#6ee7b7', bg: 'rgba(16,185,129,0.15)',  border: 'rgba(16,185,129,0.35)'  },
  Cancelled: { color: '#fca5a5', bg: 'rgba(239,68,68,0.1)',   border: 'rgba(239,68,68,0.25)' },
};

const OrdersList = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => { fetchOrders(); }, [filter]);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const status = filter === 'all' ? null : filter;
      const response = await ordersAPI.getAll(status);
      setOrders(response.data);
    } catch { console.error('Failed to fetch orders'); }
    finally { setLoading(false); }
  };

  const getStatusIcon = (status) => {
    if (status === 'Delivered') return <CheckCircle size={13} />;
    if (status === 'Shipped')   return <Truck size={13} />;
    if (status === 'Cancelled') return <X size={13} />;
    return <Clock size={13} />;
  };

  if (loading) return (
    <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
      <div style={{ width: 36, height: 36, borderRadius: '50%', border: '3px solid rgba(139,92,246,0.2)', borderTopColor: '#8b5cf6', margin: '0 auto 12px', animation: 'spin 0.7s linear infinite' }} />
      Loading orders...
    </div>
  );

  return (
    <div className="animate-fade-in" style={{ padding: '1.5rem', maxWidth: 900, margin: '0 auto', paddingBottom: '6rem' }}>
      <div style={{ marginBottom: '1.75rem' }}>
        <h1 style={{
          fontSize: '1.75rem', fontWeight: 900, margin: '0 0 4px',
          background: 'linear-gradient(135deg, #f8fafc 0%, #c4b5fd 100%)',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
        }}>My Orders</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', margin: 0 }}>Track your purchases and sales</p>
      </div>

      {/* Filter Pills */}
      <div style={{ display: 'flex', gap: 8, overflowX: 'auto', paddingBottom: 4, marginBottom: '1.25rem' }}>
        {['all', 'Placed', 'Confirmed', 'Shipped', 'Delivered'].map((status) => {
          const active = filter === status;
          return (
            <button key={status} onClick={() => setFilter(status)} style={{
              padding: '6px 16px',
              borderRadius: 99,
              border: active ? '1px solid rgba(139,92,246,0.5)' : '1px solid rgba(255,255,255,0.08)',
              background: active ? 'rgba(139,92,246,0.2)' : 'rgba(255,255,255,0.04)',
              color: active ? '#c4b5fd' : 'var(--text-muted)',
              fontWeight: 600, fontSize: '0.8rem',
              cursor: 'pointer', whiteSpace: 'nowrap',
              boxShadow: active ? '0 0 10px rgba(139,92,246,0.2)' : 'none',
              transition: 'all 0.2s',
            }}>
              {status === 'all' ? 'All Orders' : status}
            </button>
          );
        })}
      </div>

      {orders.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(139,92,246,0.12)', borderRadius: '1.25rem' }}>
          <Package size={48} style={{ color: 'rgba(139,92,246,0.2)', margin: '0 auto 12px' }} />
          <p style={{ fontWeight: 600, color: 'var(--text-muted)', margin: 0 }}>No orders yet</p>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '6px 0 0' }}>Browse the marketplace or list your products</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {orders.map((order) => {
            const status = order.order_status;
            const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.Placed;
            return (
              <div
                key={order.id}
                onClick={() => navigate(`/orders/${order.id}`)}
                style={{
                  background: 'rgba(255,255,255,0.04)',
                  border: '1px solid rgba(139,92,246,0.15)',
                  borderRadius: '1rem',
                  padding: '1.1rem 1.25rem',
                  cursor: 'pointer',
                  backdropFilter: 'blur(12px)',
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12,
                  transition: 'all 0.25s',
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.border = '1px solid rgba(139,92,246,0.35)';
                  e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.4), 0 0 12px rgba(139,92,246,0.1)';
                  e.currentTarget.style.transform = 'translateX(3px)';
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.border = '1px solid rgba(139,92,246,0.15)';
                  e.currentTarget.style.boxShadow = 'none';
                  e.currentTarget.style.transform = 'translateX(0)';
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                    <span style={{
                      display: 'inline-flex', alignItems: 'center', gap: 5,
                      padding: '3px 10px', borderRadius: 99,
                      background: cfg.bg, border: `1px solid ${cfg.border}`,
                      color: cfg.color, fontSize: '0.72rem', fontWeight: 700,
                    }}>
                      {getStatusIcon(status)} {status}
                    </span>
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>#{order.order_number}</span>
                  </div>
                  <p style={{ fontWeight: 600, color: 'var(--text-primary)', margin: '0 0 3px', fontSize: '0.9rem' }}>
                    {order.items?.length || 1} item(s)
                  </p>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0 }}>
                    {new Date(order.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <p style={{ fontWeight: 900, color: '#a78bfa', margin: '0 0 3px', fontSize: '1.3rem' }}>
                    ₹{order.final_amount?.toLocaleString() || '0'}
                  </p>
                  <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', margin: 0 }}>{order.payment_method}</p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default OrdersList;
