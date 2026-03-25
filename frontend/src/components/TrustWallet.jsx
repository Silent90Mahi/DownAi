import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { trustAPI, api } from '../services/api';
import { Coins, ArrowUpLeft, Gift, TrendingUp, Wallet, Link, Unlink, Send, ArrowDownRight, ArrowUpRight, Filter, RefreshCw, CheckCircle, X, Copy, ExternalLink } from 'lucide-react';

const glass = {
  background: 'rgba(255,255,255,0.04)',
  border: '1px solid rgba(139,92,246,0.2)',
  borderRadius: '1.25rem',
  backdropFilter: 'blur(16px)',
  WebkitBackdropFilter: 'blur(16px)',
};

const walletStubAPI = {
  connect: () => new Promise(resolve => setTimeout(() => resolve({ 
    data: { 
      address: '0x' + Math.random().toString(16).substr(2, 40),
      chain: 'Polygon',
      balance: (Math.random() * 0.5 + 0.1).toFixed(4),
      connected: true
    } 
  }), 1500)),
  
  getBalance: (address) => new Promise(resolve => setTimeout(() => resolve({
    data: {
      matic: (Math.random() * 0.5 + 0.1).toFixed(4),
      usdc: (Math.random() * 100 + 10).toFixed(2),
      trustCoins: Math.floor(Math.random() * 500 + 100)
    }
  }), 500)),
  
  simulatePayment: (amount, to) => new Promise(resolve => setTimeout(() => resolve({
    data: {
      success: true,
      txHash: '0x' + Math.random().toString(16).substr(2, 64),
      amount,
      timestamp: new Date().toISOString()
    }
  }), 2000)),
  
  getTransactions: (address) => new Promise(resolve => setTimeout(() => resolve({
    data: [
      { hash: '0x' + Math.random().toString(16).substr(2, 64), type: 'receive', amount: '0.05 MATIC', from: '0x1234...5678', timestamp: new Date(Date.now() - 3600000).toISOString() },
      { hash: '0x' + Math.random().toString(16).substr(2, 64), type: 'send', amount: '10 USDC', to: '0xabcd...efgh', timestamp: new Date(Date.now() - 86400000).toISOString() },
      { hash: '0x' + Math.random().toString(16).substr(2, 64), type: 'receive', amount: '50 Trust Coins', from: 'Ooumph Rewards', timestamp: new Date(Date.now() - 172800000).toISOString() },
    ]
  }), 500)),
};

const TrustWallet = () => {
  const { user } = useAuth();
  const [wallet, setWallet] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('balance');

  const [cryptoWallet, setCryptoWallet] = useState(null);
  const [cryptoBalance, setCryptoBalance] = useState(null);
  const [cryptoTxns, setCryptoTxns] = useState([]);
  const [connecting, setConnecting] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentAmount, setPaymentAmount] = useState('');
  const [paymentTo, setPaymentTo] = useState('0x742d35Cc6634C0532925a3b844Bc9e7595f2bD8e');
  const [processing, setProcessing] = useState(false);
  const [paymentSuccess, setPaymentSuccess] = useState(null);
  const [txFilter, setTxFilter] = useState('all');
  const [animatingBalance, setAnimatingBalance] = useState(false);

  useEffect(() => {
    if (user) { fetchWallet(); fetchHistory(); }
  }, [user]);

  useEffect(() => {
    if (cryptoWallet?.connected) {
      fetchCryptoBalance();
      fetchCryptoTxns();
    }
  }, [cryptoWallet]);

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
      animateBalanceChange(wallet.balance, wallet.balance - amount);
      alert('Coins redeemed successfully!');
      fetchWallet(); fetchHistory();
    } catch (error) { alert('Failed to redeem: ' + (error.response?.data?.detail || 'Unknown error')); }
  };

  const animateBalanceChange = (from, to) => {
    setAnimatingBalance(true);
    setTimeout(() => setAnimatingBalance(false), 1000);
  };

  const handleConnectWallet = async () => {
    try {
      setConnecting(true);
      const response = await walletStubAPI.connect();
      setCryptoWallet(response.data);
    } catch (error) {
      alert('Failed to connect wallet: ' + error.message);
    } finally {
      setConnecting(false);
    }
  };

  const handleDisconnectWallet = () => {
    setCryptoWallet(null);
    setCryptoBalance(null);
    setCryptoTxns([]);
  };

  const fetchCryptoBalance = async () => {
    if (!cryptoWallet?.address) return;
    try {
      const response = await walletStubAPI.getBalance(cryptoWallet.address);
      setCryptoBalance(response.data);
    } catch (error) {
      console.error('Failed to fetch crypto balance:', error);
    }
  };

  const fetchCryptoTxns = async () => {
    if (!cryptoWallet?.address) return;
    try {
      const response = await walletStubAPI.getTransactions(cryptoWallet.address);
      setCryptoTxns(response.data);
    } catch (error) {
      console.error('Failed to fetch crypto transactions:', error);
    }
  };

  const handleSimulatePayment = async () => {
    if (!paymentAmount || parseFloat(paymentAmount) <= 0) {
      alert('Please enter a valid amount');
      return;
    }
    try {
      setProcessing(true);
      setPaymentSuccess(null);
      const response = await walletStubAPI.simulatePayment(paymentAmount, paymentTo);
      setPaymentSuccess(response.data);
      fetchCryptoBalance();
      fetchCryptoTxns();
    } catch (error) {
      alert('Payment failed: ' + error.message);
    } finally {
      setProcessing(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
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

  const TABS = ['balance', 'crypto', 'earn', 'redeem'];

  const filteredHistory = history.filter(txn => {
    if (txFilter === 'all') return true;
    if (txFilter === 'earned') return txn.amount > 0;
    if (txFilter === 'spent') return txn.amount < 0;
    return true;
  });

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
          <div key={label} style={{ ...glass, padding: '1.25rem', background: bg, boxShadow: `0 4px 14px rgba(0,0,0,0.3), 0 0 12px ${color}15`, transition: 'transform 0.3s', cursor: 'pointer' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 8 }}>
              <Icon size={17} style={{ color }} />
              <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>{label}</span>
            </div>
            <p style={{ 
              fontSize: '2rem', 
              fontWeight: 900, 
              color, 
              margin: 0,
              transition: animatingBalance ? 'transform 0.3s' : 'none',
              transform: animatingBalance ? 'scale(1.1)' : 'scale(1)'
            }}>{value}</p>
          </div>
        ))}
      </div>

      {/* Crypto Wallet Connect Card */}
      <div style={{ ...glass, padding: '1.25rem', marginBottom: '1.75rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ width: 48, height: 48, borderRadius: 12, background: 'linear-gradient(135deg, #8b5cf6, #a855f7)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Wallet size={24} color="#fff" />
            </div>
            <div>
              <h3 style={{ fontWeight: 700, color: 'var(--text-primary)', margin: '0 0 4px', fontSize: '1rem' }}>Crypto Wallet</h3>
              {cryptoWallet?.connected ? (
                <div>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', margin: 0, display: 'flex', alignItems: 'center', gap: 6 }}>
                    {cryptoWallet.address.substring(0, 8)}...{cryptoWallet.address.substring(cryptoWallet.address.length - 6)}
                    <button onClick={() => copyToClipboard(cryptoWallet.address)} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}><Copy size={12} style={{ color: 'var(--text-muted)' }} /></button>
                  </p>
                  <span style={{ fontSize: '0.7rem', color: '#6ee7b7', display: 'flex', alignItems: 'center', gap: 4 }}>
                    <CheckCircle size={12} /> Connected to {cryptoWallet.chain}
                  </span>
                </div>
              ) : (
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>Connect wallet for crypto payments</p>
              )}
            </div>
          </div>
          {cryptoWallet?.connected ? (
            <div style={{ display: 'flex', gap: 8 }}>
              <button onClick={fetchCryptoBalance} style={{ padding: '0.5rem', background: 'rgba(139,92,246,0.1)', border: '1px solid rgba(139,92,246,0.3)', borderRadius: 8, color: '#c4b5fd', cursor: 'pointer' }}>
                <RefreshCw size={16} />
              </button>
              <button onClick={handleDisconnectWallet} style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '0.5rem 1rem', background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 8, color: '#fca5a5', fontWeight: 600, cursor: 'pointer' }}>
                <Unlink size={16} /> Disconnect
              </button>
            </div>
          ) : (
            <button onClick={handleConnectWallet} disabled={connecting} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '0.6rem 1.25rem', background: connecting ? 'rgba(139,92,246,0.3)' : 'linear-gradient(135deg, #7c3aed, #a855f7)', border: 'none', borderRadius: 10, color: '#fff', fontWeight: 700, cursor: connecting ? 'not-allowed' : 'pointer', boxShadow: '0 4px 14px rgba(139,92,246,0.35)' }}>
              {connecting ? (
                <>
                  <div style={{ width: 16, height: 16, borderRadius: '50%', border: '2px solid rgba(255,255,255,0.3)', borderTopColor: '#fff', animation: 'spin 0.7s linear infinite' }} />
                  Connecting...
                </>
              ) : (
                <><Link size={16} /> Connect Wallet</>
              )}
            </button>
          )}
        </div>

        {/* Crypto Balances */}
        {cryptoWallet?.connected && cryptoBalance && (
          <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.06)', display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem' }}>
            {[
              { label: 'MATIC', value: cryptoBalance.matic, color: '#8b5cf6' },
              { label: 'USDC', value: cryptoBalance.usdc, color: '#6ee7b7' },
              { label: 'Trust Coins', value: cryptoBalance.trustCoins, color: '#f59e0b' },
            ].map(({ label, value, color }) => (
              <div key={label} style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(139,92,246,0.15)', borderRadius: 10, padding: '0.75rem', textAlign: 'center' }}>
                <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', margin: '0 0 4px' }}>{label}</p>
                <p style={{ fontWeight: 800, color, margin: 0, fontSize: '1.1rem' }}>{value}</p>
              </div>
            ))}
          </div>
        )}
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
              {tab === 'balance' ? 'Transactions' : tab === 'crypto' ? 'Crypto' : tab === 'earn' ? 'How to Earn' : 'Redeem'}
            </button>
          ))}
        </div>

        <div style={{ padding: '1.5rem' }}>
          {activeTab === 'balance' && (
            <>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 style={{ fontWeight: 700, color: 'var(--text-primary)', margin: 0, fontSize: '1rem' }}>Transaction History</h3>
                <div style={{ display: 'flex', gap: 8 }}>
                  <select value={txFilter} onChange={(e) => setTxFilter(e.target.value)} style={{ padding: '0.4rem 0.6rem', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 8, color: 'var(--text-primary)', fontSize: '0.8rem' }}>
                    <option value="all">All</option>
                    <option value="earned">Earned</option>
                    <option value="spent">Spent</option>
                  </select>
                </div>
              </div>
              {filteredHistory.length === 0 ? (
                <p style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2rem 0' }}>No transactions yet</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxHeight: 320, overflowY: 'auto' }}>
                  {filteredHistory.map((txn) => (
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

          {activeTab === 'crypto' && (
            <>
              {cryptoWallet?.connected ? (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <h3 style={{ fontWeight: 700, color: 'var(--text-primary)', margin: 0, fontSize: '1rem' }}>Crypto Transactions</h3>
                    <button onClick={() => setShowPaymentModal(true)} style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '0.5rem 1rem', background: 'linear-gradient(135deg, #7c3aed, #a855f7)', border: 'none', borderRadius: 8, color: '#fff', fontWeight: 600, cursor: 'pointer' }}>
                      <Send size={14} /> Send Payment
                    </button>
                  </div>
                  
                  {cryptoTxns.length === 0 ? (
                    <p style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2rem 0' }}>No crypto transactions yet</p>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                      {cryptoTxns.map((txn, idx) => (
                        <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: 10 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                            <div style={{ width: 36, height: 36, borderRadius: '50%', background: txn.type === 'receive' ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                              {txn.type === 'receive' ? <ArrowDownRight size={16} color="#6ee7b7" /> : <ArrowUpRight size={16} color="#fca5a5" />}
                            </div>
                            <div>
                              <p style={{ fontWeight: 600, color: 'var(--text-primary)', margin: '0 0 2px', fontSize: '0.85rem' }}>{txn.type === 'receive' ? 'Received' : 'Sent'} {txn.amount}</p>
                              <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', margin: 0 }}>{txn.type === 'receive' ? `From: ${txn.from}` : `To: ${txn.to}`}</p>
                            </div>
                          </div>
                          <div style={{ textAlign: 'right' }}>
                            <p style={{ fontWeight: 700, color: txn.type === 'receive' ? '#6ee7b7' : '#fca5a5', margin: '0 0 2px', fontSize: '0.85rem' }}>{txn.amount}</p>
                            <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', margin: 0 }}>{new Date(txn.timestamp).toLocaleDateString()}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <div style={{ textAlign: 'center', padding: '3rem 1rem' }}>
                  <Wallet size={48} style={{ color: 'rgba(139,92,246,0.3)', margin: '0 auto 1rem' }} />
                  <h3 style={{ fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>Connect Your Wallet</h3>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '1.5rem' }}>Connect your crypto wallet to view transactions and make payments</p>
                  <button onClick={handleConnectWallet} disabled={connecting} style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '0.75rem 1.5rem', background: 'linear-gradient(135deg, #7c3aed, #a855f7)', border: 'none', borderRadius: 10, color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
                    <Link size={16} /> {connecting ? 'Connecting...' : 'Connect Wallet'}
                  </button>
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

      {/* Payment Modal */}
      {showPaymentModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '1rem' }}>
          <div style={{ ...glass, width: '100%', maxWidth: 400, padding: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h3 style={{ fontWeight: 700, color: 'var(--text-primary)', margin: 0, fontSize: '1.1rem' }}>Send Crypto Payment</h3>
              <button onClick={() => { setShowPaymentModal(false); setPaymentSuccess(null); }} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}><X size={20} /></button>
            </div>

            {paymentSuccess ? (
              <div style={{ textAlign: 'center', padding: '1rem' }}>
                <div style={{ width: 64, height: 64, borderRadius: '50%', background: 'rgba(16,185,129,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem' }}>
                  <CheckCircle size={32} color="#6ee7b7" />
                </div>
                <h4 style={{ fontWeight: 700, color: '#6ee7b7', marginBottom: '0.5rem' }}>Payment Successful!</h4>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '1rem' }}>Your payment has been processed</p>
                <div style={{ background: 'rgba(255,255,255,0.04)', borderRadius: 8, padding: '0.75rem', marginBottom: '1rem' }}>
                  <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', margin: '0 0 4px' }}>Transaction Hash</p>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', margin: 0, wordBreak: 'break-all' }}>{paymentSuccess.txHash}</p>
                </div>
                <button onClick={() => { setShowPaymentModal(false); setPaymentSuccess(null); }} style={{ padding: '0.6rem 1.5rem', background: 'linear-gradient(135deg, #7c3aed, #a855f7)', border: 'none', borderRadius: 8, color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
                  Done
                </button>
              </div>
            ) : (
              <>
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 6, fontWeight: 600 }}>Recipient Address</label>
                  <input
                    type="text"
                    value={paymentTo}
                    onChange={(e) => setPaymentTo(e.target.value)}
                    placeholder="0x..."
                    style={{ width: '100%', padding: '0.6rem 0.9rem', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 8, color: 'var(--text-primary)', fontSize: '0.9rem' }}
                  />
                </div>
                <div style={{ marginBottom: '1.5rem' }}>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 6, fontWeight: 600 }}>Amount (MATIC)</label>
                  <input
                    type="number"
                    value={paymentAmount}
                    onChange={(e) => setPaymentAmount(e.target.value)}
                    placeholder="0.00"
                    step="0.001"
                    style={{ width: '100%', padding: '0.6rem 0.9rem', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 8, color: 'var(--text-primary)', fontSize: '0.9rem' }}
                  />
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: '4px 0 0' }}>Available: {cryptoBalance?.matic || '0'} MATIC</p>
                </div>
                <button onClick={handleSimulatePayment} disabled={processing || !paymentAmount} style={{ width: '100%', padding: '0.75rem', background: processing ? 'rgba(139,92,246,0.3)' : 'linear-gradient(135deg, #7c3aed, #a855f7)', border: 'none', borderRadius: 10, color: '#fff', fontWeight: 700, cursor: processing || !paymentAmount ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
                  {processing ? (
                    <>
                      <div style={{ width: 16, height: 16, borderRadius: '50%', border: '2px solid rgba(255,255,255,0.3)', borderTopColor: '#fff', animation: 'spin 0.7s linear infinite' }} />
                      Processing...
                    </>
                  ) : (
                    <><Send size={16} /> Send Payment</>
                  )}
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default TrustWallet;
