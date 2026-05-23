module.exports = {
  apps: [
    {
      name: 'personality-server',
      script: '/app/start-server.sh',
      cwd: '/app/server',
      interpreter: 'bash',
    },
    {
      name: 'personality-client',
      script: '/app/client/prod-server.cjs',
      interpreter: 'node',
      env: {
        CLIENT_PORT: '4200',
        API_TARGET_HOST: '127.0.0.1',
        API_TARGET_PORT: '8000',
        CLIENT_DIST_ROOT: '/app/client/dist/client/browser',
      },
    },
  ],
};
