import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    const loadUser = async () => {
      const storedToken = localStorage.getItem('token');
      if (storedToken) {
        try {
          const response = await authAPI.getProfile();
          setUser(response.data);
          setToken(storedToken);
        } catch (error) {
          localStorage.removeItem('token');
          setToken(null);
        }
      }
      setLoading(false);
    };

    loadUser();
  }, []);

  const login = async (phone, password) => {
    const response = await authAPI.login(phone, password);
    const newToken = response.data.access_token;

    localStorage.setItem('token', newToken);
    setToken(newToken);

    // Fetch user profile
    const profileResponse = await authAPI.getProfile();
    setUser(profileResponse.data);

    return profileResponse.data;
  };

  const register = async (userData) => {
    const response = await authAPI.register(userData);
    setUser(response.data);
    return response.data;
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  const updateUser = async (updates) => {
    const response = await authAPI.updateProfile(updates);
    setUser(response.data);
    return response.data;
  };

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    updateUser,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'Admin' || user?.role === 'DPD',
    isSHG: user?.role === 'SHG',
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
