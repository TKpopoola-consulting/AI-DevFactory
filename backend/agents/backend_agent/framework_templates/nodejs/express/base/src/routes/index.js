const express = require('express');
const router = express.Router();

router.get('/', (req, res) => {
  res.json({ 
    message: 'Welcome to {{app_name}} API',
    endpoints: {
      docs: '/api-docs',
      health: '/health'
    }
  });
});

module.exports = router;