const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false,
    })
  );

  // Proxy for image uploads and other backend routes
  app.use(
    '/image-studio',
    createProxyMiddleware({
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false,
    })
  );

  // Proxy for YouTube routes
  app.use(
    '/youtube',
    createProxyMiddleware({
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false,
    })
  );

  // Proxy for other backend routes that might not start with /api
  app.use(
    '/scheduler',
    createProxyMiddleware({
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false,
    })
  );

  app.use(
    '/content-assets',
    createProxyMiddleware({
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false,
    })
  );
};