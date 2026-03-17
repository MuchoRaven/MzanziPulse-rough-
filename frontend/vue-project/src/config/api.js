// Central API base URL.
// In production (Vercel), set VITE_API_BASE_URL to your Railway backend URL.
// Locally it falls back to http://localhost:5000
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

export default API_BASE
