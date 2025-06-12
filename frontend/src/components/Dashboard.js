import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Tab,
  Tabs
} from '@mui/material';
import {
  Security,
  People,
  AttachMoney,
  Warning,
  TrendingUp,
  Refresh,
  PlayArrow
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar
} from 'recharts';
import axios from 'axios';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tabValue, setTabValue] = useState(0);
  const [refreshing, setRefreshing] = useState(false);

  const fetchDashboardData = async () => {
    try {
      setRefreshing(true);
      const response = await axios.get('/api/admin/dashboard');
      setDashboardData(response.data);
      setError('');
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const generateDemoData = async () => {
    try {
      setRefreshing(true);
      await axios.post('/api/demo/generate-data');
      await fetchDashboardData();
      setError('');
    } catch (err) {
      setError('Failed to generate demo data');
      console.error('Demo data error:', err);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const getRiskColor = (level) => {
    switch (level) {
      case 'low': return '#4caf50';
      case 'medium': return '#ff9800';
      case 'high': return '#f44336';
      default: return '#9e9e9e';
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  const riskDistributionData = dashboardData?.risk_distribution ? [
    { name: 'Low Risk', value: dashboardData.risk_distribution.low, color: '#4caf50' },
    { name: 'Medium Risk', value: dashboardData.risk_distribution.medium, color: '#ff9800' },
    { name: 'High Risk', value: dashboardData.risk_distribution.high, color: '#f44336' }
  ] : [];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          TrustAI Admin Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={fetchDashboardData}
            disabled={refreshing}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<PlayArrow />}
            onClick={generateDemoData}
            disabled={refreshing}
          >
            Generate Demo Data
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {dashboardData && (
        <>
          {/* Key Metrics */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <People sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                    <Box>
                      <Typography color="textSecondary" gutterBottom>
                        Total Users
                      </Typography>
                      <Typography variant="h4">
                        {dashboardData.total_users}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <AttachMoney sx={{ fontSize: 40, color: 'success.main', mr: 2 }} />
                    <Box>
                      <Typography color="textSecondary" gutterBottom>
                        Total Transactions
                      </Typography>
                      <Typography variant="h4">
                        {dashboardData.total_transactions}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Warning sx={{ fontSize: 40, color: 'error.main', mr: 2 }} />
                    <Box>
                      <Typography color="textSecondary" gutterBottom>
                        Fraud Detected
                      </Typography>
                      <Typography variant="h4">
                        {dashboardData.fraud_detected}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Security sx={{ fontSize: 40, color: 'info.main', mr: 2 }} />
                    <Box>
                      <Typography color="textSecondary" gutterBottom>
                        Avg Trust Score
                      </Typography>
                      <Typography variant="h4">
                        {dashboardData.avg_trust_score}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Charts and Analytics */}
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
            <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
              <Tab label="Risk Distribution" />
              <Tab label="Activity Timeline" />
              <Tab label="Recent Alerts" />
            </Tabs>
          </Box>

          {tabValue === 0 && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Risk Level Distribution (Last 7 Days)
                    </Typography>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={riskDistributionData}
                          cx="50%"
                          cy="50%"
                          outerRadius={80}
                          dataKey="value"
                          label={({ name, value }) => `${name}: ${value}`}
                        >
                          {riskDistributionData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Hourly Activity (Last 24 Hours)
                    </Typography>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={dashboardData.hourly_activity}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="hour" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="total_activities" fill="#1976d2" />
                        <Bar dataKey="high_risk" fill="#f44336" />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}

          {tabValue === 1 && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Trust Score Timeline
                </Typography>
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={dashboardData.hourly_activity}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="hour" />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="avg_trust_score"
                      stroke="#1976d2"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}

          {tabValue === 2 && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Security Alerts
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>User</TableCell>
                        <TableCell>Action</TableCell>
                        <TableCell>Risk Level</TableCell>
                        <TableCell>Trust Score</TableCell>
                        <TableCell>Decision</TableCell>
                        <TableCell>Timestamp</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {dashboardData.recent_alerts?.slice(0, 10).map((alert, index) => (
                        <TableRow key={index}>
                          <TableCell>{alert.username}</TableCell>
                          <TableCell>{alert.action_type}</TableCell>
                          <TableCell>
                            <Chip
                              label={alert.risk_level}
                              color={
                                alert.risk_level === 'high' ? 'error' :
                                alert.risk_level === 'medium' ? 'warning' : 'success'
                              }
                              size="small"
                            />
                          </TableCell>
                          <TableCell>{alert.trust_score.toFixed(1)}</TableCell>
                          <TableCell>{alert.decision}</TableCell>
                          <TableCell>{formatTimestamp(alert.timestamp)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </Box>
  );
};

export default Dashboard;
