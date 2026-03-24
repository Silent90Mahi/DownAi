import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { productsAPI } from '../services/api';

const ProductContext = createContext(null);

export const ProductProvider = ({ children }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchProducts = useCallback(async (status = 'Available') => {
    try {
      setLoading(true);
      setError(null);
      const response = await productsAPI.getAll(status).catch(() => ({ data: [] }));
      setProducts(response.data || []);
    } catch (err) {
      setError(err.message);
      setProducts([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const addProduct = useCallback((product) => {
    setProducts(prev => [product, ...prev]);
  }, []);

  const updateProduct = useCallback((productId, updates) => {
    setProducts(prev => prev.map(p => 
      p.id === productId ? { ...p, ...updates } : p
    ));
  }, []);

  const removeProduct = useCallback((productId) => {
    setProducts(prev => prev.filter(p => p.id !== productId));
  }, []);

  const updateStock = useCallback((productId, newStock) => {
    setProducts(prev => prev.map(p => 
      p.id === productId ? { ...p, stock: newStock } : p
    ));
  }, []);

  const refreshProducts = useCallback(() => {
    fetchProducts();
  }, [fetchProducts]);

  const getProductById = useCallback((productId) => {
    return products.find(p => p.id === productId);
  }, [products]);

  const value = {
    products,
    loading,
    error,
    addProduct,
    updateProduct,
    removeProduct,
    updateStock,
    refreshProducts,
    getProductById,
    fetchProducts
  };

  return (
    <ProductContext.Provider value={value}>
      {children}
    </ProductContext.Provider>
  );
};

export const useProducts = () => {
  const context = useContext(ProductContext);
  if (!context) {
    throw new Error('useProducts must be used within a ProductProvider');
  }
  return context;
};

export default ProductContext;
