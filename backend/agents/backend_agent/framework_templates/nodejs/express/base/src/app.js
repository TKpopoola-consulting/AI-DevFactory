require('dotenv').config();
const express = require('express');
const morgan = require('morgan');
const cors = require('cors');
const helmet = require('helmet');

const app = express();

// Middleware
app.use(morgan('dev'));
app.use(cors());
app.use(helmet());
app.use(express.json());

// Routes
app.use('/', require('./routes'));
app.use('/health', require('./routes/health'));

// Error handling
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Internal Server Error' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

module.exports = app;