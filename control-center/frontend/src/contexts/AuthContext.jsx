import React, { createContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:54112/api/auth';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load user from localStorage on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const storedUser = localStorage.getItem('user');

    if (token && storedUser) {
      try {
        setUser(JSON.parse(storedUser));
        // Verify token is still valid
        fetchCurrentUser(token).catch(() => {
          // Token invalid, clear storage
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          setUser(null);
        });
      } catch (err) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const fetchCurrentUser = async (token) => {
    const response = await axios.get(`${API_URL}/me`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  };

  const login = useCallback(async (username, password) => {
    setError(null);
    setLoading(true);

    try {
      // Send JSON as backend expects LoginRequest model
      const response = await axios.post(`${API_URL}/login`, {
        username,
        password,
      }, {
        headers: { 'Content-Type': 'application/json' }
      });

      const { access_token } = response.data;

      // Store token
      localStorage.setItem('access_token', access_token);

      // Fetch user data using the token
      const userData = await fetchCurrentUser(access_token);
      localStorage.setItem('user', JSON.stringify(userData));

      setUser(userData);
      setLoading(false);

      return { success: true };
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Login failed';
      setError(errorMessage);
      setLoading(false);
      return { success: false, error: errorMessage };
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setUser(null);
  }, []);

  const value = {
    user,
    loading,
    error,
    login,
    logout,
    isAuthenticated: !!user,
    token: localStorage.getItem('access_token'),
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthProvider;
