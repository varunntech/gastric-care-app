const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const connectDB = require('./config/db');
const authRoutes = require('./routes/authRoutes');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 4000;
const CLIENT_ORIGIN = process.env.CLIENT_ORIGIN || 'http://localhost:5173';
const MONGO_URI =
  process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/stomach_cancer_auth';

app.use(
  cors({
    origin: CLIENT_ORIGIN,
    credentials: true,
  })
);
app.use(express.json());

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.use('/api/auth', authRoutes);

const startServer = async () => {
  await connectDB(MONGO_URI);
  app.listen(PORT, () => {
    console.log(`Auth server running on port ${PORT}`);
  });
};

startServer();

