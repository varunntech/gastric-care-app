import { BrowserRouter, Route, Routes, Link } from 'react-router-dom'
import { useEffect } from 'react'
import './App.css'
import { AuthProvider, useAuth } from './AuthContext'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'

const Dashboard = () => {
  const { user } = useAuth()

  useEffect(() => {
    if (user) {
      window.location.href = '/?name=' + encodeURIComponent(user.name)
    }
  }, [user])

  return null
}

const Header = () => {
  const { user, logout } = useAuth()

  return (
    <header className="app-header">
      <h1>Gastric Cancer App</h1>
      <div className="app-header-actions">
        {user ? (
          <>
            {/* <span className="app-header-username">Hi, {user.name}</span>
            <button type="button" onClick={logout}>
              Logout
            </button> */}
          </>
        ) : (
          <>
            <Link to="/login" className="app-header-link">
              Login
            </Link>
            <Link to="/signup" className="app-header-link">
              Sign Up
            </Link>
          </>
        )}
      </div>
    </header>
  )
}

const ProtectedRoute = ({ children }) => {
  const { user } = useAuth()
  if (!user) {
    return <LoginPage />
  }
  return children
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="app-shell">
          <Header />
          <main className="app-main">
            <Routes>
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                }
              />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/signup" element={<SignupPage />} />
            </Routes>
          </main>
        </div>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
