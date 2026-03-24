import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { User, Mail, MapPin, Phone, Save, ShieldCheck, LogOut, Edit2, X } from 'lucide-react';

const inputStyle = (editing) => ({
  width: '100%', padding: '0.65rem 0.9rem',
  background: editing ? 'rgba(255,255,255,0.08)' : 'rgba(255,255,255,0.03)',
  border: editing ? '1px solid rgba(139,92,246,0.35)' : '1px solid rgba(255,255,255,0.06)',
  borderRadius: 10, outline: 'none',
  color: editing ? 'var(--text-primary)' : 'var(--text-secondary)',
  fontSize: '0.9rem',
  transition: 'all 0.2s',
});

const Profile = () => {
  const { user, updateUser, logout } = useAuth();
  const navigate = useNavigate();
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    name: '', email: '', district: '', address: '', pincode: '', language_preference: 'English',
  });

  useEffect(() => {
    if (user) {
      setFormData({
        name: user.name || '', email: user.email || '',
        district: user.district || '', address: user.address || '',
        pincode: user.pincode || '', language_preference: user.language_preference || 'English',
      });
    }
  }, [user]);

  const handleSave = async () => {
    try {
      setSaving(true);
      await updateUser(formData);
      setEditing(false);
    } catch (error) {
      alert('Failed to update profile: ' + (error.response?.data?.detail || 'Unknown error'));
    } finally { setSaving(false); }
  };

  if (!user) return null;

  const rankColors = {
    Gold:   { bg: 'rgba(255,215,0,0.12)',   border: 'rgba(255,215,0,0.3)',   text: '#fcd34d', icon: '#fbbf24' },
    Silver: { bg: 'rgba(192,192,192,0.1)',   border: 'rgba(192,192,192,0.25)',text: '#cbd5e1', icon: '#94a3b8' },
    Bronze: { bg: 'rgba(205,127,50,0.12)',   border: 'rgba(205,127,50,0.3)', text: '#fbbf24', icon: '#f97316' },
  }[user.trust_badge] || { bg: 'rgba(139,92,246,0.1)', border: 'rgba(139,92,246,0.25)', text: '#c4b5fd', icon: '#a78bfa' };

  return (
    <div className="animate-fade-in" style={{ padding: '1.5rem', maxWidth: 900, margin: '0 auto', paddingBottom: '6rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.75rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{
            fontSize: '1.75rem', fontWeight: 900, margin: '0 0 4px',
            background: 'linear-gradient(135deg, #f8fafc 0%, #c4b5fd 100%)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
          }}>My Profile</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', margin: 0 }}>Manage your account settings</p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button
            onClick={() => setEditing(true)}
            style={{
              display: 'flex', alignItems: 'center', gap: 6,
              padding: '0.55rem 1.1rem',
              background: 'rgba(139,92,246,0.15)',
              border: '1px solid rgba(139,92,246,0.35)',
              borderRadius: 10, cursor: 'pointer',
              color: '#c4b5fd', fontSize: '0.85rem', fontWeight: 600,
              transition: 'all 0.2s',
            }}
          >
            <Edit2 size={15} /> Edit Profile
          </button>
          <button
            onClick={() => { logout(); navigate('/login'); }}
            style={{
              display: 'flex', alignItems: 'center', gap: 6,
              padding: '0.55rem 1.1rem',
              background: 'rgba(239,68,68,0.1)',
              border: '1px solid rgba(239,68,68,0.25)',
              borderRadius: 10, cursor: 'pointer',
              color: '#fca5a5', fontSize: '0.85rem', fontWeight: 600,
              transition: 'all 0.2s',
            }}
          >
            <LogOut size={15} /> Logout
          </button>
        </div>
      </div>

      {/* Profile Card */}
      <div style={{
        background: 'rgba(255,255,255,0.04)',
        border: '1px solid rgba(139,92,246,0.2)',
        borderRadius: '1.25rem',
        backdropFilter: 'blur(16px)',
        padding: '1.75rem',
        marginBottom: '1.25rem',
        boxShadow: '0 4px 20px rgba(0,0,0,0.35)',
      }}>
        {/* Avatar + Name */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', marginBottom: '1.75rem', borderBottom: '1px solid rgba(139,92,246,0.12)', paddingBottom: '1.5rem' }}>
          <div style={{
            width: 72, height: 72, borderRadius: '50%',
            background: 'linear-gradient(135deg, #7c3aed 0%, #a855f7 100%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '2rem', fontWeight: 900, color: '#fff',
            boxShadow: '0 0 20px rgba(139,92,246,0.4)',
            border: '2px solid rgba(196,181,253,0.3)',
            flexShrink: 0,
          }}>
            {user.name?.charAt(0) || 'U'}
          </div>
          <div>
            <h2 style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--text-primary)', margin: '0 0 4px' }}>{user.name}</h2>
            <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              {user.role} • {user.hierarchy_level || 'SHG'}
            </p>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={(e) => { e.preventDefault(); handleSave(); }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
            {[
              { label: 'Full Name', icon: User, key: 'name', type: 'text' },
              { label: 'Email (Optional)', icon: Mail, key: 'email', type: 'email' },
              { label: 'District', icon: MapPin, key: 'district', type: 'text' },
            ].map(({ label, icon: Icon, key, type }) => (
              <div key={key}>
                <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-tertiary)', marginBottom: 6 }}>
                  <Icon size={13} style={{ color: '#8b5cf6' }} /> {label}
                </label>
                <input
                  type={type}
                  value={formData[key]}
                  onChange={(e) => setFormData({ ...formData, [key]: e.target.value })}
                  disabled={!editing}
                  style={inputStyle(editing)}
                  onFocus={e => editing && (e.target.style.boxShadow = '0 0 0 3px rgba(139,92,246,0.15)', e.target.style.borderColor = '#8b5cf6')}
                  onBlur={e => (e.target.style.boxShadow = 'none', e.target.style.borderColor = editing ? 'rgba(139,92,246,0.35)' : 'rgba(255,255,255,0.06)')}
                />
              </div>
            ))}

            <div>
              <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-tertiary)', marginBottom: 6 }}>
                <Phone size={13} style={{ color: '#8b5cf6' }} /> Phone
              </label>
              <input type="tel" value={user.phone} disabled style={inputStyle(false)} />
            </div>

            <div style={{ gridColumn: '1 / -1' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-tertiary)', marginBottom: 6 }}>
                <MapPin size={13} style={{ color: '#8b5cf6' }} /> Address
              </label>
              <input
                type="text"
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                disabled={!editing}
                style={inputStyle(editing)}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-tertiary)', marginBottom: 6, display: 'block' }}>Language Preference</label>
              <select
                value={formData.language_preference}
                onChange={(e) => setFormData({ ...formData, language_preference: e.target.value })}
                disabled={!editing}
                style={{ ...inputStyle(editing), cursor: editing ? 'pointer' : 'default' }}
              >
                <option value="English">English</option>
                <option value="Telugu">తెలుగు</option>
                <option value="Hindi">हिंदी</option>
                <option value="Urdu">اردو</option>
              </select>
            </div>

            <div>
              <label style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-tertiary)', marginBottom: 6, display: 'block' }}>Pincode</label>
              <input
                type="text"
                value={formData.pincode}
                onChange={(e) => setFormData({ ...formData, pincode: e.target.value })}
                disabled={!editing}
                style={inputStyle(editing)}
              />
            </div>
          </div>

          {editing && (
            <div style={{ display: 'flex', gap: 10, paddingTop: '1rem', borderTop: '1px solid rgba(139,92,246,0.12)' }}>
              <button
                type="submit"
                disabled={saving}
                style={{
                  flex: 1, padding: '0.7rem',
                  background: 'linear-gradient(135deg, #7c3aed, #a855f7)',
                  border: 'none', borderRadius: 10,
                  color: '#fff', fontWeight: 700, fontSize: '0.9rem',
                  cursor: saving ? 'not-allowed' : 'pointer',
                  opacity: saving ? 0.7 : 1,
                  boxShadow: '0 4px 14px rgba(139,92,246,0.35)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
                }}
              >
                <Save size={16} />
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setEditing(false);
                  if (user) setFormData({ name: user.name || '', email: user.email || '', district: user.district || '', address: user.address || '', pincode: user.pincode || '', language_preference: user.language_preference || 'English' });
                }}
                style={{
                  padding: '0.7rem 1.25rem',
                  background: 'rgba(255,255,255,0.04)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: 10, cursor: 'pointer',
                  color: 'var(--text-secondary)', fontWeight: 600, fontSize: '0.9rem',
                  display: 'flex', alignItems: 'center', gap: 5,
                }}
              >
                <X size={15} /> Cancel
              </button>
            </div>
          )}
        </form>
      </div>

      {/* Trust Badge */}
      <div style={{
        background: rankColors.bg,
        border: `1px solid ${rankColors.border}`,
        borderRadius: '1.25rem',
        padding: '1.5rem',
        display: 'flex', alignItems: 'center', gap: '1.25rem',
        boxShadow: `0 0 20px ${rankColors.bg}`,
      }}>
        <div style={{
          width: 60, height: 60, borderRadius: '50%',
          background: `${rankColors.bg}`,
          border: `2px solid ${rankColors.border}`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <ShieldCheck size={28} style={{ color: rankColors.icon }} />
        </div>
        <div>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: rankColors.text, margin: '0 0 3px' }}>
            {user.trust_badge} Badge
          </h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>
            Trust Score: {user.trust_score}/100
          </p>
        </div>
      </div>
    </div>
  );
};

export default Profile;
