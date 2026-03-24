import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import PropTypes from 'prop-types';
import { Sparkles, ChevronRight, Star, Shield, Package } from 'lucide-react';
import { recommendationAPI } from '../services/recommendationAPI';

const ProductSkeleton = () => (
  <div className="flex-shrink-0 w-64 bg-white rounded-2xl border border-gray-100 overflow-hidden animate-pulse">
    <div className="aspect-square w-full bg-gray-200" />
    <div className="p-4 space-y-3">
      <div className="h-4 bg-gray-200 rounded w-3/4" />
      <div className="h-6 bg-gray-200 rounded w-1/2" />
      <div className="h-3 bg-gray-200 rounded w-full" />
    </div>
  </div>
);

const RecommendationSection = ({
  title = 'Recommended for You',
  limit = 10,
  type = 'products'
}) => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchRecommendations();
  }, [type, limit]);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await recommendationAPI.getRecommendations(type, limit);
      setRecommendations(response.data || []);
    } catch (err) {
      console.error('Failed to fetch recommendations:', err);
      setError('Unable to load recommendations');
    } finally {
      setLoading(false);
    }
  };

  const handleProductClick = (productId) => {
    navigate(`/products/${productId}`);
  };

  const formatPrice = (price) => {
    if (typeof price === 'number') {
      return price.toLocaleString('en-IN');
    }
    return price;
  };

  const renderSkeletons = () => (
    <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide">
      {Array.from({ length: 4 }).map((_, index) => (
        <ProductSkeleton key={index} />
      ))}
    </div>
  );

  const renderEmptyState = () => (
    <div className="text-center py-12 bg-white rounded-2xl border border-gray-100">
      <Package className="w-12 h-12 mx-auto text-gray-300 mb-3" />
      <p className="text-gray-400 font-medium">No recommendations available yet</p>
      <p className="text-sm text-gray-300 mt-1">Start browsing to get personalized suggestions</p>
    </div>
  );

  const renderErrorState = () => (
    <div className="text-center py-12 bg-red-50 rounded-2xl border border-red-100">
      <p className="text-red-500 font-medium">{error}</p>
      <button
        onClick={fetchRecommendations}
        className="mt-3 text-sm text-red-600 hover:text-red-700 font-semibold"
      >
        Try Again
      </button>
    </div>
  );

  if (error && !loading) {
    return renderErrorState();
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-[#FF9933]" />
          <h2 className="text-xl font-bold text-[#333333]">{title}</h2>
        </div>
        <button
          onClick={() => navigate('/marketplace')}
          className="flex items-center gap-1 text-sm text-[#FF9933] hover:text-[#e68a2e] font-semibold transition"
        >
          View All
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {loading ? (
        renderSkeletons()
      ) : recommendations.length === 0 ? (
        renderEmptyState()
      ) : (
        <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide snap-x snap-mandatory">
          {recommendations.map((item) => (
            <article
              key={item.id}
              onClick={() => handleProductClick(item.id)}
              className="flex-shrink-0 w-64 bg-white rounded-2xl border border-gray-100 overflow-hidden cursor-pointer transition-all duration-200 hover:shadow-lg hover:border-[#FF9933]/30 snap-start group"
            >
              <div className="relative aspect-square w-full bg-gray-50 overflow-hidden">
                {item.image_url ? (
                  <img
                    src={item.image_url}
                    alt={item.name}
                    className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                    loading="lazy"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200">
                    <Package className="w-12 h-12 text-gray-300" />
                  </div>
                )}

                {item.recommendation_score && (
                  <div className="absolute top-2 right-2 bg-white/90 backdrop-blur-sm px-2 py-1 rounded-full flex items-center gap-1 shadow-sm">
                    <Star className="w-3 h-3 text-yellow-500 fill-yellow-500" />
                    <span className="text-xs font-bold text-gray-700">
                      {Math.round(item.recommendation_score * 100)}%
                    </span>
                  </div>
                )}
              </div>

              <div className="p-4 space-y-2">
                <h3 className="text-base font-semibold text-gray-800 line-clamp-2 group-hover:text-[#FF9933] transition">
                  {item.name}
                </h3>

                <div className="flex items-baseline gap-1">
                  <span className="text-lg font-bold text-[#138808]">₹</span>
                  <span className="text-xl font-bold text-[#138808]">
                    {formatPrice(item.price)}
                  </span>
                </div>

                {item.trust_score !== undefined && (
                  <div className="flex items-center gap-1 text-sm">
                    <Shield className="w-4 h-4 text-[#138808]" />
                    <span className="text-[#138808] font-semibold">
                      Trust: {item.trust_score.toFixed(1)}
                    </span>
                  </div>
                )}

                {item.seller_name && (
                  <p className="text-xs text-gray-400 truncate">by {item.seller_name}</p>
                )}
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
};

RecommendationSection.propTypes = {
  title: PropTypes.string,
  limit: PropTypes.number,
  type: PropTypes.oneOf(['products', 'shgs'])
};

export default RecommendationSection;
