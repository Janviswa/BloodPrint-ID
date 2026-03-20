import { createContext, useContext, useState } from 'react'
import api from '../utils/api'

const Ctx = createContext(null)

export function AuthProvider({ children }) {
  const [user,      setUser]      = useState(localStorage.getItem('bp_user') || null)
  const [fullName,  setFullName]  = useState(localStorage.getItem('bp_name') || null)
  const [loading,   setLoading]   = useState(false)

  const _save = (data) => {
    localStorage.setItem('bp_tok',  data.token)
    localStorage.setItem('bp_user', data.username)
    localStorage.setItem('bp_name', data.full_name || data.username)
    setUser(data.username)
    setFullName(data.full_name || data.username)
  }

  const login = async (username, password) => {
    setLoading(true)
    try {
      const { data } = await api.post('/auth/login', { username, password })
      _save(data)
      return { ok: true }
    } catch (e) {
      return { ok: false, error: e.response?.data?.error || 'Login failed.' }
    } finally { setLoading(false) }
  }

  const register = async (username, password, full_name) => {
    setLoading(true)
    try {
      const { data } = await api.post('/auth/register', { username, password, full_name })
      _save(data)
      return { ok: true }
    } catch (e) {
      return { ok: false, error: e.response?.data?.error || 'Registration failed.' }
    } finally { setLoading(false) }
  }

  const logout = () => {
    ['bp_tok','bp_user','bp_name'].forEach(k => localStorage.removeItem(k))
    setUser(null); setFullName(null)
  }

  return (
    <Ctx.Provider value={{ user, fullName, loading, login, register, logout }}>
      {children}
    </Ctx.Provider>
  )
}

export const useAuth = () => useContext(Ctx)