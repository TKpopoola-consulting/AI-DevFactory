module.exports = {
  apps: [
    {
      name: 'aidevfactory-backend',
      script: '/production/AI-DevFactory/backend/start.sh',
      interpreter: '/bin/bash',
      watch: false,
      instances: 1,
      autorestart: true,
      max_memory_restart: '500M',
      error_file: '/production/AI-DevFactory/logs/backend-error.log',
      out_file: '/production/AI-DevFactory/logs/backend-out.log',
      log_file: '/production/AI-DevFactory/logs/backend-combined.log',
      time: true,
      env: {
        PYTHONUNBUFFERED: '1'
      }
    },
    {
      name: 'aidevfactory-frontend',
      script: 'python3',
      args: '-m http.server 8080',
      cwd: '/production/AI-DevFactory',
      watch: false,
      instances: 1,
      autorestart: true,
      error_file: '/production/AI-DevFactory/logs/frontend-error.log',
      out_file: '/production/AI-DevFactory/logs/frontend-out.log',
      log_file: '/production/AI-DevFactory/logs/frontend-combined.log',
      time: true
    }
  ]
};
