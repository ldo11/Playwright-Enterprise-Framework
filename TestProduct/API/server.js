require('dotenv').config();
const express = require('express');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const store = require('./store');
const swaggerJsdoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');

const app = express();

// CORS - allow Angular dev server by default
const corsOrigin = process.env.CORS_ORIGIN || ['http://localhost:4201', 'http://127.0.0.1:4201', 'http://localhost:4200'];
app.use(cors({ origin: corsOrigin, credentials: true }));

app.use(express.json());

const swaggerOptions = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Client Management API',
      version: '0.0.1',
    },
    components: {
      securitySchemes: {
        bearerAuth: {
          type: 'http',
          scheme: 'bearer',
          bearerFormat: 'JWT',
        },
      },
      schemas: {
        User: {
          type: 'object',
          properties: {
            userId: { type: 'integer', format: 'int32' },
            username: { type: 'string' },
            role: { type: 'string' },
          },
        },
        Client: {
          type: 'object',
          properties: {
            ClientID: { type: 'integer', format: 'int32' },
            FirstName: { type: 'string' },
            LastName: { type: 'string' },
            DOB: { type: 'string', format: 'date' },
<<<<<<< HEAD
            Sex: { type: 'string', enum: ['Male', 'Female', 'N/A'] },
=======
            Sex: { type: 'string', enum: ['Male', 'Female'] },
>>>>>>> Add_Failed_test
            CreatedByUserID: { type: 'integer', format: 'int32' },
          },
        },
        Error: {
          type: 'object',
          properties: {
            message: { type: 'string' },
          },
        },
      },
    },
    security: [
      {
        bearerAuth: [],
      },
    ],
    paths: {
      '/api/health': {
        get: {
          summary: 'Health check',
          responses: {
<<<<<<< HEAD
            200: {
              description: 'API is healthy',
            },
=======
            200: { description: 'API is healthy' },
>>>>>>> Add_Failed_test
          },
        },
      },
      '/login': {
        post: {
          summary: 'Authenticate and obtain JWT token',
          requestBody: {
            required: true,
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    username: { type: 'string' },
                    password: { type: 'string', format: 'password' },
                  },
                  required: ['username', 'password'],
                },
<<<<<<< HEAD
                example: {
                  username: 'user1',
                  password: '123456',
                },
=======
                example: { username: 'user1', password: '123456' },
>>>>>>> Add_Failed_test
              },
            },
          },
          responses: {
            200: {
              description: 'Login successful',
              content: {
                'application/json': {
                  schema: {
                    type: 'object',
                    properties: {
                      token: { type: 'string' },
                      user: { $ref: '#/components/schemas/User' },
                    },
                  },
                },
              },
            },
            400: {
              description: 'Missing username or password',
<<<<<<< HEAD
              content: {
                'application/json': {
                  schema: { $ref: '#/components/schemas/Error' },
                },
              },
            },
            401: {
              description: 'Invalid credentials',
              content: {
                'application/json': {
                  schema: { $ref: '#/components/schemas/Error' },
                },
              },
=======
              content: { 'application/json': { schema: { $ref: '#/components/schemas/Error' } } },
            },
            401: {
              description: 'Invalid credentials',
              content: { 'application/json': { schema: { $ref: '#/components/schemas/Error' } } },
>>>>>>> Add_Failed_test
            },
          },
        },
      },
      '/clients': {
        get: {
          summary: 'Get clients',
<<<<<<< HEAD
          description:
            'Admin users get all clients. Non-admin users get only their own. Use ?mine=true to force own clients.',
          parameters: [
            {
              name: 'mine',
              in: 'query',
              required: false,
              schema: { type: 'boolean' },
              description: 'If true, return only clients created by the current user.',
            },
          ],
          security: [
            {
              bearerAuth: [],
            },
          ],
          responses: {
            200: {
              description: 'List of clients',
              content: {
                'application/json': {
                  schema: {
                    type: 'array',
                    items: { $ref: '#/components/schemas/Client' },
                  },
                },
              },
            },
            401: {
              description: 'Missing token',
              content: {
                'application/json': {
                  schema: { $ref: '#/components/schemas/Error' },
                },
              },
            },
            403: {
              description: 'Invalid or expired token',
              content: {
                'application/json': {
                  schema: { $ref: '#/components/schemas/Error' },
                },
              },
            },
=======
          description: 'Admin users get all clients. Non-admin users get only their own. Use ?mine=true to force own clients.',
          parameters: [
            { name: 'mine', in: 'query', required: false, schema: { type: 'boolean' }, description: 'If true, return only clients created by the current user.' },
          ],
          security: [{ bearerAuth: [] }],
          responses: {
            200: { description: 'List of clients', content: { 'application/json': { schema: { type: 'array', items: { $ref: '#/components/schemas/Client' } } } } },
            401: { description: 'Missing token', content: { 'application/json': { schema: { $ref: '#/components/schemas/Error' } } } },
            403: { description: 'Invalid or expired token', content: { 'application/json': { schema: { $ref: '#/components/schemas/Error' } } } },
>>>>>>> Add_Failed_test
          },
        },
        post: {
          summary: 'Create a new client',
<<<<<<< HEAD
          security: [
            {
              bearerAuth: [],
            },
          ],
=======
          security: [{ bearerAuth: [] }],
>>>>>>> Add_Failed_test
          requestBody: {
            required: true,
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
<<<<<<< HEAD
                    firstName: { type: 'string' },
                    lastName: { type: 'string' },
                    dob: { type: 'string', format: 'date' },
                    sex: { type: 'string', enum: ['Male', 'Female', 'N/A'] },
=======
                    firstName: { type: 'string', maxLength: 25, pattern: '^[A-Za-z]+$' },
                    lastName: { type: 'string', maxLength: 20, pattern: '^[A-Za-z]+$' },
                    dob: { type: 'string', format: 'date' },
                    sex: { type: 'string', enum: ['Male', 'Female'] },
>>>>>>> Add_Failed_test
                  },
                  required: ['firstName', 'lastName', 'dob', 'sex'],
                },
              },
            },
          },
          responses: {
<<<<<<< HEAD
            201: {
              description: 'Client created',
              content: {
                'application/json': {
                  schema: { $ref: '#/components/schemas/Client' },
                },
              },
            },
            400: {
              description: 'Validation error',
              content: {
                'application/json': {
                  schema: { $ref: '#/components/schemas/Error' },
                },
              },
            },
            401: {
              description: 'Missing token',
              content: {
                'application/json': {
                  schema: { $ref: '#/components/schemas/Error' },
                },
              },
            },
            403: {
              description: 'Invalid or expired token',
              content: {
                'application/json': {
                  schema: { $ref: '#/components/schemas/Error' },
                },
              },
            },
=======
            201: { description: 'Client created', content: { 'application/json': { schema: { $ref: '#/components/schemas/Client' } } } },
            400: { description: 'Validation error', content: { 'application/json': { schema: { $ref: '#/components/schemas/Error' } } } },
            401: { description: 'Missing token', content: { 'application/json': { schema: { $ref: '#/components/schemas/Error' } } } },
            403: { description: 'Invalid or expired token', content: { 'application/json': { schema: { $ref: '#/components/schemas/Error' } } } },
          },
        },
      },
      '/tokens/status': {
        get: {
          summary: 'Get current token status',
          security: [{ bearerAuth: [] }],
          responses: {
            200: { description: 'Token status information', content: { 'application/json': { schema: { type: 'object', properties: { status: { type: 'string', enum: ['Active', 'Valid', 'Invalid'] }, lastUsedAt: { type: 'string', format: 'date-time' } } } } } },
            401: { description: 'Missing or invalid token' },
          },
        },
      },
      '/tokens/invalidate': {
        post: {
          summary: 'Invalidate current token',
          security: [{ bearerAuth: [] }],
          responses: {
            200: { description: 'Token invalidated' },
            401: { description: 'Missing or invalid token' },
>>>>>>> Add_Failed_test
          },
        },
      },
    },
  },
  apis: [],
};

const swaggerSpec = swaggerJsdoc(swaggerOptions);

<<<<<<< HEAD
const PORT = process.env.PORT || 3001;
=======
const PORT = process.env.PORT || 8000;
>>>>>>> Add_Failed_test
const JWT_SECRET = process.env.JWT_SECRET || 'dev_super_secret_change_me';
const INACTIVITY_MS = (process.env.TOKEN_INACTIVITY_MINUTES ? Number(process.env.TOKEN_INACTIVITY_MINUTES) : 30) * 60 * 1000;

app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

// -----------------------------
// Auth middleware
// -----------------------------
async function authenticateToken(req, res, next) {
  const auth = req.headers['authorization'] || '';
  const token = auth.startsWith('Bearer ') ? auth.substring(7) : null;
  if (!token) return res.status(401).json({ message: 'Missing token' });

  let payload;
  try {
    payload = jwt.verify(token, JWT_SECRET);
  } catch (e) {
    return res.status(403).json({ message: 'Invalid or expired token' });
  }

  try {
    const rec = await store.getTokenRecord(token);
    if (!rec) return res.status(401).json({ message: 'Token not recognized' });
    if (rec.status === 'Invalid') return res.status(401).json({ message: 'Token invalid' });

    const lastUsed = rec.lastUsedAt ? new Date(rec.lastUsedAt) : null;
    const now = new Date();
    if (!lastUsed || isNaN(lastUsed.getTime())) {
      await store.touchToken(token);
    } else {
      const diff = now.getTime() - lastUsed.getTime();
      if (diff > INACTIVITY_MS) {
        await store.setTokenStatus(token, 'Invalid');
        return res.status(401).json({ message: 'Token expired due to inactivity' });
      }
      await store.touchToken(token);
    }

    req.user = payload;
    next();
  } catch (err) {
    console.error('Auth error:', err);
    return res.status(500).json({ message: 'Internal server error' });
  }
}

// -----------------------------
// Helpers
// -----------------------------
function isValidSex(val) {
  return val === 'Male' || val === 'Female';
}

function lettersOnly(str) {
  return /^[A-Za-z]+$/.test((str || '').toString());
}

function isAtLeastAge(dobDate, minAge) {
  const now = new Date();
  let age = now.getFullYear() - dobDate.getFullYear();
  const m = now.getMonth() - dobDate.getMonth();
  if (m < 0 || (m === 0 && now.getDate() < dobDate.getDate())) age--;
  return age >= minAge;
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

    const user = await store.getUserByUsername(username);
    if (!user) return res.status(401).json({ message: 'Invalid credentials' });

    const isMatch = await bcrypt.compare(password, user.passwordHash);
    if (!isMatch) return res.status(401).json({ message: 'Invalid credentials' });

    const payload = { userId: user.id, username: user.username, role: user.role };
    const token = jwt.sign(payload, JWT_SECRET, { expiresIn: '2h' });

    await store.recordLogin(token, user.id, user.username);
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
    const mineOnly = req.query.mine === 'true';

    const clients = await store.getClientsForUser(userId, role, mineOnly);
    return res.json(clients || []);
  } catch (err) {
    console.error('Get clients error:', err);
    return res.status(500).json({ message: 'Internal server error' });
  }
}
app.get(['/api/clients', '/clients'], authenticateToken, getClientsHandler);

// POST /api/clients and /clients
async function createClientHandler(req, res) {
  try {
    console.log('POST /clients payload:', req.body);
    const { userId } = req.user || {};
    const { firstName, lastName, dob, sex } = req.body || {};

    if (!firstName || !lastName || !dob || !sex)
      return res.status(400).json({ message: 'firstName, lastName, dob, and sex are required' });

    if (!isValidSex(sex)) return res.status(400).json({ message: "sex must be 'Male' or 'Female'" });

    if (!lettersOnly(firstName)) return res.status(400).json({ message: 'firstName must contain only letters' });
    if (!lettersOnly(lastName)) return res.status(400).json({ message: 'lastName must contain only letters' });
    if (firstName.toString().length > 25) return res.status(400).json({ message: 'firstName max length is 25' });
    if (lastName.toString().length > 20) return res.status(400).json({ message: 'lastName max length is 20' });

    const dobDate = new Date(dob);
    if (isNaN(dobDate.getTime())) return res.status(400).json({ message: 'dob must be a valid date' });
    if (!isAtLeastAge(dobDate, 18)) return res.status(400).json({ message: 'User must be at least 18 years old' });

    const created = await store.createClient({
      firstName,
      lastName,
      dob: dobDate.toISOString().substring(0, 10),
      sex,
      createdByUserId: userId,
    });

    return res.status(201).json(created);
  } catch (err) {
    console.error('Create client error:', err);
    return res.status(500).json({ message: 'Internal server error' });
  }
}
app.post(['/api/clients', '/clients'], authenticateToken, createClientHandler);

// GET /api/clients/:id and /clients/:id
async function getClientByIdHandler(req, res) {
  try {
    const { userId, role } = req.user || {};
    const { id } = req.params || {};

    const client = await store.getClientById(id);
    if (!client) return res.status(404).json({ message: 'Client not found' });

    const isAdmin = (role || '').toString().toLowerCase() === 'admin';
    if (!isAdmin && client.createdByUserId !== userId) {
      return res.status(403).json({ message: 'Forbidden' });
    }

    return res.json(client);
  } catch (err) {
    console.error('Get client by id error:', err);
    return res.status(500).json({ message: 'Internal server error' });
  }
}
app.get(['/api/clients/:id', '/clients/:id'], authenticateToken, getClientByIdHandler);

// PUT /api/clients/:id and /clients/:id
async function updateClientHandler(req, res) {
  try {
    const { userId, role } = req.user || {};
    const { id } = req.params || {};
    const { firstName, lastName, dob, sex } = req.body || {};

    if (!firstName || !lastName || !dob || !sex)
      return res.status(400).json({ message: 'firstName, lastName, dob, and sex are required' });

<<<<<<< HEAD
    if (!isValidSex(sex)) return res.status(400).json({ message: "sex must be 'Male', 'Female', or 'N/A'" });

    const dobDate = new Date(dob);
    if (isNaN(dobDate.getTime())) return res.status(400).json({ message: 'dob must be a valid date' });
=======
    if (!isValidSex(sex)) return res.status(400).json({ message: "sex must be 'Male' or 'Female'" });
    if (!lettersOnly(firstName)) return res.status(400).json({ message: 'firstName must contain only letters' });
    if (!lettersOnly(lastName)) return res.status(400).json({ message: 'lastName must contain only letters' });
    if (firstName.toString().length > 25) return res.status(400).json({ message: 'firstName max length is 25' });
    if (lastName.toString().length > 20) return res.status(400).json({ message: 'lastName max length is 20' });

    const dobDate = new Date(dob);
    if (isNaN(dobDate.getTime())) return res.status(400).json({ message: 'dob must be a valid date' });
    if (!isAtLeastAge(dobDate, 18)) return res.status(400).json({ message: 'User must be at least 18 years old' });
>>>>>>> Add_Failed_test

    const existing = await store.getClientById(id);
    if (!existing) return res.status(404).json({ message: 'Client not found' });

    const isAdmin = (role || '').toString().toLowerCase() === 'admin';
    if (!isAdmin && existing.createdByUserId !== userId) {
      return res.status(403).json({ message: 'Forbidden' });
    }

    const updated = await store.updateClient(id, {
      firstName,
      lastName,
      dob: dobDate.toISOString().substring(0, 10),
      sex,
    });

    if (!updated) return res.status(404).json({ message: 'Client not found' });

    return res.json(updated);
  } catch (err) {
    console.error('Update client error:', err);
    return res.status(500).json({ message: 'Internal server error' });
  }
}
app.put(['/api/clients/:id', '/clients/:id'], authenticateToken, updateClientHandler);

// DELETE /api/clients/:id and /clients/:id
async function deleteClientHandler(req, res) {
  try {
    const { userId, role } = req.user || {};
    const { id } = req.params || {};

    const existing = await store.getClientById(id);
    if (!existing) return res.status(404).json({ message: 'Client not found' });

    const isAdmin = (role || '').toString().toLowerCase() === 'admin';
    if (!isAdmin && existing.createdByUserId !== userId) {
      return res.status(403).json({ message: 'Forbidden' });
    }

    const deleted = await store.deleteClient(id);
    if (!deleted) return res.status(404).json({ message: 'Client not found or could not be deleted' });

    return res.json({ message: 'Client deleted' });
  } catch (err) {
    console.error('Delete client error:', err);
    return res.status(500).json({ message: 'Internal server error' });
  }
}
app.delete(['/api/clients/:id', '/clients/:id'], authenticateToken, deleteClientHandler);

<<<<<<< HEAD
=======
// Token status and invalidation endpoints
app.get(['/api/tokens/status', '/tokens/status'], authenticateToken, async (req, res) => {
  try {
    const auth = req.headers['authorization'] || '';
    const token = auth.startsWith('Bearer ') ? auth.substring(7) : null;
    const rec = token ? await store.getTokenRecord(token) : null;
    if (!token || !rec) return res.status(404).json({ message: 'Token not found' });
    return res.json({ status: rec.status, lastUsedAt: rec.lastUsedAt });
  } catch (err) {
    console.error('Token status error:', err);
    return res.status(500).json({ message: 'Internal server error' });
  }
});

app.post(['/api/tokens/invalidate', '/tokens/invalidate'], authenticateToken, async (req, res) => {
  try {
    const auth = req.headers['authorization'] || '';
    const token = auth.startsWith('Bearer ') ? auth.substring(7) : null;
    if (!token) return res.status(400).json({ message: 'Missing token' });
    const ok = await store.invalidateToken(token);
    if (!ok) return res.status(404).json({ message: 'Token not found' });
    return res.json({ message: 'Token invalidated' });
  } catch (err) {
    console.error('Token invalidate error:', err);
    return res.status(500).json({ message: 'Internal server error' });
  }
});

>>>>>>> Add_Failed_test
// -----------------------------
// Start server
// -----------------------------
if (process.env.NODE_ENV !== 'test') {
  app.listen(PORT, '0.0.0.0', () => {
    console.log(`API listening on http://0.0.0.0:${PORT}`);
  });
}

module.exports = app;
