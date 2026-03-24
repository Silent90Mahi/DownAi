import api from './api';

export const recommendationAPI = {
  getRecommendations: (type = 'products', limit = 10) =>
    api.get('/api/recommendations', { params: { type, limit } }),

  getSimilarProducts: (productId, limit = 5) =>
    api.get(`/api/recommendations/products/${productId}/similar`, { params: { limit } }),

  getTrendingProducts: (district = null, limit = 10) =>
    api.get('/api/recommendations/trending', { params: { district, limit } }),

  getRecommendedSHGs: (limit = 5) =>
    api.get('/api/recommendations/shgs', { params: { limit } }),

  getRecommendationExplanation: (productId) =>
    api.get(`/api/recommendations/products/${productId}/explain`),
};

export default recommendationAPI;
