require('dotenv').config({ path: require('path').resolve(__dirname, '../.env') });
require('dotenv').config(); // also attempt to load local .env if moved later

const app = require('./src/app');
const logger = require('./src/utils/logger');

const port = process.env.PORT || 3000;

app.listen(port, () => {
    logger.info(`Server running on port ${port}`, null);
});
