module.exports = {
  apps: [
    {
      name: "crm-api",
      cwd: "/caminho/para/seu-projeto/backend",
      script: "venv/bin/uvicorn",
      args: "app.main:app --host 0.0.0.0 --port 8000 --workers 2",
      interpreter: "none",
      env: {
        APP_ENV: "production",
        DEBUG: "false",
      },
      autorestart: true,
      watch: false,
      max_memory_restart: "500M",
      error_file: "/var/log/seu-app/error.log",
      out_file: "/var/log/seu-app/out.log",
      merge_logs: true,
      time: true,
    },
  ],
};
