const db = require('../config/db');

class UserRepository {
  async findByUsername(username) {
    const result = await db.query('SELECT * FROM users WHERE username = $1', [username]);
    return result.rows[0];
  }

  async create(username, password) {
    const result = await db.query(
      'INSERT INTO users (username, password) VALUES ($1, $2) RETURNING id, username, created_at',
      [username, password]
    );
    return result.rows[0];
  }
}

module.exports = new UserRepository();
