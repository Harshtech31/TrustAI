import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // Verify token validity by making a test request
      axios.get('/api/health')
        .then(() => {
          // Token is valid, get user info from token or make another request
          const userData = JSON.parse(localStorage.getItem('user') || '{}');
          if (userData.id) {
            setUser(userData);
          }
        })
        .catch(() => {
          // Token is invalid
          logout();
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, [token]);

  const login = async (username, password) => {
    try {
      const response = await axios.post('/api/auth/login', {
        username,
        password
      });

      const { access_token, user: userData, trust_score, risk_level, requires_mfa } = response.data;

      if (requires_mfa) {
        return {
          success: false,
          requiresMfa: true,
          mfaChallenge: response.data.mfa_challenge,
          message: 'Multi-factor authentication required'
        };
      }

      // Store token and user data
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      
      setToken(access_token);
      setUser(userData);
      
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

      return {
        success: true,
        trustScore: trust_score,
        riskLevel: risk_level
      };
    } catch (error) {
      console.error('Login error:', error);
      return {
        success: false,
        message: error.response?.data?.error || 'Login failed'
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  const verifyMfa = async (challengeId, code) => {
    try {
      const response = await axios.post('/api/auth/verify-mfa', {
        challenge_id: challengeId,
        code
      });

      const { access_token, user: userData } = response.data;

      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      
      setToken(access_token);
      setUser(userData);
      
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

      return { success: true };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.error || 'MFA verification failed'
      };
    }
  };

  const value = {
    user,
    login,
    logout,
    verifyMfa,
    loading,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
