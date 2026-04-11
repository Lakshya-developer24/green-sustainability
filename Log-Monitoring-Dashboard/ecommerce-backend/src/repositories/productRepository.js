const db = require('../config/db');

class ProductRepository {
  async findAll() {
    const result = await db.query('SELECT * FROM products');
    return result.rows;
  }
}

module.exports = new ProductRepository();
