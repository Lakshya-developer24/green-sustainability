const requestLogger = (req, res, next) => {
  req.startTime = Date.now();
  next();
};

module.exports = requestLogger;
