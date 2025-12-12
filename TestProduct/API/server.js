require('dotenv').config();
const express = require('express');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const { sql, getPool } = require('./db');

const app = express();

// CORS - allow Angular dev server by default
const corsOrigin = process.env.CORS_ORIGIN || 'http://localhost:4200';
app.use(cors({ origin: corsOrigin, credentials: true }));

app.use(express.json());

const PORT = process.env.PORT || 8000;
const JWT_SECRET = process.env.JWT_SECRET || 'dev_super_secret_change_me';

// -----------------------------
// Auth middleware
// -----------------------------
function authenticateToken(req, res, next) {
  const auth = req.headers['authorization'] || '';
  const token = auth.startsWith('Bearer ') ? auth.substring(7) : null;
  if (!token) return res.status(401).json({ message: 'Missing token' });

  jwt.verify(token, JWT_SECRET, (err, payload) => {
    if (err) return res.status(403).json({ message: 'Invalid or expired token' });
    req.user = payload; // { userId, username, role }
    next();
  });
}

// -----------------------------
// Helpers
// -----------------------------
function isValidSex(val) {
  return val === 'Male' || val === 'Female' || val === 'N/A';
}

// -----------------------------
// Routes
// -----------------------------
app.get(['/api/health', '/health'], (req, res) => res.json({ status: 'ok' }));

// POST /api/login and /login
async function loginHandler(req, res) {
  try {
    const { username, password } = req.body || {};
    if (!username || !password) return res.status(400).json({ message: 'Username and password are required' });

    const pool = await getPool();
    const result = await pool
      .request()
      .input('username', sql.VarChar(100), username)
      .query('SELECT TOP 1 UserID, Username, PasswordHash, Role FROM Users WHERE Username = @username');

    const row = result.recordset?.[0];
    if (!row) return res.status(401).json({ message: 'Invalid credentials' });

    const isMatch = await bcrypt.compare(password, row.PasswordHash);
    if (!isMatch) return res.status(401).json({ message: 'Invalid credentials' });

    const payload = { userId: row.UserID, username: row.Username, role: row.Role };
    const token = jwt.sign(payload, JWT_SECRET, { expiresIn: '2h' });

    return res.json({ token, user: payload });
  } catch (err) {
    console.error('Login error:', err);
    return res.status(500).json({ message: 'Internal server error' });
  }
}
app.post(['/api/login', '/login'], loginHandler);

// GET /api/clients and /clients
async function getClientsHandler(req, res) {
  try {
    const { userId, role } = req.user || {};
    const lowerRole = (role || '').toString().toLowerCase();
    const mineOnly = req.query.mine === 'true';

    const pool = await getPool();
    if (lowerRole === 'admin' && !mineOnly) {
      const result = await pool
        .request()
        .query('SELECT ClientID, FirstName, LastName, DOB, Sex, CreatedByUserID FROM Clients ORDER BY ClientID DESC');
      return res.json(result.recordset || []);
    } else {
      const result = await pool
        .request()
        .input('userId', sql.Int, userId)
        .query(
          'SELECT ClientID, FirstName, LastName, DOB, Sex, CreatedByUserID FROM Clients WHERE CreatedByUserID = @userId ORDER BY ClientID DESC'
        );
      return res.json(result.recordset || []);
    }
  } catch (err) {
    console.error('Get clients error:', err);
    return res.status(500).json({ message: 'Internal server error' });
  }
}
app.get(['/api/clients', '/clients'], authenticateToken, getClientsHandler);

// POST /api/clients and /clients
async function createClientHandler(req, res) {
  try {
    const { userId } = req.user || {};
    const { firstName, lastName, dob, sex } = req.body || {};

    if (!firstName || !lastName || !dob || !sex)
      return res.status(400).json({ message: 'firstName, lastName, dob, and sex are required' });

    if (!isValidSex(sex)) return res.status(400).json({ message: "sex must be 'Male', 'Female', or 'N/A'" });

    const dobDate = new Date(dob);
    if (isNaN(dobDate.getTime())) return res.status(400).json({ message: 'dob must be a valid date' });

    const pool = await getPool();
    const result = await pool
      .request()
      .input('firstName', sql.VarChar(100), firstName)
      .input('lastName', sql.VarChar(100), lastName)
      .input('dob', sql.Date, dobDate)
      .input('sex', sql.VarChar(10), sex)
      .input('createdBy', sql.Int, userId)
      .query(
        `INSERT INTO Clients (FirstName, LastName, DOB, Sex, CreatedByUserID)
         OUTPUT INSERTED.ClientID, INSERTED.FirstName, INSERTED.LastName, INSERTED.DOB, INSERTED.Sex, INSERTED.CreatedByUserID
         VALUES (@firstName, @lastName, @dob, @sex, @createdBy)`
      );

    const inserted = result.recordset?.[0];
    return res.status(201).json(inserted);
  } catch (err) {
    console.error('Create client error:', err);
    return res.status(500).json({ message: 'Internal server error' });
  }
}
app.post(['/api/clients', '/clients'], authenticateToken, createClientHandler);

// -----------------------------
// Start server
// -----------------------------
app.listen(PORT, () => {
  console.log(`API listening on http://localhost:${PORT}`);
});
