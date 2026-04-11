const express = require('express');
const orderRepository = require('../repositories/orderRepository');
const logger = require('../utils/logger');

const router = express.Router();

router.post('/', async (req, res) => {
  try {
    const { userId } = req.body;
    
    if (!userId) {
      logger.warn('Order failed - missing userId', req);
      return res.status(400).json({ error: 'userId is required' });
    }

    // Simulate random payment failure
    const isPaymentFailure = Math.random() < 0.3; // 30% chance of failure
    
    if (isPaymentFailure) {
      logger.error('Payment failure processing order', req);
      return res.status(402).json({ error: 'Payment failed' });
    }

    const order = await orderRepository.create(userId, 'COMPLETED');
    logger.info('Order placed successfully', req);
    
    res.status(201).json(order);
  } catch (error) {
    logger.error('Error processing order: ' + error.message, req);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
