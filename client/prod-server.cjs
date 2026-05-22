const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');

const PORT = Number(process.env.CLIENT_PORT || 4200);
const API_TARGET_HOST = process.env.API_TARGET_HOST || '127.0.0.1';
const API_TARGET_PORT = Number(process.env.API_TARGET_PORT || 8000);
const DIST_ROOT =
  process.env.CLIENT_DIST_ROOT || path.join(__dirname, 'dist', 'client', 'browser');

const MIME_TYPES = {
  '.css': 'text/css; charset=utf-8',
  '.gif': 'image/gif',
  '.html': 'text/html; charset=utf-8',
  '.ico': 'image/x-icon',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.map': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.txt': 'text/plain; charset=utf-8',
  '.webp': 'image/webp',
};

function contentType(filePath) {
  return MIME_TYPES[path.extname(filePath).toLowerCase()] || 'application/octet-stream';
}

function send(res, statusCode, body, headers = {}) {
  res.writeHead(statusCode, headers);
  res.end(body);
}

function serveFile(res, filePath) {
  fs.readFile(filePath, (error, data) => {
    if (error) {
      send(res, 404, 'Not Found');
      return;
    }
    send(res, 200, data, {
      'Content-Type': contentType(filePath),
      'Cache-Control': filePath.endsWith('.html')
        ? 'no-cache'
        : 'public, max-age=31536000, immutable',
    });
  });
}

function proxyApiRequest(req, res) {
  const proxyReq = http.request(
    {
      hostname: API_TARGET_HOST,
      port: API_TARGET_PORT,
      method: req.method,
      path: req.url,
      headers: {
        ...req.headers,
        host: `${API_TARGET_HOST}:${API_TARGET_PORT}`,
      },
    },
    (proxyRes) => {
      res.writeHead(proxyRes.statusCode || 502, proxyRes.headers);
      proxyRes.pipe(res);
    }
  );

  proxyReq.on('error', () => {
    send(res, 502, 'Bad Gateway');
  });

  req.pipe(proxyReq);
}

function resolveStaticPath(urlPath) {
  const cleanPath = decodeURIComponent(urlPath.split('?')[0]).replace(/^\/+/, '');
  const candidate = path.join(DIST_ROOT, cleanPath);
  return candidate;
}

const server = http.createServer((req, res) => {
  if (!req.url) {
    send(res, 400, 'Bad Request');
    return;
  }

  if (req.url === '/health') {
    send(res, 200, JSON.stringify({ status: 'ok' }), {
      'Content-Type': 'application/json; charset=utf-8',
    });
    return;
  }

  if (req.url.startsWith('/api/')) {
    proxyApiRequest(req, res);
    return;
  }

  const filePath = resolveStaticPath(req.url);
  let stat;

  try {
    stat = fs.statSync(filePath);
  } catch {
    stat = null;
  }

  if (stat && stat.isFile()) {
    serveFile(res, filePath);
    return;
  }

  const indexPath = path.join(DIST_ROOT, 'index.html');
  serveFile(res, indexPath);
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`Client listening on http://0.0.0.0:${PORT}`);
  console.log(`Serving dist from ${DIST_ROOT}`);
});
