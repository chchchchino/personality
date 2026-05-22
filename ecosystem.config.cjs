module.exports = {
  apps: [
    {
      name: 'personality-server',
      script: '/opt/uv-venv/bin/uv',
      args: 'run uvicorn personality_server.app:app --host 127.0.0.1 --port 8000',
      cwd: '/app/server',
      interpreter: 'none',
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
