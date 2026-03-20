// utils/api.js
import axios from 'axios'

// In production (Vercel), VITE_API_URL = your Render backend URL
// In development, Vite proxy forwards /api → localhost:5000
const baseURL = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api`
  : '/api'

const api = axios.create({ baseURL })

// Attach JWT to every request
api.interceptors.request.use(cfg => {
  const tok = localStorage.getItem('bp_tok')
  if (tok) cfg.headers.Authorization = `Bearer ${tok}`
  return cfg
})

// Auto-logout on 401
api.interceptors.response.use(
  r => r,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('bp_tok')
      localStorage.removeItem('bp_user')
      window.location.href = '/'
    }
    return Promise.reject(err)
  }
)

export default api