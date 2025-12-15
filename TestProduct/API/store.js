const fs = require('fs').promises;
const path = require('path');
const bcrypt = require('bcryptjs');

const DATA_FILE = path.join(__dirname, 'data.json');
const TOKEN_FILE = path.join(__dirname, 'token.json');

async function ensureDataFile() {
  try {
    await fs.access(DATA_FILE);
  } catch {
    const passwordHash = await bcrypt.hash('123456', 10);
    const initial = {
      users: [
        {
          id: 1,
          username: 'user1',
          passwordHash,
          role: 'Admin',
        },
      ],
      clients: [],
    };
    await fs.writeFile(DATA_FILE, JSON.stringify(initial, null, 2), 'utf8');
  }
}

async function ensureTokenFile() {
  try {
    await fs.access(TOKEN_FILE);
  } catch {
    const initial = { tokens: [] };
    await fs.writeFile(TOKEN_FILE, JSON.stringify(initial, null, 2), 'utf8');
  }
}

async function readData() {
  await ensureDataFile();
  const raw = await fs.readFile(DATA_FILE, 'utf8');
  return JSON.parse(raw);
}

async function writeData(data) {
  await fs.writeFile(DATA_FILE, JSON.stringify(data, null, 2), 'utf8');
}

async function readTokens() {
  await ensureTokenFile();
  const raw = await fs.readFile(TOKEN_FILE, 'utf8');
  return JSON.parse(raw);
}

async function writeTokens(tokensDoc) {
  await fs.writeFile(TOKEN_FILE, JSON.stringify(tokensDoc, null, 2), 'utf8');
}

async function getUserByUsername(username) {
  const data = await readData();
  const uname = (username || '').toLowerCase();
  return data.users.find((u) => (u.username || '').toLowerCase() === uname) || null;
}

async function getClientsForUser(userId, role, mineOnly) {
  const data = await readData();
  const isAdmin = (role || '').toString().toLowerCase() === 'admin';
  let clients = data.clients || [];
  if (!isAdmin || mineOnly) {
    clients = clients.filter((c) => c.createdByUserId === userId);
  }
  return clients;
}

async function createClient(input) {
  const data = await readData();
  const clients = data.clients || [];
  const nextId = clients.length ? Math.max(...clients.map((c) => c.id || 0)) + 1 : 1;

  const client = {
    id: nextId,
    firstName: input.firstName,
    lastName: input.lastName,
    dob: input.dob,
    sex: input.sex,
    createdByUserId: input.createdByUserId,
  };

  clients.unshift(client);
  data.clients = clients;
  await writeData(data);

  return client;
}

async function getClientById(id) {
  const data = await readData();
  const intId = Number(id);
  if (!Number.isFinite(intId)) return null;
  const clients = data.clients || [];
  return clients.find((c) => c.id === intId) || null;
}

async function updateClient(id, input) {
  const data = await readData();
  const intId = Number(id);
  if (!Number.isFinite(intId)) return null;

  const clients = data.clients || [];
  const index = clients.findIndex((c) => c.id === intId);
  if (index === -1) return null;

  const existing = clients[index];
  const updated = {
    ...existing,
    firstName: input.firstName,
    lastName: input.lastName,
    dob: input.dob,
    sex: input.sex,
  };

  clients[index] = updated;
  data.clients = clients;
  await writeData(data);

  return updated;
}

async function deleteClient(id) {
  const data = await readData();
  const intId = Number(id);
  if (!Number.isFinite(intId)) return false;

  const clients = data.clients || [];
  const initialLength = clients.length;
  const filtered = clients.filter((c) => c.id !== intId);

  if (filtered.length === initialLength) return false;

  data.clients = filtered;
  await writeData(data);
  return true;
}

module.exports = {
  getUserByUsername,
  getClientsForUser,
  createClient,
  getClientById,
  updateClient,
  deleteClient,
  // token helpers
  async recordLogin(token, userId, username) {
    const doc = await readTokens();
    const now = new Date().toISOString();
    const existingIdx = (doc.tokens || []).findIndex((t) => t.token === token);
    const rec = {
      token,
      userId,
      username,
      status: 'Active',
      lastUsedAt: now,
    };
    if (existingIdx >= 0) {
      doc.tokens[existingIdx] = rec;
    } else {
      doc.tokens.push(rec);
    }
    await writeTokens(doc);
    return rec;
  },

  async getTokenRecord(token) {
    const doc = await readTokens();
    return (doc.tokens || []).find((t) => t.token === token) || null;
  },

  async touchToken(token) {
    const doc = await readTokens();
    const idx = (doc.tokens || []).findIndex((t) => t.token === token);
    if (idx === -1) return null;
    const rec = doc.tokens[idx];
    if (rec.status !== 'Invalid') {
      rec.status = 'Valid';
      rec.lastUsedAt = new Date().toISOString();
      doc.tokens[idx] = rec;
      await writeTokens(doc);
    }
    return rec;
  },

  async invalidateToken(token) {
    const doc = await readTokens();
    const idx = (doc.tokens || []).findIndex((t) => t.token === token);
    if (idx === -1) return false;
    doc.tokens[idx].status = 'Invalid';
    await writeTokens(doc);
    return true;
  },

  async setTokenStatus(token, status) {
    const doc = await readTokens();
    const idx = (doc.tokens || []).findIndex((t) => t.token === token);
    if (idx === -1) return false;
    doc.tokens[idx].status = status;
    await writeTokens(doc);
    return true;
  },

  async tokensDoc() {
    return readTokens();
  },
};
