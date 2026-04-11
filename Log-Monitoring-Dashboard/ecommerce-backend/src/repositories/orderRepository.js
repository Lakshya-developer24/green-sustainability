const db = require('../config/db');

class OrderRepository {
  async create(userId, status) {
    const result = await db.query(
      'INSERT INTO orders (user_id, status) VALUES ($1, $2) RETURNING *',
      [userId, status]
    );
    return result.rows[0];
  }
}

module.exports = new OrderRepository();
