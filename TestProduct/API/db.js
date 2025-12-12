const sql = require('mssql');

let pool;

function buildConfig() {
  if (process.env.DB_CONNECTION_STRING) {
    const cfg = { connectionString: process.env.DB_CONNECTION_STRING };
    if (process.env.DB_DRIVER) cfg.driver = process.env.DB_DRIVER;
    return cfg;
  }

  const driver = process.env.DB_DRIVER || 'tedious';
  if (driver === 'msnodesqlv8') {
    const server = process.env.DB_HOST || 'localhost';
    const database = process.env.DB_NAME || 'ClientManagementDB';
    return {
      driver: 'msnodesqlv8',
      connectionString:
        process.env.DB_CONNECTION_STRING ||
        `server=${server};Database=${database};Trusted_Connection=Yes;Driver={SQL Server Native Client 11.0}`,
    };
  }

  return {
    server: process.env.DB_HOST || 'localhost',
    database: process.env.DB_NAME || 'ClientManagementDB',
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    port: process.env.DB_PORT ? parseInt(process.env.DB_PORT, 10) : 1433,
    options: { trustServerCertificate: true },
  };
}

async function getPool() {
  if (pool) return pool;
  const config = buildConfig();
  pool = await new sql.ConnectionPool(config).connect();
  return pool;
}

module.exports = { sql, getPool };
