import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box, AppBar, Toolbar, Typography, Button, Container } from '@mui/material';
import { Shield, ExitToApp } from '@mui/icons-material';

import Login from './components/Login';
import Dashboard from './components/Dashboard';
import UserDashboard from './components/UserDashboard';
import TransactionSimulator from './components/TransactionSimulator';
import { AuthProvider, useAuth } from './contexts/AuthContext';

function AppContent() {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" sx={{ backgroundColor: '#1976d2' }}>
        <Toolbar>
          <Shield sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            TrustAI - Fraud Detection System
          </Typography>
          {user && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography variant="body2">
                Welcome, {user.username}
              </Typography>
              <Button
                color="inherit"
                onClick={handleLogout}
                startIcon={<ExitToApp />}
              >
                Logout
              </Button>
            </Box>
          )}
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Routes>
          <Route
            path="/login"
            element={!user ? <Login /> : <Navigate to="/" replace />}
          />
          <Route
            path="/"
            element={
              user ? (
                user.role === 'admin' ? (
                  <Dashboard />
                ) : (
                  <UserDashboard />
                )
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/simulator"
            element={
              user ? <TransactionSimulator /> : <Navigate to="/login" replace />
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Container>
    </Box>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
