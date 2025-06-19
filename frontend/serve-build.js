const handler = require('serve-handler');
const http = require('http');

const server = http.createServer((request, response) => {
  return handler(request, response, {
    public: 'build',
    rewrites: [
      { source: '**', destination: '/index.html' }
    ]
  });
});

server.listen(3000, '0.0.0.0', () => {
  console.log('Running static server on http://0.0.0.0:3000');
});