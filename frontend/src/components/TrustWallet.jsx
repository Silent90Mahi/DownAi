import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { trustAPI } from '../services/api';
import { Coins, ArrowUpLeft, Gift, TrendingUp } from 'lucide-react';

const glass = {
  background: 'rgba(255,255,255,0.04)',
  border: '1px solid rgba(139,92,246,0.2)',
  borderRadius: '1.25rem',
  backdropFilter: 'blur(16px)',
  WebkitBackdropFilter: 'blur(16px)',
};

const TrustWallet = () => {
  const { user } = useAuth();
  const [wallet, setWallet] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('balance');

  useEffect(() => {
    if (user) { fetchWallet(); fetchHistory(); }
  }, [user]);

  const fetchWallet = async () => {
    try { setLoading(true); const r = await trustAPI.getCoins(); setWallet(r.data); }
    catch { console.error('Failed to fetch wallet'); }
    finally { setLoading(false); }
  };

  const fetchHistory = async () => {
    try { const r = await trustAPI.getHistory(20); setHistory(r.data); }
    catch { console.error('Failed to fetch history'); }
  };

  const handleRedeem = async (amount, rewardType) => {
    if (amount > wallet?.balance) { alert('Insufficient coins'); return; }
    try {
      await trustAPI.redeemCoins(amount, rewardType);
      alert('Coins redeemed successfully!');
      fetchWallet(); fetchHistory();
    } catch (error) { alert('Failed to redeem: ' + (error.response?.data?.detail || 'Unknown error')); }
  };

  if (loading || !wallet) return (
    <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
      <div style={{ width: 36, height: 36, borderRadius: '50%', border: '3px solid rgba(139,92,246,0.2)', borderTopColor: '#8b5cf6', margin: '0 auto 12px', animation: 'spin 0.7s linear infinite' }} />
      Loading wallet...
    </div>
  );

  const earningWays = [
    { icon: '✅', coins: 10, description: 'Complete an order' },
    { icon: '🚚', coins: 5,  description: 'On-time delivery' },
    { icon: '⭐', coins: 5,  description: 'Receive positive review' },
    { icon: '🎓', coins: 20, description: 'Complete training' },
    { icon: '✅', coins: 15, description: 'Pass audit' },
    { icon: '🤝', coins: 25, description: 'Refer SHG' },
  ];

  const rewards = [
    { icon: '🏷️', name: 'Premium Listing', cost: 50,  description: 'Featured placement for 7 days' },
    { icon: '📣', name: 'Promotion',       cost: 100, description: 'Community promotion' },
    { icon: '🎓', name: 'Training Course', cost: 75,  description: 'Advanced skill training' },
    { icon: '📊', name: 'Market Report',   cost: 40,  description: 'Detailed market analysis' },
  ];

  const TABS = ['balance', 'earn', 'redeem'];

  return (
    <div className="animate-fade-in" style={{ padding: '1.5rem', maxWidth: 900, margin: '0 auto', paddingBottom: '6rem' }}>
      <div style={{ marginBottom: '1.75rem' }}>
        <h1 style={{
          fontSize: '1.75rem', fontWeight: 900, margin: '0 0 4px',
          background: 'linear-gradient(135deg, #f8fafc 0%, #c4b5fd 100%)',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
        }}>Trust Coin Wallet</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', margin: 0 }}>Agent Vishwas — Earn, Spend, Grow</p>
      </div>

      {/* Balance Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginBottom: '1.75rem' }}>
        {[
          { label: 'Balance',      value: wallet.balance,       icon: Coins,        color: '#8b5cf6', bg: 'linear-gradient(135deg, rgba(124,58,237,0.3), rgba(168,85,247,0.2))' },
          { label: 'Total Earned', value: wallet.total_earned,  icon: TrendingUp,   color: '#10b981', bg: 'rgba(16,185,129,0.08)' },
          { label: 'Total Spent',  value: wallet.total_spent,   icon: ArrowUpLeft,  color: '#f59e0b', bg: 'rgba(245,158,11,0.08)' },
          { label: 'Available',    value: wallet.balance,       icon: Gift,         color: '#a855f7', bg: 'rgba(168,85,247,0.08)' },
        ].map(({ label, value, icon: Icon, color, bg }) => (
          <div key={label} style={{ ...glass, padding: '1.25rem', background: bg, boxShadow: `0 4px 14px rgba(0,0,0,0.3), 0 0 12px ${color}15` }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 8 }}>
              <Icon size={17} style={{ color }} />
              <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>{label}</span>
            </div>
            <p style={{ fontSize: '2rem', fontWeight: 900, color, margin: 0 }}>{value}</p>
          </div>
        ))}
      </div>

      {/* Tabs Panel */}
      <div style={{ ...glass, overflow: 'hidden' }}>
        {/* Tab Bar */}
        <div style={{ display: 'flex', borderBottom: '1px solid rgba(139,92,246,0.15)' }}>
          {TABS.map(tab => (
            <button key={tab} onClick={() => setActiveTab(tab)} style={{
              flex: 1, padding: '1rem',
              fontSize: '0.875rem', fontWeight: 600,
              cursor: 'pointer', border: 'none',
              background: 'transparent',
              color: activeTab === tab ? '#c4b5fd' : 'var(--text-muted)',
              borderBottom: activeTab === tab ? '2px solid #8b5cf6' : '2px solid transparent',
              textTransform: 'capitalize', transition: 'all 0.2s',
            }}>
              {tab === 'balance' ? 'Balance' : tab === 'earn' ? 'How to Earn' : 'Redeem'}
            </button>
          ))}
        </div>

        <div style={{ padding: '1.5rem' }}>
          {activeTab === 'balance' && (
            <>
              <h3 style={{ fontWeight: 700, color: 'var(--text-primary)', marginBottom: '1rem', fontSize: '1rem' }}>Transaction History</h3>
              {history.length === 0 ? (
                <p style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2rem 0' }}>No transactions yet</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxHeight: 320, overflowY: 'auto' }}>
                  {history.map((txn) => (
                    <div key={txn.id} style={{
                      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                      padding: '0.75rem', background: 'rgba(255,255,255,0.03)',
                      border: '1px solid rgba(255,255,255,0.05)', borderRadius: 10,
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <span style={{
                          width: 38, height: 38, borderRadius: '50%',
                          background: txn.amount > 0 ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)',
                          border: `1px solid ${txn.amount > 0 ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)'}`,
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                          color: txn.amount > 0 ? '#6ee7b7' : '#fca5a5',
                          fontWeight: 700, fontSize: '0.78rem',
                        }}>
                          {txn.amount > 0 ? `+${txn.amount}` : txn.amount}
                        </span>
                        <div>
                          <p style={{ fontWeight: 600, color: 'var(--text-primary)', margin: '0 0 2px', fontSize: '0.875rem' }}>{txn.source}</p>
                          <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', margin: 0 }}>{new Date(txn.created_at).toLocaleDateString()}</p>
                        </div>
                      </div>
                      <p style={{ fontWeight: 700, color: txn.amount > 0 ? '#6ee7b7' : '#fca5a5', margin: 0 }}>
                        {txn.amount > 0 ? '+' : ''}{txn.balance_after}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}

          {activeTab === 'earn' && (
            <>
              <h3 style={{ fontWeight: 700, color: 'var(--text-primary)', marginBottom: '1rem', fontSize: '1rem' }}>Ways to Earn Trust Coins</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
                {earningWays.map((way, idx) => (
                  <div key={idx} style={{
                    padding: '1rem',
                    background: 'rgba(16,185,129,0.07)',
                    border: '1px solid rgba(16,185,129,0.18)',
                    borderRadius: 12,
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <span style={{ fontSize: '1.5rem' }}>{way.icon}</span>
                      <div>
                        <p style={{ fontWeight: 800, color: '#6ee7b7', margin: '0 0 2px', fontSize: '0.9rem' }}>{way.coins} Coins</p>
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', margin: 0 }}>{way.description}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}

          {activeTab === 'redeem' && (
            <>
              <h3 style={{ fontWeight: 700, color: 'var(--text-primary)', marginBottom: '1rem', fontSize: '1rem' }}>Redeem Coins for Rewards</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
                {rewards.map((reward, idx) => (
                  <div key={idx} style={{
                    padding: '1rem',
                    background: 'rgba(255,255,255,0.03)',
                    border: '1px solid rgba(139,92,246,0.18)',
                    borderRadius: 12,
                    display: 'flex', flexDirection: 'column', gap: 10,
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <span style={{ fontSize: '1.5rem' }}>{reward.icon}</span>
                      <div>
                        <p style={{ fontWeight: 700, color: 'var(--text-primary)', margin: '0 0 2px', fontSize: '0.9rem' }}>{reward.name}</p>
                        <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0 }}>{reward.description}</p>
                      </div>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <p style={{ fontWeight: 900, color: '#c4b5fd', margin: 0 }}>{reward.cost} Coins</p>
                      <button
                        onClick={() => handleRedeem(reward.cost, reward.name)}
                        disabled={wallet.balance < reward.cost}
                        style={{
                          padding: '5px 14px', borderRadius: 8, border: 'none',
                          background: wallet.balance >= reward.cost
                            ? 'linear-gradient(135deg, #7c3aed, #a855f7)'
                            : 'rgba(255,255,255,0.05)',
                          color: wallet.balance >= reward.cost ? '#fff' : 'var(--text-muted)',
                          fontWeight: 700, fontSize: '0.8rem', cursor: wallet.balance >= reward.cost ? 'pointer' : 'not-allowed',
                          boxShadow: wallet.balance >= reward.cost ? '0 3px 10px rgba(139,92,246,0.35)' : 'none',
                        }}
                      >
                        Redeem
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default TrustWallet;
