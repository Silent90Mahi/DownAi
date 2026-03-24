import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import PropTypes from 'prop-types';
import { Layers, Package, ArrowRight } from 'lucide-react';
import { recommendationAPI } from '../services/recommendationAPI';

const SimilarProductSkeleton = () => (
  <div className="flex-shrink-0 w-72 bg-white rounded-xl border border-gray-100 overflow-hidden animate-pulse">
    <div className="h-40 bg-gray-200" />
    <div className="p-4 space-y-2">
      <div className="h-4 bg-gray-200 rounded w-3/4" />
      <div className="h-5 bg-gray-200 rounded w-1/2" />
    </div>
  </div>
);

const SimilarProducts = ({ productId, limit = 5 }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (productId) {
      fetchSimilarProducts();
    }
  }, [productId, limit]);

  const fetchSimilarProducts = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await recommendationAPI.getSimilarProducts(productId, limit);
      setProducts(response.data || []);
    } catch (err) {
      console.error('Failed to fetch similar products:', err);
      setError('Unable to load similar products');
    } finally {
      setLoading(false);
    }
  };

  const handleProductClick = (similarProductId) => {
    navigate(`/products/${similarProductId}`);
  };

  const formatPrice = (price) => {
    if (typeof price === 'number') {
      return price.toLocaleString('en-IN');
    }
    return price;
  };

  if (!productId) {
    return null;
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <Layers className="w-5 h-5 text-[#FF9933]" />
          <h3 className="text-lg font-bold text-[#333333]">Similar Products</h3>
        </div>
        <div className="flex gap-4 overflow-x-auto pb-2">
          {Array.from({ length: 3 }).map((_, index) => (
            <SimilarProductSkeleton key={index} />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 rounded-xl p-4 border border-red-100">
        <p className="text-red-500 text-sm">{error}</p>
      </div>
    );
  }

  if (products.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Layers className="w-5 h-5 text-[#FF9933]" />
        <h3 className="text-lg font-bold text-[#333333]">Similar Products</h3>
      </div>

      <div className="flex gap-4 overflow-x-auto pb-2 scrollbar-hide snap-x snap-mandatory">
        {products.map((product) => (
          <article
            key={product.id}
            onClick={() => handleProductClick(product.id)}
            className="flex-shrink-0 w-72 bg-white rounded-xl border border-gray-100 overflow-hidden cursor-pointer transition-all duration-200 hover:shadow-lg hover:border-[#FF9933]/30 snap-start group"
          >
            <div className="relative h-40 bg-gray-50 overflow-hidden">
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

              {product.similarity_score !== undefined && (
                <div className="absolute top-2 left-2 bg-[#138808] text-white px-2 py-1 rounded-full text-xs font-bold">
                  {Math.round(product.similarity_score * 100)}% Similar
                </div>
              )}
            </div>

            <div className="p-4">
              <h4 className="font-semibold text-gray-800 line-clamp-1 group-hover:text-[#FF9933] transition">
                {product.name}
              </h4>
              <div className="flex items-center justify-between mt-2">
                <div className="flex items-baseline gap-1">
                  <span className="text-sm text-[#138808]">₹</span>
                  <span className="text-lg font-bold text-[#138808]">
                    {formatPrice(product.price)}
                  </span>
                </div>
                <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-[#FF9933] transition" />
              </div>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
};

SimilarProducts.propTypes = {
  productId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  limit: PropTypes.number
};

export default SimilarProducts;
