const express = require('express');
const bcrypt = require('bcryptjs');
const userRepository = require('../repositories/userRepository');
const logger = require('../utils/logger');

const router = express.Router();

router.post('/signup', async (req, res) => {
  try {
    const { username, password } = req.body;
    if (!username || !password) {
      logger.warn('Signup failed - missing fields', req);
      return res.status(400).json({ error: 'Username and password required' });
    }

    const existingUser = await userRepository.findByUsername(username);
    if (existingUser) {
      logger.warn('Signup failed - username exists', req);
      return res.status(409).json({ error: 'Username already exists' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const user = await userRepository.create(username, hashedPassword);

    logger.info('User signed up successfully', req);
    res.status(201).json(user);
  } catch (error) {
    logger.error('Error during signup: ' + error.message, req);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    const user = await userRepository.findByUsername(username);

    if (!user) {
      logger.warn('Invalid login - user not found', req);
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const isValid = await bcrypt.compare(password, user.password);
    if (!isValid) {
      logger.warn('Invalid login - incorrect password', req);
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    logger.info('User logged in successfully', req);
    res.json({ message: 'Login successful', userId: user.id });
  } catch (error) {
    logger.error('Error during login: ' + error.message, req);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
