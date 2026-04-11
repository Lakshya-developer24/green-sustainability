const express = require('express');
const productRepository = require('../repositories/productRepository');
const logger = require('../utils/logger');

const router = express.Router();

router.get('/', async (req, res) => {
  try {
    // Add random delay to simulate slow response
    const delay = Math.floor(Math.random() * 800); // 0 to 800ms
    await new Promise(resolve => setTimeout(resolve, delay));

    const products = await productRepository.findAll();
    
    // Explicitly calculate expected response time for logging warn logic
    const currentResponseTime = Date.now() - req.startTime;
    
    if (currentResponseTime > 500) {
      logger.warn('Slow response on /products', req);
    } else {
      logger.info('Products retrieved successfully', req);
    }

    res.json(products);
  } catch (error) {
    logger.error('Error retrieving products: ' + error.message, req);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
