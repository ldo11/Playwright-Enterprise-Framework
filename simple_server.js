const http = require('http');
const port = 3001;
const server = http.createServer((req, res) => {
  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.end('Hello World\n');
});
server.listen(port, '127.0.0.1', () => {
  console.log(`Test server running at http://127.0.0.1:${port}/`);
});
