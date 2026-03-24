import { useState, useEffect, useCallback } from 'react';
import { Lightbulb, X, TrendingUp, Package, Users, DollarSign, RefreshCw } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const SUGGESTION_ICONS = {
  listing: Package,
  pricing: DollarSign,
  buyer: Users,
  trend: TrendingUp,
  default: Lightbulb,
};

const SUGGESTION_COLORS = {
  listing: 'border-blue-200 bg-blue-50',
  pricing: 'border-green-200 bg-green-50',
  buyer: 'border-purple-200 bg-purple-50',
  trend: 'border-orange-200 bg-orange-50',
  default: 'border-gray-200 bg-gray-50',
};

const MOCK_SUGGESTIONS = [
  { id: 1, type: 'listing', title: 'List more products', message: 'You have 3 draft products ready to publish. Listing them could increase your visibility by 40%.', priority: 'high' },
  { id: 2, type: 'pricing', title: 'Price update recommended', message: 'Market prices for "Handwoven Cotton Fabric" have increased 12%. Consider updating your listing price.', priority: 'medium' },
  { id: 3, type: 'buyer', title: 'New buyer match', message: '3 new buyers are looking for products in your category. Check your matches now!', priority: 'high' },
  { id: 4, type: 'trend', title: 'Trending opportunity', message: 'Demand for eco-friendly products is up 25% in your district. Consider adding sustainability tags.', priority: 'low' },
  { id: 5, type: 'listing', title: 'Restock alert', message: 'Your top-selling item "Organic Turmeric" is running low. Restock to maintain your seller ranking.', priority: 'high' },
];

const AISuggestionsPanel = ({ userId, limit = 5 }) => {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dismissed, setDismissed] = useState(new Set());
  const { user } = useAuth();

  const fetchSuggestions = useCallback(async () => {
    setLoading(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 800));
      const userSuggestions = MOCK_SUGGESTIONS.filter(
        (s) => !dismissed.has(s.id)
      ).slice(0, limit);
      setSuggestions(userSuggestions);
    } catch (error) {
      console.error('Failed to fetch AI suggestions:', error);
    } finally {
      setLoading(false);
    }
  }, [limit, dismissed]);

  useEffect(() => {
    fetchSuggestions();
    const interval = setInterval(fetchSuggestions, 60000);
    return () => clearInterval(interval);
  }, [fetchSuggestions]);

  const dismissSuggestion = (suggestionId) => {
    setDismissed((prev) => new Set([...prev, suggestionId]));
    setSuggestions((prev) => prev.filter((s) => s.id !== suggestionId));
  };

  const getPriorityIndicator = (priority) => {
    switch (priority) {
      case 'high':
        return 'bg-red-500';
      case 'medium':
        return 'bg-yellow-500';
      case 'low':
        return 'bg-green-500';
      default:
        return 'bg-gray-500';
    }
  };

  const visibleSuggestions = suggestions.filter((s) => !dismissed.has(s.id));

  if (loading && suggestions.length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow-[0_4px_20px_rgb(0,0,0,0.03)] border border-gray-100 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Lightbulb className="w-5 h-5 text-[#FF9933]" />
          <h3 className="font-bold text-gray-800">AI Suggestions</h3>
        </div>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-100 rounded w-full"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (visibleSuggestions.length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow-[0_4px_20px_rgb(0,0,0,0.03)] border border-gray-100 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Lightbulb className="w-5 h-5 text-[#FF9933]" />
          <h3 className="font-bold text-gray-800">AI Suggestions</h3>
        </div>
        <div className="text-center py-6">
          <Lightbulb className="w-12 h-12 mx-auto text-gray-300 mb-2" />
          <p className="text-gray-400 text-sm">All caught up! Check back later for new suggestions.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-[0_4px_20px_rgb(0,0,0,0.03)] border border-gray-100 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-[#FF9933]" />
          <h3 className="font-bold text-gray-800">AI Suggestions</h3>
          <span className="px-2 py-0.5 bg-[#FF9933]/10 text-[#FF9933] text-xs font-semibold rounded-full">
            {visibleSuggestions.length}
          </span>
        </div>
        <button
          onClick={fetchSuggestions}
          disabled={loading}
          className="p-1.5 hover:bg-gray-100 rounded-full transition disabled:opacity-50"
          title="Refresh suggestions"
        >
          <RefreshCw className={`w-4 h-4 text-gray-500 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      <div className="space-y-3">
        {visibleSuggestions.map((suggestion) => {
          const Icon = SUGGESTION_ICONS[suggestion.type] || SUGGESTION_ICONS.default;
          const colorClass = SUGGESTION_COLORS[suggestion.type] || SUGGESTION_COLORS.default;

          return (
            <div
              key={suggestion.id}
              className={`relative p-4 rounded-xl border ${colorClass} transition-all duration-200 hover:shadow-md group`}
            >
              <button
                onClick={() => dismissSuggestion(suggestion.id)}
                className="absolute top-2 right-2 p-1 opacity-0 group-hover:opacity-100 hover:bg-white/50 rounded-full transition-all"
                title="Dismiss"
              >
                <X className="w-4 h-4 text-gray-500" />
              </button>

              <div className="flex items-start gap-3">
                <div className="p-2 bg-white rounded-lg shadow-sm">
                  <Icon className="w-4 h-4 text-gray-600" />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`w-2 h-2 rounded-full ${getPriorityIndicator(suggestion.priority)}`} />
                    <h4 className="font-semibold text-sm text-gray-800">{suggestion.title}</h4>
                  </div>
                  <p className="text-xs text-gray-600 leading-relaxed">{suggestion.message}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default AISuggestionsPanel;
