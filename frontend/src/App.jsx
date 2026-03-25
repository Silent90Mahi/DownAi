import { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import { LogOut, Zap } from 'lucide-react';

// Pages
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Marketplace from './components/Marketplace';
import ChatAssistant from './components/ChatAssistant';
import SellProduct from './components/SellProduct';
import AdminDashboard from './components/AdminDashboard';

// Lazy load other pages
import OrdersList from './components/OrdersList';
import OrderDetail from './components/OrderDetail';
import Checkout from './components/Checkout';
import MarketAnalyzer from './components/MarketAnalyzer';
import SupplierMarket from './components/SupplierMarket';
import SupplierProfile from './components/SupplierProfile';
import BuyerMatches from './components/BuyerMatches';
import Profile from './components/Profile';
import TrustWallet from './components/TrustWallet';
import BulkRequests from './components/BulkRequests';
import NotificationsPanel from './components/NotificationsPanel';
import CommunityHub from './components/CommunityHub';
import Reports from './components/Reports';
import MyProducts from './components/MyProducts';
import ProductDetail from './components/ProductDetail';
import ProductEdit from './components/ProductEdit';

function App() {
  const { isAuthenticated, loading, isAdmin, logout } = useAuth();
  const [lowBandwidth, setLowBandwidth] = useState(false);

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--bg-primary)',
      }}>
        <div style={{ textAlign: 'center' }}>
          {/* Animated Logo */}
          <div style={{
            width: 72,
            height: 72,
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #7c3aed, #a855f7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 20px',
            boxShadow: '0 0 30px rgba(139,92,246,0.5)',
            animation: 'glowPulse 2s ease-in-out infinite',
          }}>
            <Zap size={32} color="#fff" />
          </div>
          <div style={{
            width: 48,
            height: 3,
            background: 'linear-gradient(90deg, #7c3aed, #a855f7, #e879f9)',
            borderRadius: 99,
            margin: '0 auto 16px',
            animation: 'glowPulse 1.5s ease-in-out infinite',
          }} />
          <p style={{ color: 'var(--text-tertiary)', fontWeight: 600, letterSpacing: '0.05em' }}>
            Loading...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={lowBandwidth ? 'low-bandwidth' : ''}>
      {/* Header Bar */}
      {isAuthenticated && (
        <header style={{
          position: 'sticky',
          top: 0,
          zIndex: 40,
          background: 'rgba(13, 10, 26, 0.85)',
          borderBottom: '1px solid rgba(139, 92, 246, 0.2)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
        }}>
          <div style={{
            maxWidth: 1280,
            margin: '0 auto',
            padding: '0.75rem 1.5rem',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}>
            {/* Logo */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{
                width: 38,
                height: 38,
                borderRadius: 10,
                background: 'linear-gradient(135deg, #7c3aed 0%, #a855f7 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 0 15px rgba(139,92,246,0.4)',
              }}>
                <Zap size={20} color="#fff" fill="#fff" />
              </div>
              <span style={{
                fontWeight: 800,
                fontSize: '1.25rem',
                background: 'linear-gradient(135deg, #c4b5fd 0%, #a78bfa 50%, #e879f9 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}>
                Ooumph
              </span>
            </div>

            {/* Controls */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <button
                onClick={() => setLowBandwidth(!lowBandwidth)}
                style={{
                  fontSize: '0.8rem',
                  padding: '6px 12px',
                  borderRadius: 8,
                  border: '1px solid rgba(139,92,246,0.25)',
                  cursor: 'pointer',
                  background: lowBandwidth
                    ? 'rgba(139,92,246,0.2)'
                    : 'rgba(255,255,255,0.05)',
                  color: lowBandwidth ? '#c4b5fd' : 'var(--text-tertiary)',
                  transition: 'all 0.2s',
                }}
              >
                {lowBandwidth ? 'Fast Mode' : 'Normal'}
              </button>

              <NotificationsPanel />

              <button
                onClick={() => {
                  logout();
                  window.location.href = '/login';
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  fontSize: '0.8rem',
                  padding: '6px 14px',
                  borderRadius: 8,
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  background: 'rgba(239, 68, 68, 0.1)',
                  color: '#fca5a5',
                  cursor: 'pointer',
                  fontWeight: 600,
                  transition: 'all 0.2s',
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.background = 'rgba(239, 68, 68, 0.2)';
                  e.currentTarget.style.boxShadow = '0 0 12px rgba(239,68,68,0.2)';
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                <LogOut size={14} />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </header>
      )}

      {/* Routes */}
      <Routes>
        <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/" />} />

        {/* Protected Routes */}
        <Route path="/"                element={isAuthenticated ? <Dashboard />      : <Navigate to="/login" />} />
        <Route path="/marketplace"     element={isAuthenticated ? <Marketplace />    : <Navigate to="/login" />} />
        <Route path="/sell"            element={isAuthenticated ? <SellProduct />    : <Navigate to="/login" />} />
        <Route path="/my-products"     element={isAuthenticated ? <MyProducts />     : <Navigate to="/login" />} />
        <Route path="/products/:productId"       element={isAuthenticated ? <ProductDetail /> : <Navigate to="/login" />} />
        <Route path="/products/:productId/edit"  element={isAuthenticated ? <ProductEdit />   : <Navigate to="/login" />} />
        <Route path="/orders"          element={isAuthenticated ? <OrdersList />     : <Navigate to="/login" />} />
        <Route path="/checkout"        element={isAuthenticated ? <Checkout />       : <Navigate to="/login" />} />
        <Route path="/orders/:orderId" element={isAuthenticated ? <OrderDetail />   : <Navigate to="/login" />} />
        <Route path="/market-analyzer" element={isAuthenticated ? <MarketAnalyzer />: <Navigate to="/login" />} />
        <Route path="/suppliers"       element={isAuthenticated ? <SupplierMarket />: <Navigate to="/login" />} />
        <Route path="/suppliers/:supplierId" element={isAuthenticated ? <SupplierProfile />: <Navigate to="/login" />} />
        <Route path="/matches"         element={isAuthenticated ? <BuyerMatches />  : <Navigate to="/login" />} />
        <Route path="/profile"         element={isAuthenticated ? <Profile />       : <Navigate to="/login" />} />
        <Route path="/wallet"          element={isAuthenticated ? <TrustWallet />   : <Navigate to="/login" />} />
        <Route path="/bulk-requests"   element={isAuthenticated ? <BulkRequests />  : <Navigate to="/login" />} />
        <Route path="/community"       element={isAuthenticated ? <CommunityHub />  : <Navigate to="/login" />} />

        {/* Admin Routes */}
        <Route path="/admin"   element={isAuthenticated && isAdmin ? <AdminDashboard /> : <Navigate to="/" />} />
        <Route path="/reports" element={isAuthenticated && isAdmin ? <Reports />        : <Navigate to="/" />} />

        <Route path="*" element={<Navigate to="/" />} />
      </Routes>

      {/* Chat Assistant - Global */}
      {isAuthenticated && <ChatAssistant />}
    </div>
  );
}

export default App;
