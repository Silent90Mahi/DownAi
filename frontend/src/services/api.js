import axios from 'axios';

const API_BASE_URL = window.location.hostname === 'localhost' && window.location.port === '5173'
  ? 'http://localhost:6002'
  : '/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    // Remove Content-Type for FormData to let browser set it with boundary
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============================================================================
// AUTH API
// ============================================================================

export const authAPI = {
  register: (data) => api.post('/api/auth/register', data),
  registerAndSendOTP: (data) => api.post('/api/auth/register-and-send-otp', data),
  login: (email, password) => api.post('/api/auth/admin-login', { email, password }),
  sendOTP: (phone) => api.post('/api/auth/send-otp', { phone }),
  verifyOTP: (phone, otp) => api.post('/api/auth/verify-otp', { phone, otp }),
  getProfile: () => api.get('/api/auth/profile'),
  updateProfile: (data) => api.put('/api/auth/profile', data),
  logout: () => api.post('/api/auth/logout'),
};

// ============================================================================
// CHAT API (Agent Vaani)
// ============================================================================

export const chatAPI = {
  sendMessage: (query, language = 'English') =>
    api.post('/api/chat/process', { query, language }),
  getHistory: (limit = 50) => api.get(`/api/chat/history?limit=${limit}`),
};

// ============================================================================
// PRODUCTS API
// ============================================================================

export const productsAPI = {
  create: (data) => api.post('/api/products/', data),
  getAll: (params) => {
    if (typeof params === 'string') {
      return api.get('/api/products/', { params: { status: params } });
    }
    return api.get('/api/products/', { params: params || {} });
  },
  getById: (id) => api.get(`/api/products/${id}`),
  update: (id, data) => api.put(`/api/products/${id}`, data),
  delete: (id) => api.delete(`/api/products/${id}`),
  getMyProducts: () => api.get('/api/products/my/products'),
};

// ============================================================================
// ORDERS API
// ============================================================================

export const ordersAPI = {
  create: (data) => api.post('/api/orders/', data),
  getAll: (status) => api.get(`/api/orders/${status ? `?status=${status}` : ''}`),
  getById: (id) => api.get(`/api/orders/${id}`),
  updateStatus: (id, status, trackingNumber) =>
    api.patch(`/api/orders/${id}/status`, { status, tracking_number: trackingNumber }),
};

// ============================================================================
// MARKET API (Agent Bazaar Buddhi)
// ============================================================================

export const marketAPI = {
  analyze: (productName, category, district, price) =>
    api.post('/api/market/analyze', {
      product_name: productName,
      category: category,
      district: district,
      price: price
    }),
  getPriceSuggestion: (data) => api.post('/api/market/price-suggestion', data),
  getTrends: (category, district) =>
    api.get(`/api/market/trends?category=${category || ''}&district=${district || ''}`),
};

// ============================================================================
// MATCHING API (Agent Jodi)
// ============================================================================

export const matchingAPI = {
  findBuyers: (data) => api.post('/api/matching/buyers', data),
  getRequirements: (category, district) =>
    api.get(`/api/matching/requirements?category=${category || ''}&district=${district || ''}`),
  negotiate: (buyerId, productId, initialPrice, quantity) =>
    api.post('/api/matching/negotiate', null, {
      params: { buyer_id: buyerId, product_id: productId, initial_price: initialPrice, quantity }
    }),
  getGeMOpportunities: (category, district) =>
    api.get(`/api/matching/gem-opportunities?category=${category || ''}&district=${district || ''}`),
  getOndcStatus: () => api.get('/api/matching/ondc-status'),
};

// ============================================================================
// SUPPLIERS API (Agent Samagri)
// ============================================================================

export const suppliersAPI = {
  search: (params) => api.get('/api/suppliers/search', { params }),
  getSupplier: (id) => api.get(`/api/suppliers/supplier/${id}`),
  listSuppliers: (params) => api.get('/api/suppliers/list', { params }),
  
  createBulkRequest: (data) => api.post('/api/suppliers/bulk-request', data),
  joinBulkRequest: (requestId, quantity) =>
    api.post(`/api/suppliers/bulk-request/${requestId}/join`, null, { params: { quantity } }),
  getBulkRequests: (district, status = 'Open') =>
    api.get(`/api/suppliers/bulk-requests?district=${district || ''}&status=${status}`),
  getPriceTrends: (materialName, district, months = 6) =>
    api.get(`/api/suppliers/price-trends/${materialName}?district=${district}&months=${months}`),
  
  getSupplierReviews: (supplierId, limit = 10, offset = 0) =>
    api.get(`/api/suppliers/supplier/${supplierId}/reviews?limit=${limit}&offset=${offset}`),
  createReview: (data) => api.post('/api/suppliers/reviews', data),
  markReviewHelpful: (reviewId) => api.post(`/api/suppliers/reviews/${reviewId}/helpful`),
  
  connect: (supplierId, message) => api.post('/api/suppliers/connect', { supplier_id: supplierId, message }),
  getConnections: (status) => api.get(`/api/suppliers/connections${status ? `?status=${status}` : ''}`),
  acceptConnection: (connectionId) => api.post(`/api/suppliers/connections/${connectionId}/accept`),
  rejectConnection: (connectionId) => api.post(`/api/suppliers/connections/${connectionId}/reject`),
  
  requestQuote: (data) => api.post('/api/suppliers/quotes', data),
  getQuotes: (status) => api.get(`/api/suppliers/quotes${status ? `?status=${status}` : ''}`),
  acceptQuote: (quoteId) => api.post(`/api/suppliers/quotes/${quoteId}/accept`),
  rejectQuote: (quoteId) => api.post(`/api/suppliers/quotes/${quoteId}/reject`),
};

// ============================================================================
// TRUST API (Agent Vishwas)
// ============================================================================

export const trustAPI = {
  getScore: () => api.get('/api/trust/score'),
  getHistory: (limit = 50) => api.get(`/api/trust/history?limit=${limit}`),
  getCoins: () => api.get('/api/trust/coins'),
  getLeaderboard: (limit = 50, district) =>
    api.get(`/api/trust/leaderboard?limit=${limit}&district=${district || ''}`),
  redeemCoins: (amount, rewardType) =>
    api.post('/api/trust/redeem', null, { params: { amount, reward_type: rewardType } }),
  getAuditLogs: (entityType, limit = 100) =>
    api.get(`/api/trust/audit-logs?entity_type=${entityType || ''}&limit=${limit}`),
};

// ============================================================================
// COMMUNITY API (Agent Sampark)
// ============================================================================

export const communityAPI = {
  getHierarchy: () => api.get('/api/community/hierarchy'),
  getFederationMembers: (federationId, level) =>
    api.get(`/api/community/federation/${federationId}/members?federation_level=${level}`),
  getFederationStats: (federationId, level) =>
    api.get(`/api/community/federation/${federationId}/stats?federation_level=${level}`),
  sendAlert: (title, message, targetLevel, district) =>
    api.post('/api/community/alert', null, {
      params: { title, message, target_level: targetLevel, district }
    }),
  getDistrictOverview: (district) => api.get(`/api/community/district/${district}`),
  escalate: (issueType, issueDetails, urgency = 'medium') =>
    api.post('/api/community/escalate', null, {
      params: { issue_type: issueType, issue_details: issueDetails, urgency }
    }),
  getAnnouncements: (district, limit = 10) =>
    api.get(`/api/community/announcements?district=${district || ''}&limit=${limit}`),
  getFederationPerformance: (federationId, periodMonths = 6) =>
    api.get(`/api/community/federation/${federationId}/performance?period_months=${periodMonths}`),
};

// ============================================================================
// PAYMENTS API
// ============================================================================

export const paymentsAPI = {
  initiate: (orderId, useCoins = false, coinsToUse = 0) =>
    api.post('/api/payments/initiate', null, {
      params: { order_id: orderId, use_coins: useCoins, coins_to_use: coinsToUse }
    }),
  getStatus: (paymentId) => api.get(`/api/payments/status/${paymentId}`),
  getMethods: () => api.get('/api/payments/methods'),
  calculateBreakdown: (orderId, useCoins = false, coinsToUse = 0) =>
    api.post('/api/payments/calculate', null, {
      params: { order_id: orderId, use_coins: useCoins, coins_to_use: coinsToUse }
    }),
  refund: (orderId, reason) =>
    api.post(`/api/payments/refund/${orderId}`, null, { params: { reason } }),
};

// ============================================================================
// ANALYTICS API
// ============================================================================

export const analyticsAPI = {
  getDashboard: (district, federationId) =>
    api.get('/api/analytics/dashboard', { params: { district, federation_id } }),
  getDistrictStats: () => api.get('/api/analytics/districts'),
  getUserAnalytics: (userId, periodMonths = 6) =>
    api.get(`/api/analytics/user/${userId}?period_months=${periodMonths}`),
  getTopPerformers: (limit = 20, district, period = 'month') =>
    api.get('/api/analytics/top-performers', { params: { limit, district, period } }),
  getCategories: () => api.get('/api/analytics/categories'),
  getTrustDistribution: () => api.get('/api/analytics/trust-distribution'),
};

// ============================================================================
// NOTIFICATIONS API
// ============================================================================

export const notificationsAPI = {
  getAll: (unreadOnly = false, limit = 50) =>
    api.get(`/api/notifications/${unreadOnly ? `?unread_only=true&` : ''}?limit=${limit}`),
  getUnreadCount: () => api.get('/api/notifications/unread-count'),
  markAsRead: (notificationId) => api.put(`/api/notifications/${notificationId}/read`),
  markAllAsRead: () => api.put('/api/notifications/read-all'),
  deleteOld: (daysOld = 90) => api.delete('/api/notifications/old', { params: { days_old: daysOld } }),
};

// ============================================================================
// REPORTS API
// ============================================================================

export const reportsAPI = {
  generate: (reportType, filters = {}, dateRange = null, format = 'pdf') =>
    api.post('/api/reports/generate', { report_type: reportType, filters, date_range, format }),
  download: (reportId) => api.get(`/api/reports/download/${reportId}`),
};

// ============================================================================
// EXPORT
// ============================================================================

export { api };
export default api;
