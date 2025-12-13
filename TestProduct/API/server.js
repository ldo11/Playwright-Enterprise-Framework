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
const corsOrigin = process.env.CORS_ORIGIN || 'http://localhost:4200';
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
            Sex: { type: 'string', enum: ['Male', 'Female', 'N/A'] },
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
            200: {
              description: 'API is healthy',
            },
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
                example: {
                  username: 'user1',
                  password: '123456',
                },
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
            },
          },
        },
      },
      '/clients': {
        get: {
          summary: 'Get clients',
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
          },
        },
        post: {
          summary: 'Create a new client',
          security: [
            {
              bearerAuth: [],
            },
          ],
          requestBody: {
            required: true,
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    firstName: { type: 'string' },
                    lastName: { type: 'string' },
                    dob: { type: 'string', format: 'date' },
                    sex: { type: 'string', enum: ['Male', 'Female', 'N/A'] },
                  },
                  required: ['firstName', 'lastName', 'dob', 'sex'],
                },
              },
            },
          },
          responses: {
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
          },
        },
      },
    },
  },
  apis: [],
};

const swaggerSpec = swaggerJsdoc(swaggerOptions);

const PORT = process.env.PORT || 8000;
const JWT_SECRET = process.env.JWT_SECRET || 'dev_super_secret_change_me';

app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

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

    const user = await store.getUserByUsername(username);
    if (!user) return res.status(401).json({ message: 'Invalid credentials' });

    const isMatch = await bcrypt.compare(password, user.passwordHash);
    if (!isMatch) return res.status(401).json({ message: 'Invalid credentials' });

    const payload = { userId: user.id, username: user.username, role: user.role };
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
    const { userId } = req.user || {};
    const { firstName, lastName, dob, sex } = req.body || {};

    if (!firstName || !lastName || !dob || !sex)
      return res.status(400).json({ message: 'firstName, lastName, dob, and sex are required' });

    if (!isValidSex(sex)) return res.status(400).json({ message: "sex must be 'Male', 'Female', or 'N/A'" });

    const dobDate = new Date(dob);
    if (isNaN(dobDate.getTime())) return res.status(400).json({ message: 'dob must be a valid date' });

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

    if (!isValidSex(sex)) return res.status(400).json({ message: "sex must be 'Male', 'Female', or 'N/A'" });

    const dobDate = new Date(dob);
    if (isNaN(dobDate.getTime())) return res.status(400).json({ message: 'dob must be a valid date' });

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

// -----------------------------
// Start server
// -----------------------------
if (process.env.NODE_ENV !== 'test') {
  app.listen(PORT, () => {
    console.log(`API listening on http://localhost:${PORT}`);
  });
}

module.exports = app;
