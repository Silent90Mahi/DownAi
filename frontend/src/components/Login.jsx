import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { authAPI } from '../services/api';
import { Zap, Loader2, User, Phone, ShieldCheck } from 'lucide-react';

const Login = () => {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [isRegister, setIsRegister] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [phone, setPhone] = useState('');
  const [name, setName] = useState('');
  const [otp, setOtp] = useState('');
  const [otpSent, setOtpSent] = useState(false);

  useEffect(() => {
    if (isAuthenticated) navigate('/');
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (isRegister && !otpSent) {
        await authAPI.registerAndSendOTP({ phone, name, role: 'SHG', district: 'Hyderabad' });
        setOtpSent(true);
      } else if (isRegister && otpSent) {
        await authAPI.verifyOTP(phone, otp);
        await login(phone, '123456');
      } else {
        await login(phone, '123456');
      }
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1.5rem',
      position: 'relative',
      overflow: 'hidden',
      background: 'var(--bg-primary)',
    }}>
      {/* Background glow blobs */}
      <div style={{
        position: 'absolute', top: '-15%', left: '20%',
        width: 500, height: 500, borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(139,92,246,0.15) 0%, transparent 70%)',
        pointerEvents: 'none',
      }} />
      <div style={{
        position: 'absolute', bottom: '-10%', right: '10%',
        width: 400, height: 400, borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(217,70,239,0.12) 0%, transparent 70%)',
        pointerEvents: 'none',
      }} />

      {/* Card */}
      <div className="animate-scale-in" style={{
        width: '100%',
        maxWidth: 440,
        background: 'rgba(255,255,255,0.05)',
        border: '1px solid rgba(139,92,246,0.25)',
        borderRadius: '1.5rem',
        backdropFilter: 'blur(24px)',
        WebkitBackdropFilter: 'blur(24px)',
        padding: '2.5rem',
        boxShadow: '0 25px 60px rgba(0,0,0,0.6), 0 0 40px rgba(139,92,246,0.1), inset 0 1px 0 rgba(255,255,255,0.08)',
        position: 'relative',
        zIndex: 1,
      }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{
            width: 72, height: 72,
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #7c3aed 0%, #a855f7 100%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 1.25rem',
            boxShadow: '0 0 30px rgba(139,92,246,0.5)',
          }}>
            <Zap size={34} color="#fff" fill="#fff" />
          </div>
          <h2 style={{
            fontSize: '1.75rem',
            fontWeight: 800,
            background: 'linear-gradient(135deg, #c4b5fd 0%, #a78bfa 50%, #e879f9 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            marginBottom: '0.5rem',
          }}>
            {isRegister ? 'Join Ooumph' : 'Welcome Back'}
          </h2>
          <p style={{ color: 'var(--text-tertiary)', fontSize: '0.9rem', margin: 0 }}>
            {isRegister ? 'Create your SHG account' : 'The Last Human Network for SHGs'}
          </p>
        </div>

        {/* Toggle */}
        <div style={{
          display: 'flex',
          background: 'rgba(0,0,0,0.3)',
          border: '1px solid rgba(139,92,246,0.2)',
          borderRadius: 99,
          padding: 4,
          marginBottom: '1.75rem',
        }}>
          {['Login', 'Register'].map((tab) => {
            const active = (tab === 'Register') === isRegister;
            return (
              <button
                key={tab}
                onClick={() => { setIsRegister(tab === 'Register'); setOtpSent(false); setError(''); }}
                style={{
                  flex: 1, padding: '0.5rem',
                  borderRadius: 99,
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '0.875rem',
                  fontWeight: 600,
                  transition: 'all 0.25s',
                  background: active
                    ? 'linear-gradient(135deg, #7c3aed, #a855f7)'
                    : 'transparent',
                  color: active ? '#fff' : 'var(--text-muted)',
                  boxShadow: active ? '0 0 14px rgba(139,92,246,0.4)' : 'none',
                }}
              >
                {tab}
              </button>
            );
          })}
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.1rem' }}>
          {error && (
            <div style={{
              background: 'rgba(239,68,68,0.12)',
              border: '1px solid rgba(239,68,68,0.3)',
              color: '#fca5a5',
              padding: '0.75rem 1rem',
              borderRadius: 10,
              fontSize: '0.85rem',
              fontWeight: 500,
            }}>
              {error}
            </div>
          )}

          {isRegister && !otpSent && (
            <div>
              <label style={{
                display: 'flex', alignItems: 'center', gap: 6,
                fontSize: '0.8rem', fontWeight: 600,
                color: 'var(--text-secondary)', marginBottom: '0.5rem',
              }}>
                <User size={14} style={{ color: 'var(--accent-primary)' }} />
                Your Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                style={{
                  width: '100%', padding: '0.75rem 1rem',
                  background: 'rgba(255,255,255,0.06)',
                  border: '1px solid rgba(139,92,246,0.2)',
                  borderRadius: 10,
                  color: 'var(--text-primary)',
                  fontSize: '0.95rem',
                  outline: 'none',
                  transition: 'all 0.2s',
                }}
                placeholder="e.g. Lakshmi Devi"
                required
                onFocus={e => {
                  e.target.style.borderColor = '#8b5cf6';
                  e.target.style.boxShadow = '0 0 0 3px rgba(139,92,246,0.15)';
                }}
                onBlur={e => {
                  e.target.style.borderColor = 'rgba(139,92,246,0.2)';
                  e.target.style.boxShadow = 'none';
                }}
              />
            </div>
          )}

          <div>
            <label style={{
              display: 'flex', alignItems: 'center', gap: 6,
              fontSize: '0.8rem', fontWeight: 600,
              color: 'var(--text-secondary)', marginBottom: '0.5rem',
            }}>
              <Phone size={14} style={{ color: 'var(--accent-primary)' }} />
              Mobile Number
            </label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              style={{
                width: '100%', padding: '0.75rem 1rem',
                background: 'rgba(255,255,255,0.06)',
                border: '1px solid rgba(139,92,246,0.2)',
                borderRadius: 10,
                color: 'var(--text-primary)',
                fontSize: '0.95rem',
                outline: 'none',
                transition: 'all 0.2s',
                opacity: otpSent ? 0.6 : 1,
              }}
              placeholder="9876543210"
              pattern="[0-9]{10}"
              required
              disabled={otpSent}
              onFocus={e => {
                e.target.style.borderColor = '#8b5cf6';
                e.target.style.boxShadow = '0 0 0 3px rgba(139,92,246,0.15)';
              }}
              onBlur={e => {
                e.target.style.borderColor = 'rgba(139,92,246,0.2)';
                e.target.style.boxShadow = 'none';
              }}
            />
          </div>

          {isRegister && otpSent && (
            <div>
              <label style={{
                display: 'block',
                fontSize: '0.8rem', fontWeight: 600,
                color: 'var(--text-secondary)', marginBottom: '0.5rem',
              }}>
                <ShieldCheck size={14} style={{ color: 'var(--accent-primary)', marginRight: 6 }} />
                OTP (6 digits)
              </label>
              <input
                type="text"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                style={{
                  width: '100%', padding: '0.75rem 1rem',
                  background: 'rgba(255,255,255,0.06)',
                  border: '1px solid rgba(139,92,246,0.2)',
                  borderRadius: 10,
                  color: 'var(--text-primary)',
                  fontSize: '1.5rem',
                  letterSpacing: '0.3em',
                  textAlign: 'center',
                  outline: 'none',
                  transition: 'all 0.2s',
                }}
                placeholder="••••••"
                pattern="[0-9]{6}"
                required
                onFocus={e => {
                  e.target.style.borderColor = '#8b5cf6';
                  e.target.style.boxShadow = '0 0 0 3px rgba(139,92,246,0.15)';
                }}
                onBlur={e => {
                  e.target.style.borderColor = 'rgba(139,92,246,0.2)';
                  e.target.style.boxShadow = 'none';
                }}
              />
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textAlign: 'center', marginTop: 6 }}>
                Mock OTP: 123456
              </p>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '0.9rem',
              marginTop: '0.5rem',
              background: 'linear-gradient(135deg, #7c3aed 0%, #a855f7 100%)',
              border: 'none',
              borderRadius: 10,
              color: '#fff',
              fontSize: '1rem',
              fontWeight: 700,
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1,
              boxShadow: '0 4px 20px rgba(139,92,246,0.4)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
              transition: 'all 0.25s',
            }}
            onMouseEnter={e => !loading && (e.currentTarget.style.boxShadow = '0 6px 28px rgba(139,92,246,0.6)')}
            onMouseLeave={e => (e.currentTarget.style.boxShadow = '0 4px 20px rgba(139,92,246,0.4)')}
          >
            {loading ? (
              <>
                <Loader2 size={18} style={{ animation: 'spin 0.7s linear infinite' }} />
                Processing...
              </>
            ) : (
              isRegister ? (otpSent ? 'Complete Registration' : 'Send OTP') : 'Login via OTP'
            )}
          </button>
        </form>

        {/* Toggle Link */}
        <div style={{ marginTop: '1.75rem', textAlign: 'center', borderTop: '1px solid rgba(139,92,246,0.12)', paddingTop: '1.5rem' }}>
          <button
            onClick={() => { setIsRegister(!isRegister); setOtpSent(false); setError(''); }}
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              fontSize: '0.875rem', fontWeight: 600,
              color: 'var(--text-link)', transition: 'color 0.2s',
            }}
            onMouseEnter={e => (e.currentTarget.style.color = 'var(--text-link-hover)')}
            onMouseLeave={e => (e.currentTarget.style.color = 'var(--text-link)')}
          >
            {isRegister ? 'Already have an account? Login' : "Don't have an account? Register"}
          </button>
        </div>

        <p style={{ textAlign: 'center', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '1.25rem' }}>
          🌐 Available in English, Telugu, Hindi, Urdu
        </p>
      </div>
    </div>
  );
};

export default Login;
