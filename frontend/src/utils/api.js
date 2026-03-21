import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

api.interceptors.request.use(cfg => {
  const tok = localStorage.getItem('bp_tok')
  if (tok) {
    cfg.headers.Authorization = `Bearer ${tok}`
  }
  cfg.headers['Content-Type'] = cfg.headers['Content-Type'] || 'application/json'
  return cfg
})

api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('bp_tok')
      localStorage.removeItem('bp_user')
      window.location.replace('/')
    }
    return Promise.reject(err)
  }
)

export default api