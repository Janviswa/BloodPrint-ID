import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import { ThemeProvider } from './context/ThemeContext'
import Navbar     from './components/Navbar'
import LoginModal from './components/LoginModal'
import Background from './components/Background'
import Home       from './pages/Home'
import Predict    from './pages/Predict'
import History    from './pages/History'
import Settings   from './pages/Settings'
import Research   from './pages/Research'

function Protected({ children }) {
  const { user } = useAuth()
  return user ? children : <Navigate to="/" replace />
}

function Layout() {
  const { user } = useAuth()
  return (
    <>
      <Background />
      <Navbar />
      {!user && <LoginModal />}
      <main style={{ paddingTop:62, minHeight:'100vh', position:'relative', zIndex:1 }}>
        <Routes>
          <Route path="/"         element={<Home />} />
          <Route path="/predict"  element={<Protected><Predict /></Protected>} />
          <Route path="/history"  element={<Protected><History /></Protected>} />
          <Route path="/research" element={<Research />} />
          <Route path="/settings" element={<Protected><Settings /></Protected>} />
          <Route path="*"         element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </>
  )
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Layout />
      </AuthProvider>
    </ThemeProvider>
  )
}