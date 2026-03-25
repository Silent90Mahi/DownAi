import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { suppliersAPI } from '../services/api';
import { 
  ArrowLeft, Star, MapPin, Award, Users, Package, CheckCircle2,
  MessageSquare, FileText, ThumbsUp, Send, X, Building, Shield
} from 'lucide-react';

const glass = { 
  background: 'rgba(255,255,255,0.04)', 
  border: '1px solid rgba(139,92,246,0.2)', 
  borderRadius: '1rem', 
  backdropFilter: 'blur(16px)', 
  WebkitBackdropFilter: 'blur(16px)' 
};

const SupplierProfile = () => {
  const { supplierId } = useParams();
  const navigate = useNavigate();
  const [supplier, setSupplier] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showConnectModal, setShowConnectModal] = useState(false);
  const [showQuoteModal, setShowQuoteModal] = useState(false);
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [connectMessage, setConnectMessage] = useState('');
  const [selectedMaterial, setSelectedMaterial] = useState(null);
  const [quoteQuantity, setQuoteQuantity] = useState(100);
  const [quoteDescription, setQuoteDescription] = useState('');
  const [reviewData, setReviewData] = useState({ rating: 5, title: '', content: '', quality_rating: 5, delivery_rating: 5, communication_rating: 5, value_rating: 5 });

  useEffect(() => {
    fetchSupplier();
  }, [supplierId]);

  const fetchSupplier = async () => {
    try {
      setLoading(true);
      const res = await suppliersAPI.getSupplier(supplierId);
      setSupplier(res.data);
    } catch (error) {
      console.error('Failed to fetch supplier:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async () => {
    try {
      await suppliersAPI.connect(supplierId, connectMessage);
      setShowConnectModal(false);
      setConnectMessage('');
      alert('Connection request sent successfully!');
    } catch (error) {
      alert('Failed to send connection request');
    }
  };

  const handleRequestQuote = async () => {
    try {
      await suppliersAPI.requestQuote({
        supplier_id: parseInt(supplierId),
        material_id: selectedMaterial?.id,
        material_name: selectedMaterial?.name || 'General inquiry',
        quantity: quoteQuantity,
        unit: selectedMaterial?.unit || 'piece',
        description: quoteDescription,
        delivery_district: supplier?.district
      });
      setShowQuoteModal(false);
      setSelectedMaterial(null);
      setQuoteQuantity(100);
      setQuoteDescription('');
      alert('Quote request sent successfully!');
    } catch (error) {
      alert('Failed to send quote request');
    }
  };

  const handleSubmitReview = async () => {
    try {
      await suppliersAPI.createReview({
        supplier_id: parseInt(supplierId),
        ...reviewData
      });
      setShowReviewModal(false);
      setReviewData({ rating: 5, title: '', content: '', quality_rating: 5, delivery_rating: 5, communication_rating: 5, value_rating: 5 });
      fetchSupplier();
      alert('Review submitted successfully!');
    } catch (error) {
      alert('Failed to submit review');
    }
  };

  const handleMarkHelpful = async (reviewId) => {
    try {
      await suppliersAPI.markReviewHelpful(reviewId);
      fetchSupplier();
    } catch (error) {
      console.error('Failed to mark helpful:', error);
    }
  };

  const renderStars = (rating, interactive = false, onChange = null) => {
    return [...Array(5)].map((_, i) => (
      <Star
        key={i}
        size={interactive ? 24 : 16}
        style={{
          cursor: interactive ? 'pointer' : 'default',
          color: i < rating ? '#fcd34d' : 'rgba(255,255,255,0.2)',
          fill: i < rating ? '#fcd34d' : 'transparent'
        }}
        onClick={() => interactive && onChange && onChange(i + 1)}
      />
    ));
  };

  if (loading) {
    return (
      <div style={{ padding: '3rem', textAlign: 'center' }}>
        <div style={{ width: 40, height: 40, borderRadius: '50%', border: '3px solid rgba(139,92,246,0.2)', borderTopColor: '#8b5cf6', margin: '0 auto 1rem', animation: 'spin 0.7s linear infinite' }} />
        <p style={{ color: 'var(--text-muted)' }}>Loading supplier profile...</p>
      </div>
    );
  }

  if (!supplier) {
    return (
      <div style={{ padding: '3rem', textAlign: 'center' }}>
        <p style={{ color: 'var(--text-muted)' }}>Supplier not found</p>
        <button onClick={() => navigate('/suppliers')} style={{ marginTop: '1rem', padding: '0.5rem 1rem', background: 'linear-gradient(135deg, #7c3aed, #a855f7)', border: 'none', borderRadius: 8, color: '#fff', cursor: 'pointer' }}>
          Back to Suppliers
        </button>
      </div>
    );
  }

  return (
    <div className="animate-fade-in" style={{ padding: '1.5rem', maxWidth: 1100, margin: '0 auto', paddingBottom: '6rem' }}>
      <button onClick={() => navigate('/suppliers')} style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', marginBottom: '1rem', fontSize: '0.9rem' }}>
        <ArrowLeft size={18} /> Back to Suppliers
      </button>

      <div style={{ ...glass, padding: '1.5rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1.5rem', alignItems: 'flex-start' }}>
          <div style={{ width: 80, height: 80, borderRadius: '50%', background: 'linear-gradient(135deg, rgba(139,92,246,0.2), rgba(16,185,129,0.1))', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Building size={36} style={{ color: 'rgba(139,92,246,0.6)' }} />
          </div>
          <div style={{ flex: 1, minWidth: 250 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
              <h1 style={{ fontSize: '1.5rem', fontWeight: 900, margin: 0, background: 'linear-gradient(135deg, #f8fafc, #c4b5fd)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                {supplier.business_name}
              </h1>
              {supplier.is_verified && (
                <span style={{ display: 'flex', alignItems: 'center', gap: 4, padding: '3px 10px', background: 'rgba(16,185,129,0.15)', border: '1px solid rgba(16,185,129,0.3)', borderRadius: 99, fontSize: '0.75rem', fontWeight: 700, color: '#6ee7b7' }}>
                  <CheckCircle2 size={12} /> Verified
                </span>
              )}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: 8 }}>
              <MapPin size={14} /> {supplier.district}, {supplier.state}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 12 }}>
              {renderStars(Math.round(supplier.rating))}
              <span style={{ fontWeight: 700, color: '#fcd34d', marginLeft: 4 }}>{supplier.rating?.toFixed(1)}</span>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>({supplier.total_reviews} reviews)</span>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {supplier.categories_supplied?.map((cat, i) => (
                <span key={i} style={{ padding: '4px 12px', background: 'rgba(139,92,246,0.12)', border: '1px solid rgba(139,92,246,0.25)', borderRadius: 99, fontSize: '0.75rem', fontWeight: 600, color: '#c4b5fd' }}>
                  {cat}
                </span>
              ))}
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <button onClick={() => setShowConnectModal(true)} style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '0.6rem 1.2rem', background: 'linear-gradient(135deg, #7c3aed, #a855f7)', border: 'none', borderRadius: 8, color: '#fff', fontWeight: 700, fontSize: '0.85rem', cursor: 'pointer' }}>
              <Users size={16} /> Connect
            </button>
            <button onClick={() => setShowQuoteModal(true)} style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '0.6rem 1.2rem', background: 'rgba(16,185,129,0.15)', border: '1px solid rgba(16,185,129,0.3)', borderRadius: 8, color: '#6ee7b7', fontWeight: 700, fontSize: '0.85rem', cursor: 'pointer' }}>
              <FileText size={16} /> Request Quote
            </button>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
        {[
          { icon: Shield, label: 'Trust Score', value: supplier.trust_score, suffix: '', color: '#a78bfa' },
          { icon: Star, label: 'Rating', value: supplier.rating?.toFixed(1), suffix: '/5', color: '#fcd34d' },
          { icon: Users, label: 'Connections', value: supplier.total_connections, suffix: '', color: '#6ee7b7' },
          { icon: Package, label: 'Materials', value: supplier.total_materials, suffix: '', color: '#93c5fd' },
        ].map((stat, i) => (
          <div key={i} style={{ ...glass, padding: '1rem', textAlign: 'center' }}>
            <stat.icon size={24} style={{ color: stat.color, marginBottom: 6 }} />
            <div style={{ fontSize: '1.5rem', fontWeight: 900, color: stat.color }}>{stat.value}{stat.suffix}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{stat.label}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
        <div style={{ ...glass, padding: '1.25rem' }}>
          <h3 style={{ fontWeight: 800, color: 'var(--text-primary)', margin: '0 0 1rem', fontSize: '1rem' }}>Service Areas</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {supplier.service_areas?.map((area, i) => (
              <span key={i} style={{ padding: '4px 12px', background: 'rgba(59,130,246,0.12)', border: '1px solid rgba(59,130,246,0.25)', borderRadius: 99, fontSize: '0.8rem', color: '#93c5fd' }}>
                {area}
              </span>
            ))}
          </div>
        </div>
        <div style={{ ...glass, padding: '1.25rem' }}>
          <h3 style={{ fontWeight: 800, color: 'var(--text-primary)', margin: '0 0 1rem', fontSize: '1rem' }}>Address</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>{supplier.address}</p>
        </div>
      </div>

      <div style={{ ...glass, padding: '1.25rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 style={{ fontWeight: 800, color: 'var(--text-primary)', margin: 0, fontSize: '1rem' }}>Materials Available</h3>
        </div>
        {supplier.materials?.length > 0 ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '0.75rem' }}>
            {supplier.materials.map((material, i) => (
              <div key={i} style={{ padding: '0.75rem', background: 'rgba(255,255,255,0.03)', borderRadius: 8, border: '1px solid rgba(139,92,246,0.15)' }}>
                <div style={{ fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4 }}>{material.name}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4 }}>{material.category}</div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 800, color: '#a78bfa' }}>₹{material.price_per_unit}/{material.unit}</span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Stock: {material.stock_available}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center' }}>No materials listed</p>
        )}
      </div>

      <div style={{ ...glass, padding: '1.25rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 style={{ fontWeight: 800, color: 'var(--text-primary)', margin: 0, fontSize: '1rem' }}>Reviews ({supplier.total_reviews})</h3>
          <button onClick={() => setShowReviewModal(true)} style={{ padding: '6px 14px', background: 'rgba(139,92,246,0.15)', border: '1px solid rgba(139,92,246,0.3)', borderRadius: 8, color: '#c4b5fd', fontWeight: 600, fontSize: '0.8rem', cursor: 'pointer' }}>
            Write Review
          </button>
        </div>
        {supplier.recent_reviews?.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {supplier.recent_reviews.map((review, i) => (
              <div key={i} style={{ padding: '1rem', background: 'rgba(255,255,255,0.03)', borderRadius: 8, border: '1px solid rgba(139,92,246,0.15)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                  <div>
                    <div style={{ fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4 }}>{review.reviewer_name}</div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      {renderStars(review.rating)}
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {new Date(review.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  {review.is_verified_purchase && (
                    <span style={{ padding: '2px 8px', background: 'rgba(16,185,129,0.12)', border: '1px solid rgba(16,185,129,0.25)', borderRadius: 99, fontSize: '0.65rem', fontWeight: 700, color: '#6ee7b7' }}>
                      Verified Purchase
                    </span>
                  )}
                </div>
                {review.title && <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: 4 }}>{review.title}</div>}
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', margin: '0 0 8px' }}>{review.content}</p>
                <div style={{ display: 'flex', gap: 12, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  <span>Quality: {review.quality_rating}/5</span>
                  <span>Delivery: {review.delivery_rating}/5</span>
                  <span>Communication: {review.communication_rating}/5</span>
                  <span>Value: {review.value_rating}/5</span>
                </div>
                <button onClick={() => handleMarkHelpful(review.id)} style={{ display: 'flex', alignItems: 'center', gap: 4, marginTop: 8, padding: '4px 10px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 6, color: 'var(--text-muted)', fontSize: '0.75rem', cursor: 'pointer' }}>
                  <ThumbsUp size={12} /> Helpful ({review.helpful_count})
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center' }}>No reviews yet. Be the first to review!</p>
        )}
      </div>

      {showConnectModal && (
        <Modal title="Connect with Supplier" onClose={() => setShowConnectModal(false)}>
          <textarea
            value={connectMessage}
            onChange={(e) => setConnectMessage(e.target.value)}
            placeholder="Introduce yourself and explain why you'd like to connect..."
            style={{ width: '100%', minHeight: 100, padding: '0.75rem', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(139,92,246,0.22)', borderRadius: 8, color: 'var(--text-primary)', fontSize: '0.9rem', resize: 'vertical' }}
          />
          <button onClick={handleConnect} style={{ marginTop: '1rem', width: '100%', padding: '0.75rem', background: 'linear-gradient(135deg, #7c3aed, #a855f7)', border: 'none', borderRadius: 8, color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
            Send Connection Request
          </button>
        </Modal>
      )}

      {showQuoteModal && (
        <Modal title="Request Quote" onClose={() => setShowQuoteModal(false)}>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: 6, color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Select Material</label>
            <select
              value={selectedMaterial?.id || ''}
              onChange={(e) => setSelectedMaterial(supplier.materials?.find(m => m.id === parseInt(e.target.value)))}
              style={{ width: '100%', padding: '0.6rem', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(139,92,246,0.22)', borderRadius: 8, color: 'var(--text-primary)', fontSize: '0.9rem' }}
            >
              <option value="">Select a material</option>
              {supplier.materials?.map(m => (
                <option key={m.id} value={m.id}>{m.name} - ₹{m.price_per_unit}/{m.unit}</option>
              ))}
            </select>
          </div>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: 6, color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Quantity ({selectedMaterial?.unit || 'units'})</label>
            <input
              type="number"
              value={quoteQuantity}
              onChange={(e) => setQuoteQuantity(parseInt(e.target.value) || 0)}
              style={{ width: '100%', padding: '0.6rem', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(139,92,246,0.22)', borderRadius: 8, color: 'var(--text-primary)', fontSize: '0.9rem' }}
            />
          </div>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: 6, color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Additional Details</label>
            <textarea
              value={quoteDescription}
              onChange={(e) => setQuoteDescription(e.target.value)}
              placeholder="Any specific requirements, delivery timeline, etc."
              style={{ width: '100%', minHeight: 80, padding: '0.6rem', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(139,92,246,0.22)', borderRadius: 8, color: 'var(--text-primary)', fontSize: '0.9rem', resize: 'vertical' }}
            />
          </div>
          <button onClick={handleRequestQuote} style={{ width: '100%', padding: '0.75rem', background: 'linear-gradient(135deg, #7c3aed, #a855f7)', border: 'none', borderRadius: 8, color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
            Request Quote
          </button>
        </Modal>
      )}

      {showReviewModal && (
        <Modal title="Write a Review" onClose={() => setShowReviewModal(false)}>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: 6, color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Overall Rating</label>
            <div style={{ display: 'flex', gap: 4 }}>{renderStars(reviewData.rating, true, (r) => setReviewData({ ...reviewData, rating: r }))}</div>
          </div>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: 6, color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Title</label>
            <input
              type="text"
              value={reviewData.title}
              onChange={(e) => setReviewData({ ...reviewData, title: e.target.value })}
              placeholder="Summary of your experience"
              style={{ width: '100%', padding: '0.6rem', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(139,92,246,0.22)', borderRadius: 8, color: 'var(--text-primary)', fontSize: '0.9rem' }}
            />
          </div>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: 6, color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Your Review</label>
            <textarea
              value={reviewData.content}
              onChange={(e) => setReviewData({ ...reviewData, content: e.target.value })}
              placeholder="Share your experience with this supplier..."
              style={{ width: '100%', minHeight: 100, padding: '0.6rem', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(139,92,246,0.22)', borderRadius: 8, color: 'var(--text-primary)', fontSize: '0.9rem', resize: 'vertical' }}
            />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem', marginBottom: '1rem' }}>
            {[
              { key: 'quality_rating', label: 'Quality' },
              { key: 'delivery_rating', label: 'Delivery' },
              { key: 'communication_rating', label: 'Communication' },
              { key: 'value_rating', label: 'Value' }
            ].map(item => (
              <div key={item.key}>
                <label style={{ display: 'block', marginBottom: 4, color: 'var(--text-muted)', fontSize: '0.75rem' }}>{item.label}</label>
                <div style={{ display: 'flex', gap: 2 }}>
                  {renderStars(reviewData[item.key], true, (r) => setReviewData({ ...reviewData, [item.key]: r }))}
                </div>
              </div>
            ))}
          </div>
          <button onClick={handleSubmitReview} style={{ width: '100%', padding: '0.75rem', background: 'linear-gradient(135deg, #7c3aed, #a855f7)', border: 'none', borderRadius: 8, color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
            Submit Review
          </button>
        </Modal>
      )}
    </div>
  );
};

const Modal = ({ title, children, onClose }) => (
  <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, padding: '1rem' }}>
    <div style={{ ...glass, padding: '1.5rem', maxWidth: 480, width: '100%', maxHeight: '90vh', overflow: 'auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h3 style={{ fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>{title}</h3>
        <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}><X size={20} /></button>
      </div>
      {children}
    </div>
  </div>
);

export default SupplierProfile;
