import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { productsAPI, marketAPI } from '../services/api';
import { UploadCloud, Mic, Loader2, ArrowLeft, Save } from 'lucide-react';

const ProductEdit = () => {
  const { productId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [marketAnalysis, setMarketAnalysis] = useState(null);
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: 'Handicrafts',
    quantity: '',
    unit: 'pcs',
    price: '',
    district: user?.district || 'Hyderabad'
  });

  useEffect(() => {
    fetchProduct();
  }, [productId]);

  const fetchProduct = async () => {
    try {
      setLoading(true);
      const response = await productsAPI.getById(productId);
      const product = response.data;

      // Check if user owns this product
      if (product.seller_id !== user?.id) {
        alert('You can only edit your own products');
        navigate('/marketplace');
        return;
      }

      setFormData({
        name: product.name || '',
        description: product.description || '',
        category: product.category || 'Handicrafts',
        quantity: product.quantity?.toString() || '',
        unit: product.unit || 'pcs',
        price: product.price?.toString() || '',
        district: product.district || user?.district || 'Hyderabad'
      });

      if (product.image_url) {
        setPreview(product.image_url);
      }
    } catch (error) {
      alert('Failed to load product: ' + (error.response?.data?.detail || 'Unknown error'));
      navigate('/marketplace');
    } finally {
      setLoading(false);
    }
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      setPreview(URL.createObjectURL(file));
    }
  };

  const handleVoiceInput = async () => {
    alert('Voice input: Recording for 5 seconds...');
    try {
      // Mock voice input
      setFormData(prev => ({
        ...prev,
        description: 'Handwoven organic cotton product with traditional patterns.',
      }));
    } catch (error) {
      console.error('Voice transcription failed:', error);
    }
  };

  const handlePredictDemand = async () => {
    if (!formData.name) {
      alert('Please enter a product name first');
      return;
    }

    try {
      setAnalyzing(true);
      const response = await marketAPI.analyze(
        formData.name,
        formData.category,
        formData.district,
        formData.price ? parseFloat(formData.price) : null
      );
      setMarketAnalysis(response.data);
      if (response.data.recommended_price_min) {
        const avgPrice = Math.round((response.data.recommended_price_min + (response.data.recommended_price_max || response.data.recommended_price_min)) / 2);
        setFormData(prev => ({ ...prev, price: avgPrice.toString() }));
      }
    } catch (error) {
      console.error('Market analysis failed:', error);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate all required fields
    if (!formData.name?.trim()) {
      alert('Please enter a product name');
      return;
    }
    if (!formData.category) {
      alert('Please select a category');
      return;
    }
    if (!formData.quantity || parseInt(formData.quantity) <= 0) {
      alert('Please enter a valid quantity (must be greater than 0)');
      return;
    }
    if (!formData.price || parseFloat(formData.price) <= 0) {
      alert('Please enter a valid price (must be greater than 0)');
      return;
    }

    try {
      setSaving(true);
      const productData = new FormData();
      productData.append('name', formData.name.trim());
      productData.append('description', formData.description?.trim() || '');
      productData.append('category', formData.category);
      productData.append('quantity', parseInt(formData.quantity));
      productData.append('unit', formData.unit);
      productData.append('price', parseFloat(formData.price));
      productData.append('district', formData.district);

      // Only append image if a new one is selected
      if (image instanceof File) {
        productData.append('image', image);
      }

      console.log('Updating product - FormData entries:', Array.from(productData.entries()));

      await productsAPI.update(productId, productData);
      alert('Product updated successfully!');
      navigate(`/products/${productId}`);
    } catch (error) {
      console.error('Failed to update product:', error);
      console.error('Error response:', error.response?.data);
      const errorMsg = error.response?.data?.detail || 'Unknown error';
      if (Array.isArray(errorMsg)) {
        alert('Failed to update product:\n' + errorMsg.map(e => `- ${e.msg}: ${e.loc?.join('.') || 'field'}`).join('\n'));
      } else {
        alert('Failed to update product: ' + errorMsg);
      }
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-pulse text-gray-400">Loading product...</div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-8 animate-fade-in pb-12">
      <div className="flex items-center space-x-6">
        <button
          onClick={() => navigate(`/products/${productId}`)}
          className="text-gray-600 hover:text-black font-bold px-6 py-3 bg-white rounded-2xl shadow-sm hover:shadow-md transition-all flex items-center"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back
        </button>
        <h1 className="text-3xl font-extrabold text-[#333] tracking-tight">Edit Product</h1>
      </div>

      <div className="bg-white p-8 md:p-10 rounded-[2rem] shadow-sm border border-gray-100">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Image Upload */}
          <div className="border-2 border-dashed border-gray-200 rounded-2xl p-8 flex flex-col items-center justify-center text-gray-500 bg-gray-50 hover:bg-gray-100 transition cursor-pointer relative">
            {preview ? (
              <img src={preview} alt="Preview" className="w-full h-48 object-cover rounded-xl" />
            ) : (
              <>
                <UploadCloud size={48} className="text-[#FF9933] mb-4" />
                <p className="font-bold">Upload Product Photo</p>
                <p className="text-sm mt-1">Tap to browse files</p>
              </>
            )}
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="absolute inset-0 opacity-0 cursor-pointer"
            />
          </div>

          {/* Product Name */}
          <div>
            <label className="block text-sm font-bold text-gray-700 uppercase tracking-widest mb-2">Product Name</label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={e => setFormData(prev => ({ ...prev, name: e.target.value }))}
              className="w-full px-5 py-4 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#000080] focus:border-transparent outline-none font-medium"
              placeholder="Product Name"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-bold text-gray-700 uppercase tracking-widest mb-2">Description</label>
            <div className="relative">
              <textarea
                rows="3"
                value={formData.description}
                onChange={e => setFormData(prev => ({ ...prev, description: e.target.value }))}
                className="w-full px-5 py-4 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#000080] focus:border-transparent outline-none font-medium resize-none pr-16"
                placeholder="Describe your product (or use voice)"
              ></textarea>
              <button
                type="button"
                onClick={handleVoiceInput}
                className="absolute bottom-4 right-4 p-3 bg-blue-100 text-[#000080] rounded-full hover:bg-[#000080] hover:text-white transition"
                title="Agent Vaani Input"
              >
                <Mic size={20} />
              </button>
            </div>
          </div>

          {/* Category & District */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-bold text-gray-700 uppercase tracking-widest mb-2">Category</label>
              <select
                value={formData.category}
                onChange={e => setFormData(prev => ({ ...prev, category: e.target.value }))}
                className="w-full px-5 py-4 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#000080] focus:border-transparent outline-none font-medium"
              >
                <option>Handicrafts</option>
                <option>Textiles</option>
                <option>Food Products</option>
                <option>Organic Products</option>
                <option>Personal Care</option>
                <option>Home Decor</option>
                <option>Agro Products</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-bold text-gray-700 uppercase tracking-widest mb-2">District</label>
              <input
                type="text"
                value={formData.district}
                onChange={e => setFormData(prev => ({ ...prev, district: e.target.value }))}
                className="w-full px-5 py-4 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#000080] focus:border-transparent outline-none font-medium"
                placeholder="Your district"
              />
            </div>
          </div>

          {/* Quantity, Unit, Price */}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-bold text-gray-700 uppercase tracking-widest mb-2">Quantity</label>
              <input
                type="number"
                required
                value={formData.quantity}
                onChange={e => setFormData(prev => ({ ...prev, quantity: e.target.value }))}
                className="w-full px-5 py-4 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#000080] focus:border-transparent outline-none font-medium"
                placeholder="100"
              />
            </div>
            <div>
              <label className="block text-sm font-bold text-gray-700 uppercase tracking-widest mb-2">Unit</label>
              <select
                value={formData.unit}
                onChange={e => setFormData(prev => ({ ...prev, unit: e.target.value }))}
                className="w-full px-5 py-4 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#000080] focus:border-transparent outline-none font-medium"
              >
                <option value="pcs">Pcs</option>
                <option value="kg">Kg</option>
                <option value="g">Grams</option>
                <option value="l">Liters</option>
                <option value="ml">ml</option>
                <option value="meters">Meters</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-bold text-gray-700 uppercase tracking-widest mb-2 flex justify-between items-center">
                <span>Price (₹)</span>
                {analyzing ? (
                  <Loader2 size={14} className="animate-spin text-[#FF9933]" />
                ) : (
                  <button type="button" onClick={handlePredictDemand} className="text-[#FF9933] flex items-center text-xs bg-orange-50 px-2 py-1 rounded-full cursor-pointer hover:bg-orange-100">
                    AI Price
                  </button>
                )}
              </label>
              <input
                type="number"
                required
                value={formData.price}
                onChange={e => setFormData(prev => ({ ...prev, price: e.target.value }))}
                className="w-full px-5 py-4 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#000080] focus:border-transparent outline-none font-medium"
                placeholder="3500"
              />
            </div>
          </div>

          {/* Market Analysis */}
          {marketAnalysis && (
            <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
              <p className="text-sm font-semibold text-blue-900 mb-2">🤖 Agent Bazaar Buddhi Analysis:</p>
              <p className="text-sm text-blue-800">Demand Level: <strong>{marketAnalysis.demand_level}</strong> (Score: {marketAnalysis.demand_score}/100)</p>
              {marketAnalysis.recommended_price_min && (
                <p className="text-sm text-blue-800">Recommended Price: ₹{marketAnalysis.recommended_price_min} - ₹{marketAnalysis.recommended_price_max}</p>
              )}
              {marketAnalysis.suggestions && (
                <p className="text-xs text-blue-700 mt-2">{marketAnalysis.suggestions[0]}</p>
              )}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={saving}
            className="w-full py-5 bg-[#138808] text-white rounded-2xl font-black text-xl hover:bg-green-700 shadow-xl shadow-green-900/20 transform transition hover:-translate-y-1 mt-6 flex justify-center items-center disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? (
              <>Saving Changes...</>
            ) : (
              <>
                <Save className="w-5 h-5 mr-2" />
                Save Changes
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ProductEdit;
