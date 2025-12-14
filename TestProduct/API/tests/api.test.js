require('dotenv').config();

const request = require('supertest');
const app = require('../server');

describe('POST /login', () => {
  it('returns a token for valid credentials user1/123456', async () => {
    const res = await request(app)
      .post('/login')
      .send({ username: 'user1', password: '123456' })
      .expect(200);

    expect(res.body).toHaveProperty('token');
    expect(typeof res.body.token).toBe('string');
    expect(res.body).toHaveProperty('user');
    expect(res.body.user).toHaveProperty('username', 'user1');
  });
});
