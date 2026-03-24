import { useState, useEffect } from 'react';
import { Package, LineChart, ShieldCheck, Coins, ArrowRight, List, TrendingUp, Star } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { analyticsAPI, trustAPI } from '../services/api';

const StatCard = ({ label, value, icon: Icon, color, delay }) => (
  <div
    className={`animate-fade-in delay-${delay}`}
    style={{
      background: 'rgba(255,255,255,0.04)',
      border: '1px solid rgba(139,92,246,0.2)',
      borderRadius: '1.25rem',
      padding: '1.5rem',
      backdropFilter: 'blur(16px)',
      WebkitBackdropFilter: 'blur(16px)',
      display: 'flex',
      flexDirection: 'column',
      gap: '1rem',
      transition: 'all 0.3s',
      cursor: 'default',
      boxShadow: '0 4px 20px rgba(0,0,0,0.4)',
    }}
    onMouseEnter={e => {
      e.currentTarget.style.border = '1px solid rgba(139,92,246,0.45)';
      e.currentTarget.style.boxShadow = `0 8px 30px rgba(0,0,0,0.5), 0 0 20px ${color}25`;
      e.currentTarget.style.transform = 'translateY(-3px)';
    }}
    onMouseLeave={e => {
      e.currentTarget.style.border = '1px solid rgba(139,92,246,0.2)';
      e.currentTarget.style.boxShadow = '0 4px 20px rgba(0,0,0,0.4)';
      e.currentTarget.style.transform = 'translateY(0)';
    }}
  >
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
        {label}
      </span>
      <div style={{
        width: 40, height: 40,
        borderRadius: 10,
        background: `${color}20`,
        border: `1px solid ${color}35`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        <Icon size={20} style={{ color }} />
      </div>
    </div>
    <p style={{ fontSize: '2.25rem', fontWeight: 900, color: 'var(--text-primary)', margin: 0, lineHeight: 1 }}>
      {value}
    </p>
  </div>
);

const ActionCard = ({ title, subtitle, onClick, accentColor, delay, icon: Icon }) => (
  <div
    className={`animate-fade-in delay-${delay}`}
    onClick={onClick}
    style={{
      background: 'rgba(255,255,255,0.04)',
      border: '1px solid rgba(139,92,246,0.18)',
      borderRadius: '1.25rem',
      padding: '1.75rem',
      backdropFilter: 'blur(16px)',
      WebkitBackdropFilter: 'blur(16px)',
      cursor: 'pointer',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      transition: 'all 0.3s',
      boxShadow: '0 4px 15px rgba(0,0,0,0.3)',
    }}
    onMouseEnter={e => {
      e.currentTarget.style.border = `1px solid ${accentColor}50`;
      e.currentTarget.style.boxShadow = `0 12px 30px rgba(0,0,0,0.5), 0 0 25px ${accentColor}20`;
      e.currentTarget.style.transform = 'translateY(-4px)';
    }}
    onMouseLeave={e => {
      e.currentTarget.style.border = '1px solid rgba(139,92,246,0.18)';
      e.currentTarget.style.boxShadow = '0 4px 15px rgba(0,0,0,0.3)';
      e.currentTarget.style.transform = 'translateY(0)';
    }}
  >
    <div>
      <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '0.4rem' }}>
        {title}
      </h3>
      <p style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)', margin: 0 }}>
        {subtitle}
      </p>
    </div>
    <div style={{
      width: 48, height: 48,
      borderRadius: '50%',
      background: `${accentColor}18`,
      border: `1px solid ${accentColor}35`,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      transition: 'all 0.3s',
      flexShrink: 0,
    }}>
      <Icon size={22} style={{ color: accentColor }} />
    </div>
  </div>
);

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => { fetchDashboardStats(); }, [user]);

  const fetchDashboardStats = async () => {
    try {
      setLoading(true);
      const [analyticsResp, profileResp] = await Promise.all([
        user?.id ? analyticsAPI.getUserAnalytics(user.id).catch(() => ({ data: null })) : Promise.resolve({ data: null }),
        trustAPI.getProfile().catch(() => ({ data: null }))
      ]);
      const analytics = analyticsResp.data;
      const profile = profileResp.data;
      setStats({
        trustScore:    profile?.trust_score || 50,
        trustCoins:   profile?.trust_coins || 0,
        activeListings: analytics?.active_listings || 0,
        revenue:       analytics?.total_revenue ? `₹${analytics.total_revenue.toLocaleString()}` : '₹0',
        rank:          profile?.trust_badge || 'Bronze',
        totalOrders:   analytics?.total_orders || 0,
        completionRate: analytics?.completion_rate || 0,
      });
    } catch {
      setStats({ trustScore: 50, trustCoins: 0, activeListings: 0, revenue: '₹0', rank: 'Bronze', totalOrders: 0, completionRate: 0 });
    } finally {
      setLoading(false);
    }
  };

  if (loading || !stats) return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <div style={{ color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.9rem', letterSpacing: '0.05em' }}>
        <div style={{
          width: 40, height: 40, borderRadius: '50%',
          border: '3px solid rgba(139,92,246,0.2)',
          borderTopColor: '#8b5cf6',
          margin: '0 auto 12px',
          animation: 'spin 0.7s linear infinite',
        }} />
        Loading Network...
      </div>
    </div>
  );

  const rankBadgeStyle = {
    Gold:   { bg: 'rgba(255,215,0,0.15)',   border: 'rgba(255,215,0,0.4)',   color: '#fcd34d', glow: 'rgba(255,215,0,0.2)' },
    Silver: { bg: 'rgba(192,192,192,0.12)', border: 'rgba(192,192,192,0.3)', color: '#cbd5e1', glow: 'rgba(192,192,192,0.15)' },
    Bronze: { bg: 'rgba(205,127,50,0.15)',  border: 'rgba(205,127,50,0.35)', color: '#fbbf24', glow: 'rgba(205,127,50,0.2)' },
  }[stats.rank] || { bg: 'rgba(139,92,246,0.15)', border: 'rgba(139,92,246,0.35)', color: '#c4b5fd', glow: 'rgba(139,92,246,0.2)' };

  return (
    <div style={{ padding: '1.5rem', maxWidth: 1200, margin: '0 auto' }}>
      {/* Hero */}
      <div
        className="animate-fade-in"
        style={{
          background: 'rgba(255,255,255,0.04)',
          border: '1px solid rgba(139,92,246,0.22)',
          borderRadius: '1.5rem',
          padding: '2rem 2.25rem',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1.5rem',
          marginBottom: '1.75rem',
          position: 'relative',
          overflow: 'hidden',
          boxShadow: '0 4px 30px rgba(0,0,0,0.4)',
        }}
      >
        {/* Decorative orb */}
        <div style={{
          position: 'absolute', top: '-60px', right: '-40px',
          width: 200, height: 200, borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(139,92,246,0.2) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />

        <div>
          <h1 style={{
            fontSize: '2.25rem', fontWeight: 900, margin: 0,
            background: 'linear-gradient(135deg, #f8fafc 0%, #c4b5fd 100%)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
            letterSpacing: '-0.02em',
          }}>
            Your Network Hub
          </h1>
          <p style={{ color: 'var(--text-tertiary)', fontWeight: 500, margin: '0.5rem 0 0', fontSize: '1rem' }}>
            Manage your products, trust, and community standing.
          </p>
        </div>

        {/* Trust Badge */}
        <div style={{
          background: rankBadgeStyle.bg,
          border: `1px solid ${rankBadgeStyle.border}`,
          borderRadius: '1rem',
          padding: '0.9rem 1.5rem',
          display: 'flex', alignItems: 'center', gap: '0.75rem',
          boxShadow: `0 0 20px ${rankBadgeStyle.glow}`,
        }}>
          <ShieldCheck size={28} style={{ color: rankBadgeStyle.color }} />
          <div>
            <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', color: rankBadgeStyle.color, opacity: 0.8 }}>Trust Level</div>
            <div style={{ fontWeight: 900, fontSize: '1.3rem', color: rankBadgeStyle.color }}>{stats.rank}</div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '1.75rem' }}>
        <StatCard label="Trust Score"      value={`${stats.trustScore}/100`}   icon={LineChart}    color="#8b5cf6" delay={100} />
        <StatCard label="Trust Coins"      value={stats.trustCoins}             icon={Coins}        color="#f59e0b" delay={200} />
        <StatCard label="Active Listings"  value={stats.activeListings}         icon={Package}      color="#10b981" delay={300} />
        <StatCard label="Total Revenue"    value={stats.revenue}                icon={TrendingUp}   color="#a855f7" delay={100} />
      </div>

      {/* Action Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem' }}>
        <ActionCard title="My Products"       subtitle="Manage your listings"                icon={List}       onClick={() => navigate('/my-products')}   accentColor="#10b981" delay={100} />
        <ActionCard title="Buy Raw Materials" subtitle="Go to Samagri Marketplace"           icon={ArrowRight}  onClick={() => navigate('/marketplace')}    accentColor="#f59e0b" delay={200} />
        <ActionCard title="Sell Products"     subtitle="List to ONDC & GeM via Agent Jodi"  icon={Star}       onClick={() => navigate('/sell')}           accentColor="#8b5cf6" delay={300} />
      </div>
    </div>
  );
};

export default Dashboard;
