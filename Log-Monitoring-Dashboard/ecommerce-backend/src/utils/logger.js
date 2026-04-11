const logger = {
  log: (level, message, req = null) => {
    const logEntry = {
      timestamp: new Date().toISOString(),
      level: level,
      service: 'ecommerce-backend',
      endpoint: req && req.originalUrl ? req.originalUrl : 'system',
      message: message,
    };

    if (req && req.startTime) {
      logEntry.response_time = Date.now() - req.startTime;
    }

    console.log(JSON.stringify(logEntry));
  },
  info: (message, req) => logger.log('INFO', message, req),
  warn: (message, req) => logger.log('WARN', message, req),
  error: (message, req) => logger.log('ERROR', message, req),
};

module.exports = logger;
