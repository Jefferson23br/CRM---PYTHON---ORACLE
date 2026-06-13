module.exports = {
  apps: [
    {
      name: "crm-api",
      cwd: "/var/www/crm/backend",
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
      error_file: "/var/log/crm-api/error.log",
      out_file: "/var/log/crm-api/out.log",
      merge_logs: true,
      time: true,
    },
  ],
};
