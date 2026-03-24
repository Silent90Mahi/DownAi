import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { productsAPI, ordersAPI } from '../services/api';
import { ArrowLeft, Package, MapPin, Phone, User, ShoppingCart, Edit, Trash2, IndianRupee } from 'lucide-react';

const ProductDetail = () => {
  const { productId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [ordering, setOrdering] = useState(false);
  const [quantity, setQuantity] = useState(1);

  useEffect(() => {
    fetchProduct();
  }, [productId]);

  const fetchProduct = async () => {
    try {
      setLoading(true);
      const response = await productsAPI.getById(productId);
      setProduct(response.data);
    } catch (error) {
      console.error('Failed to fetch product:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOrder = async () => {
    try {
      setOrdering(true);
      const orderData = {
        items: [{
          product_id: product.id,
          product_name: product.name,
          quantity: quantity,
          unit_price: product.price,
          total_price: product.price * quantity
        }],
        delivery_name: user?.name || '',
        delivery_phone: user?.phone || '',
        delivery_address: user?.address || '',
        delivery_city: user?.district || '',
        delivery_district: user?.district || '',
        delivery_pincode: user?.pincode || '500001',
        payment_method: 'UPI'
      };

      const response = await ordersAPI.create(orderData);
      alert('Order placed successfully!');
      navigate(`/orders/${response.data.id}`);
    } catch (error) {
      alert('Failed to place order: ' + (error.response?.data?.detail || 'Unknown error'));
    } finally {
      setOrdering(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this product?')) return;

    try {
      await productsAPI.delete(productId);
      alert('Product deleted successfully');
      navigate('/my-products');
    } catch (error) {
      alert('Failed to delete product: ' + (error.response?.data?.detail || 'Unknown error'));
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-pulse text-gray-400">Loading product details...</div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="text-center py-20">
        <p className="text-xl font-semibold text-gray-400">Product not found</p>
        <button onClick={() => navigate('/marketplace')} className="mt-4 text-[#FF9933] font-semibold">
          Back to Marketplace
        </button>
      </div>
    );
  }

  const isOwner = product.seller_id === user?.id;
  const totalPrice = product.price * quantity;

  return (
    <div className="space-y-8">
      {/* Back Button */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-gray-600 hover:text-[#FF9933] font-medium transition"
      >
        <ArrowLeft className="w-5 h-5" />
        Back
      </button>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Product Image */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          {product.image_url ? (
            <img
              src={product.image_url}
              alt={product.name}
              className="w-full h-96 object-cover rounded-xl"
            />
          ) : (
            <div className="w-full h-96 bg-gradient-to-br from-[#FF9933]/20 to-[#138808]/20 rounded-xl flex items-center justify-center">
              <Package className="w-24 h-24 text-[#FF9933]/50" />
            </div>
          )}
        </div>

        {/* Product Info */}
        <div className="space-y-6">
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-start justify-between mb-4">
              <span className="px-3 py-1 bg-[#FF9933]/10 text-[#FF9933] rounded-full text-xs font-bold uppercase tracking-wider">
                {product.category}
              </span>
              {isOwner && (
                <div className="flex gap-2">
                  <button
                    onClick={() => navigate(`/products/${product.id}/edit`)}
                    className="p-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={handleDelete}
                    className="p-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>

            <h1 className="text-3xl font-extrabold text-[#333333] mb-2">{product.name}</h1>
            <p className="text-gray-600 mb-6">{product.description || 'No description available'}</p>

            <div className="flex items-baseline gap-3 mb-6">
              <span className="text-4xl font-black text-[#138808]">₹{product.price?.toLocaleString()}</span>
              <span className="text-gray-500">per {product.unit}</span>
            </div>

            {/* Stock Info */}
            <div className="grid grid-cols-2 gap-4 pb-6 border-b border-gray-100">
              <div>
                <p className="text-sm text-gray-500">Available Stock</p>
                <p className="text-lg font-bold text-gray-800">{product.quantity} {product.unit}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Status</p>
                <p className={`text-lg font-bold ${product.status === 'Available' ? 'text-green-600' : 'text-red-600'}`}>
                  {product.status}
                </p>
              </div>
            </div>

            {/* Quantity Selector */}
            {!isOwner && product.status === 'Available' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Quantity</label>
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => setQuantity(Math.max(1, quantity - 1))}
                      className="w-10 h-10 bg-gray-100 rounded-lg font-bold hover:bg-gray-200 transition"
                    >
                      -
                    </button>
                    <input
                      type="number"
                      value={quantity}
                      onChange={(e) => setQuantity(Math.max(1, Math.min(product.quantity, parseInt(e.target.value) || 1)))}
                      className="w-20 h-10 text-center border border-gray-300 rounded-lg font-bold"
                    />
                    <button
                      onClick={() => setQuantity(Math.min(product.quantity, quantity + 1))}
                      className="w-10 h-10 bg-gray-100 rounded-lg font-bold hover:bg-gray-200 transition"
                    >
                      +
                    </button>
                    <span className="text-gray-500 text-sm ml-2">{product.unit}</span>
                  </div>
                </div>

                {/* Total Price */}
                <div className="bg-gray-50 rounded-xl p-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Total Amount:</span>
                    <span className="text-2xl font-bold text-[#138808]">₹{totalPrice.toLocaleString()}</span>
                  </div>
                </div>

                {/* Order Button */}
                <button
                  onClick={handleOrder}
                  disabled={ordering}
                  className="w-full py-4 bg-[#138808] text-white rounded-xl font-bold text-lg hover:bg-[#0e6e06] transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  <ShoppingCart className="w-5 h-5" />
                  {ordering ? 'Processing...' : 'Place Order'}
                </button>
              </div>
            )}
          </div>

          {/* Seller Info */}
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <h2 className="text-lg font-bold text-[#333333] mb-4">Seller Information</h2>
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <User className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500">Seller</p>
                  <p className="font-semibold text-gray-800">{product.seller_name || 'SHG Member'}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <MapPin className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500">Location</p>
                  <p className="font-semibold text-gray-800">{product.district || 'Andhra Pradesh'}</p>
                </div>
              </div>
              {!isOwner && (
                <div className="flex items-center gap-3">
                  <Phone className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-sm text-gray-500">Contact</p>
                    <p className="font-semibold text-gray-800">Available after order confirmation</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetail;
