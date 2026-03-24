import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import PropTypes from 'prop-types';
import { Users, Shield, Package, UserPlus, UserCheck, ChevronRight } from 'lucide-react';
import { recommendationAPI } from '../services/recommendationAPI';

const SHGSkeleton = () => (
  <div className="flex-shrink-0 w-72 bg-white rounded-2xl border border-gray-100 overflow-hidden animate-pulse">
    <div className="p-4 space-y-3">
      <div className="flex items-center gap-3">
        <div className="w-14 h-14 rounded-full bg-gray-200" />
        <div className="flex-1 space-y-2">
          <div className="h-4 bg-gray-200 rounded w-3/4" />
          <div className="h-3 bg-gray-200 rounded w-1/2" />
        </div>
      </div>
      <div className="flex gap-2">
        <div className="h-6 bg-gray-200 rounded-full w-20" />
        <div className="h-6 bg-gray-200 rounded-full w-20" />
      </div>
    </div>
  </div>
);

const RecommendedSHGs = ({ limit = 5 }) => {
  const [shgs, setShgs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [followingIds, setFollowingIds] = useState(new Set());
  const navigate = useNavigate();

  useEffect(() => {
    fetchRecommendedSHGs();
  }, [limit]);

  const fetchRecommendedSHGs = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await recommendationAPI.getRecommendedSHGs(limit);
      setShgs(response.data || []);
    } catch (err) {
      console.error('Failed to fetch recommended SHGs:', err);
      setError('Unable to load recommended SHGs');
    } finally {
      setLoading(false);
    }
  };

  const handleFollow = async (shgId) => {
    try {
      setFollowingIds(prev => new Set([...prev, shgId]));
    } catch (err) {
      console.error('Failed to follow SHG:', err);
      setFollowingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(shgId);
        return newSet;
      });
    }
  };

  const handleSHGClick = (shgId) => {
    navigate(`/shgs/${shgId}`);
  };

  const renderSkeletons = () => (
    <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide">
      {Array.from({ length: 3 }).map((_, index) => (
        <SHGSkeleton key={index} />
      ))}
    </div>
  );

  const renderErrorState = () => (
    <div className="text-center py-10 bg-red-50 rounded-2xl border border-red-100">
      <p className="text-red-500 font-medium">{error}</p>
      <button
        onClick={fetchRecommendedSHGs}
        className="mt-3 text-sm text-red-600 hover:text-red-700 font-semibold"
      >
        Try Again
      </button>
    </div>
  );

  const renderEmptyState = () => (
    <div className="text-center py-10 bg-white rounded-2xl border border-gray-100">
      <Users className="w-10 h-10 mx-auto text-gray-300 mb-2" />
      <p className="text-gray-400 font-medium">No SHG recommendations yet</p>
    </div>
  );

  if (error && !loading) {
    return renderErrorState();
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Users className="w-5 h-5 text-[#FF9933]" />
          <h2 className="text-xl font-bold text-[#333333]">SHGs to Follow</h2>
        </div>
        <button
          onClick={() => navigate('/community')}
          className="flex items-center gap-1 text-sm text-[#FF9933] hover:text-[#e68a2e] font-semibold transition"
        >
          View All
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {loading ? (
        renderSkeletons()
      ) : shgs.length === 0 ? (
        renderEmptyState()
      ) : (
        <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide snap-x snap-mandatory">
          {shgs.map((shg) => {
            const isFollowing = followingIds.has(shg.id);
            
            return (
              <article
                key={shg.id}
                className="flex-shrink-0 w-72 bg-white rounded-2xl border border-gray-100 overflow-hidden transition-all duration-200 hover:shadow-lg hover:border-[#FF9933]/30 snap-start group"
              >
                <div className="p-4 space-y-4">
                  <div 
                    className="flex items-center gap-3 cursor-pointer"
                    onClick={() => handleSHGClick(shg.id)}
                  >
                    <div className="w-14 h-14 rounded-full bg-gradient-to-br from-[#FF9933] to-[#138808] flex items-center justify-center overflow-hidden">
                      {shg.profile_image ? (
                        <img
                          src={shg.profile_image}
                          alt={shg.name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <span className="text-white text-xl font-bold">
                          {shg.name?.charAt(0)?.toUpperCase() || 'S'}
                        </span>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-gray-800 truncate group-hover:text-[#FF9933] transition">
                        {shg.name}
                      </h3>
                      {shg.district && (
                        <p className="text-sm text-gray-400 truncate">{shg.district}</p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    {shg.trust_score !== undefined && (
                      <div className="flex items-center gap-1 bg-[#138808]/10 px-3 py-1.5 rounded-full">
                        <Shield className="w-4 h-4 text-[#138808]" />
                        <span className="text-sm font-semibold text-[#138808]">
                          {shg.trust_score.toFixed(1)}
                        </span>
                      </div>
                    )}
                    {shg.product_count !== undefined && (
                      <div className="flex items-center gap-1 bg-gray-100 px-3 py-1.5 rounded-full">
                        <Package className="w-4 h-4 text-gray-500" />
                        <span className="text-sm font-semibold text-gray-600">
                          {shg.product_count} Products
                        </span>
                      </div>
                    )}
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleFollow(shg.id);
                    }}
                    disabled={isFollowing}
                    className={`w-full py-2.5 rounded-xl font-semibold text-sm transition-all duration-200 flex items-center justify-center gap-2 ${
                      isFollowing
                        ? 'bg-[#138808]/10 text-[#138808] cursor-default'
                        : 'bg-[#FF9933] text-white hover:bg-[#e68a2e] active:scale-[0.98]'
                    }`}
                  >
                    {isFollowing ? (
                      <>
                        <UserCheck className="w-4 h-4" />
                        Following
                      </>
                    ) : (
                      <>
                        <UserPlus className="w-4 h-4" />
                        Follow
                      </>
                    )}
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
};

RecommendedSHGs.propTypes = {
  limit: PropTypes.number
};

export default RecommendedSHGs;
