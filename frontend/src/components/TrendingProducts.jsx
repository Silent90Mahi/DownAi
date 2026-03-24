import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import PropTypes from 'prop-types';
import { TrendingUp, Package, ShoppingBag, ChevronRight } from 'lucide-react';
import { recommendationAPI } from '../services/recommendationAPI';

const TrendingProductSkeleton = () => (
  <div className="flex-shrink-0 w-56 bg-white rounded-2xl border border-gray-100 overflow-hidden animate-pulse">
    <div className="aspect-square w-full bg-gray-200" />
    <div className="p-3 space-y-2">
      <div className="h-3 bg-gray-200 rounded w-2/3" />
      <div className="h-5 bg-gray-200 rounded w-1/2" />
      <div className="h-3 bg-gray-200 rounded w-full" />
    </div>
  </div>
);

const TrendingProducts = ({ district = null, limit = 10 }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchTrendingProducts();
  }, [district, limit]);

  const fetchTrendingProducts = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await recommendationAPI.getTrendingProducts(district, limit);
      setProducts(response.data || []);
    } catch (err) {
      console.error('Failed to fetch trending products:', err);
      setError('Unable to load trending products');
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
        <TrendingProductSkeleton key={index} />
      ))}
    </div>
  );

  const renderErrorState = () => (
    <div className="text-center py-10 bg-red-50 rounded-2xl border border-red-100">
      <p className="text-red-500 font-medium">{error}</p>
      <button
        onClick={fetchTrendingProducts}
        className="mt-3 text-sm text-red-600 hover:text-red-700 font-semibold"
      >
        Try Again
      </button>
    </div>
  );

  const renderEmptyState = () => (
    <div className="text-center py-10 bg-white rounded-2xl border border-gray-100">
      <TrendingUp className="w-10 h-10 mx-auto text-gray-300 mb-2" />
      <p className="text-gray-400 font-medium">No trending products yet</p>
    </div>
  );

  if (error && !loading) {
    return renderErrorState();
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-[#FF9933]" />
          <h2 className="text-xl font-bold text-[#333333]">Trending Now</h2>
          {district && (
            <span className="text-sm text-gray-400 font-medium">in {district}</span>
          )}
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
      ) : products.length === 0 ? (
        renderEmptyState()
      ) : (
        <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide snap-x snap-mandatory">
          {products.map((product) => (
            <article
              key={product.id}
              onClick={() => handleProductClick(product.id)}
              className="flex-shrink-0 w-56 bg-white rounded-2xl border border-gray-100 overflow-hidden cursor-pointer transition-all duration-200 hover:shadow-lg hover:border-[#FF9933]/30 snap-start group"
            >
              <div className="relative aspect-square w-full bg-gray-50 overflow-hidden">
                {product.image_url ? (
                  <img
                    src={product.image_url}
                    alt={product.name}
                    className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                    loading="lazy"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200">
                    <Package className="w-10 h-10 text-gray-300" />
                  </div>
                )}

                {product.order_count !== undefined && (
                  <div className="absolute top-2 right-2 bg-[#FF9933] text-white px-2 py-1 rounded-full flex items-center gap-1">
                    <ShoppingBag className="w-3 h-3" />
                    <span className="text-xs font-bold">
                      {product.order_count > 999 ? `${(product.order_count / 1000).toFixed(1)}k` : product.order_count}
                    </span>
                  </div>
                )}
              </div>

              <div className="p-3 space-y-2">
                <h3 className="text-sm font-semibold text-gray-800 line-clamp-2 group-hover:text-[#FF9933] transition">
                  {product.name}
                </h3>

                <div className="flex items-baseline gap-1">
                  <span className="text-sm text-[#138808]">₹</span>
                  <span className="text-lg font-bold text-[#138808]">
                    {formatPrice(product.price)}
                  </span>
                </div>

                {product.category && (
                  <span className="text-xs text-gray-400 bg-gray-50 px-2 py-0.5 rounded-full">
                    {product.category}
                  </span>
                )}
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
};

TrendingProducts.propTypes = {
  district: PropTypes.string,
  limit: PropTypes.number
};

export default TrendingProducts;
