const express = require('express');
const requestLogger = require('./middleware/requestLogger');
const authRoutes = require('./routes/auth');
const productRoutes = require('./routes/products');
const orderRoutes = require('./routes/orders');
const logger = require('./utils/logger');

const app = express();

const path = require('path');

app.use(express.json());
app.use(requestLogger);

// Root endpoint serves the API tester dashboard
app.get('/', (req, res) => {
  logger.info('Root endpoint accessed (Dashboard loaded)', req);
  res.sendFile(path.join(__dirname, 'public/index.html'));
});

// Health check endpoint
app.get('/health', (req, res) => {
  logger.info('Health check passed', req);
  res.status(200).json({ status: 'UP' });
});

// Metrics endpoint (placeholder for real metrics if needed)
app.get('/metrics', (req, res) => {
  logger.info('Metrics retrieved', req);
  res.status(200).json({ metrics: 'placeholder' });
});

// Routes
app.use('/', authRoutes);
app.use('/products', productRoutes);
app.use('/order', orderRoutes);

module.exports = app;
