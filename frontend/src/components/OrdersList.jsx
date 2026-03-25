import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ordersAPI } from '../services/api';
import { Package, Truck, CheckCircle, Clock, X, Search, Calendar, Filter, AlertCircle } from 'lucide-react';

const STATUS_CONFIG = {
  Placed:    { color: '#60a5fa', bg: 'rgba(59,130,246,0.12)',   border: 'rgba(59,130,246,0.3)'  },
  Confirmed: { color: '#6ee7b7', bg: 'rgba(16,185,129,0.12)',  border: 'rgba(16,185,129,0.3)' },
  Processing:{ color: '#fcd34d', bg: 'rgba(245,158,11,0.12)',  border: 'rgba(245,158,11,0.3)' },
  Shipped:   { color: '#c4b5fd', bg: 'rgba(139,92,246,0.12)',  border: 'rgba(139,92,246,0.3)' },
  Delivered: { color: '#6ee7b7', bg: 'rgba(16,185,129,0.15)',  border: 'rgba(16,185,129,0.35)'  },
  Cancelled: { color: '#fca5a5', bg: 'rgba(239,68,68,0.1)',   border: 'rgba(239,68,68,0.25)' },
  Refunded:  { color: '#fca5a5', bg: 'rgba(239,68,68,0.1)',   border: 'rgba(239,68,68,0.25)' },
};

const glass = {
  background: 'rgba(255,255,255,0.04)',
  border: '1px solid rgba(139,92,246,0.2)',
  borderRadius: '1.1rem',
  backdropFilter: 'blur(16px)',
  WebkitBackdropFilter: 'blur(16px)'
};

const OrdersList = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [dateFilter, setDateFilter] = useState('all');
  const [showFilters, setShowFilters] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => { 
    fetchOrders(); 
  }, [filter, dateFilter, page]);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const status = filter === 'all' ? null : filter;
      const response = await ordersAPI.getAll(status);
      const data = response.data;
      const ordersList = data.items || data || [];
      setOrders(Array.isArray(ordersList) ? ordersList : []);
      setTotalPages(data.total_pages || 1);
    } catch { console.error('Failed to fetch orders'); }
    finally { setLoading(false); }
  };

  const getStatusIcon = (status) => {
    if (status === 'Delivered') return <CheckCircle size={13} />;
    if (status === 'Shipped')   return <Truck size={13} />;
    if (status === 'Cancelled' || status === 'Refunded') return <X size={13} />;
    return <Clock size={13} />;
  };

  const filterByDate = (order) => {
    if (dateFilter === 'all') return true;
    const orderDate = new Date(order.created_at);
    const now = new Date();
    const diffDays = Math.floor((now - orderDate) / (1000 * 60 * 60 * 24));
    
    switch(dateFilter) {
      case 'today': return diffDays === 0;
      case 'week': return diffDays <= 7;
      case 'month': return diffDays <= 30;
      case '3months': return diffDays <= 90;
      default: return true;
    }
  };

  const filterBySearch = (order) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      order.order_number?.toLowerCase().includes(query) ||
      order.items?.some(item => item.product_name?.toLowerCase().includes(query))
    );
  };

  const filteredOrders = orders.filter(filterByDate).filter(filterBySearch);

  const handleCancelOrder = async (orderId) => {
    if (!window.confirm('Are you sure you want to cancel this order?')) return;
    try {
      await ordersAPI.updateStatus(orderId, 'Cancelled');
      fetchOrders();
    } catch (error) {
      alert('Failed to cancel order: ' + (error.response?.data?.detail || 'Unknown error'));
    }
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

      {/* Search and Filter Bar */}
      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: 200, position: 'relative' }}>
          <Search size={16} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text"
            placeholder="Search orders..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '0.6rem 0.9rem 0.6rem 2.25rem',
              background: 'rgba(255,255,255,0.04)',
              border: '1px solid rgba(139,92,246,0.2)',
              borderRadius: 10,
              color: 'var(--text-primary)',
              fontSize: '0.875rem'
            }}
          />
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          style={{
            display: 'flex', alignItems: 'center', gap: 6,
            padding: '0.6rem 1rem',
            background: showFilters ? 'rgba(139,92,246,0.2)' : 'rgba(255,255,255,0.04)',
            border: '1px solid rgba(139,92,246,0.2)',
            borderRadius: 10,
            color: showFilters ? '#c4b5fd' : 'var(--text-muted)',
            cursor: 'pointer',
            fontWeight: 600
          }}
        >
          <Filter size={16} /> Filters
        </button>
      </div>

      {/* Expanded Filters */}
      {showFilters && (
        <div style={{ ...glass, padding: '1rem', marginBottom: '1rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '0.75rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 4, fontWeight: 600 }}>Date Range</label>
              <select
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
                style={{ width: '100%', padding: '0.5rem', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 8, color: 'var(--text-primary)', fontSize: '0.85rem' }}
              >
                <option value="all">All Time</option>
                <option value="today">Today</option>
                <option value="week">Last 7 Days</option>
                <option value="month">Last 30 Days</option>
                <option value="3months">Last 3 Months</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Filter Pills */}
      <div style={{ display: 'flex', gap: 8, overflowX: 'auto', paddingBottom: 4, marginBottom: '1.25rem' }}>
        {['all', 'Placed', 'Confirmed', 'Shipped', 'Delivered', 'Cancelled'].map((status) => {
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

      {/* Results Count */}
      <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
        Showing {filteredOrders.length} order{filteredOrders.length !== 1 ? 's' : ''}
      </p>

      {filteredOrders.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(139,92,246,0.12)', borderRadius: '1.25rem' }}>
          <Package size={48} style={{ color: 'rgba(139,92,246,0.2)', margin: '0 auto 12px' }} />
          <p style={{ fontWeight: 600, color: 'var(--text-muted)', margin: 0 }}>No orders found</p>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '6px 0 0' }}>
            {searchQuery ? 'Try adjusting your search or filters' : 'Browse the marketplace or list your products'}
          </p>
          <button
            onClick={() => navigate('/marketplace')}
            style={{
              marginTop: '1rem',
              padding: '0.6rem 1.25rem',
              background: 'linear-gradient(135deg, #7c3aed, #a855f7)',
              border: 'none',
              borderRadius: 10,
              color: '#fff',
              fontWeight: 700,
              cursor: 'pointer'
            }}
          >
            Browse Marketplace
          </button>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {filteredOrders.map((order) => {
            const status = order.order_status;
            const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.Placed;
            const canCancel = status === 'Placed' || status === 'Confirmed';
            const isSeller = order.seller_id === user?.id;
            
            return (
              <div
                key={order.id}
                style={{
                  background: 'rgba(255,255,255,0.04)',
                  border: '1px solid rgba(139,92,246,0.15)',
                  borderRadius: '1rem',
                  padding: '1.1rem 1.25rem',
                  backdropFilter: 'blur(12px)',
                  transition: 'all 0.25s',
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.border = '1px solid rgba(139,92,246,0.35)';
                  e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.4), 0 0 12px rgba(139,92,246,0.1)';
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.border = '1px solid rgba(139,92,246,0.15)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                <div 
                  onClick={() => navigate(`/orders/${order.id}`)}
                  style={{ cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}
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
                      {isSeller && (
                        <span style={{ fontSize: '0.7rem', padding: '2px 8px', background: 'rgba(245,158,11,0.12)', border: '1px solid rgba(245,158,11,0.25)', borderRadius: 6, color: '#fcd34d' }}>
                          SELLING
                        </span>
                      )}
                    </div>
                    <p style={{ fontWeight: 600, color: 'var(--text-primary)', margin: '0 0 3px', fontSize: '0.9rem' }}>
                      {order.items?.length || 1} item(s) - {order.items?.map(i => i.product_name).join(', ').substring(0, 40)}...
                    </p>
                    <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0, display: 'flex', alignItems: 'center', gap: 6 }}>
                      <Calendar size={12} />
                      {new Date(order.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                    </p>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <p style={{ fontWeight: 900, color: '#a78bfa', margin: '0 0 3px', fontSize: '1.3rem' }}>
                      ₹{order.final_amount?.toLocaleString() || '0'}
                    </p>
                    <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', margin: 0 }}>{order.payment_method} • {order.payment_status}</p>
                  </div>
                </div>
                
                {canCancel && !isSeller && (
                  <div style={{ marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(255,255,255,0.06)', display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleCancelOrder(order.id); }}
                      style={{
                        display: 'flex', alignItems: 'center', gap: 4,
                        padding: '0.4rem 0.75rem',
                        background: 'rgba(239,68,68,0.1)',
                        border: '1px solid rgba(239,68,68,0.25)',
                        borderRadius: 8,
                        color: '#fca5a5',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        cursor: 'pointer'
                      }}
                    >
                      <AlertCircle size={12} /> Cancel Order
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem', marginTop: '1.5rem' }}>
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            style={{
              padding: '0.5rem 1rem',
              background: 'rgba(255,255,255,0.04)',
              border: '1px solid rgba(139,92,246,0.2)',
              borderRadius: 8,
              color: page === 1 ? 'var(--text-muted)' : '#c4b5fd',
              cursor: page === 1 ? 'not-allowed' : 'pointer',
              fontWeight: 600
            }}
          >
            Previous
          </button>
          <span style={{ padding: '0.5rem 1rem', color: 'var(--text-secondary)' }}>
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            style={{
              padding: '0.5rem 1rem',
              background: 'rgba(255,255,255,0.04)',
              border: '1px solid rgba(139,92,246,0.2)',
              borderRadius: 8,
              color: page === totalPages ? 'var(--text-muted)' : '#c4b5fd',
              cursor: page === totalPages ? 'not-allowed' : 'pointer',
              fontWeight: 600
            }}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default OrdersList;
