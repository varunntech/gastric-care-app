import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'
import AuthCarousel from '../components/AuthCarousel'

const LoginPage = () => {
  const navigate = useNavigate()
  const { loginWithEmail, loginWithGoogle } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await loginWithEmail(email, password)
      navigate('/')
    } catch (err) {
      const msg = err.code ? err.message : 'Login failed. Please check your credentials.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleLogin = async () => {
    setError('')
    setLoading(true)
    try {
      await loginWithGoogle()
      navigate('/')
    } catch (err) {
      setError(err.code ? err.message : 'Google Login failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-layout">
      <div className="auth-panel image-panel" style={{ position: 'relative', padding: 0 }}>
        <AuthCarousel />
      </div>

      <div className="auth-panel form-panel">
        <div className="form-header">
          <h1>Log in</h1>
          <p>
            Don&apos;t have an account?{' '}
            <Link to="/signup" className="link-inline">
              Create one
            </Link>
          </p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form wide">
          <label className="field">
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="you@example.com"
            />
          </label>
          <label className="field">
            Password
            <div className="password-wrapper">
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={8}
                placeholder="Enter your password"
              />
              <button
                type="button"
                className="pw-toggle"
                onClick={() => setShowPassword((v) => !v)}
              >
                {showPassword ? 'Hide' : 'Show'}
              </button>
            </div>
          </label>

          {error && <div className="auth-error">{error}</div>}

          <button type="submit" disabled={loading}>
            {loading ? 'Logging in...' : 'Log in'}
          </button>
          
          <div style={{ display: 'flex', alignItems: 'center', margin: '20px 0', color: '#6b7280' }}>
            <hr style={{ flex: 1, borderColor: '#e5e7eb', borderStyle: 'solid', borderWidth: '1px 0 0' }} />
            <span style={{ padding: '0 10px', fontSize: '0.875rem' }}>or</span>
            <hr style={{ flex: 1, borderColor: '#e5e7eb', borderStyle: 'solid', borderWidth: '1px 0 0' }} />
          </div>

          <button 
            type="button" 
            onClick={handleGoogleLogin} 
            disabled={loading}
            style={{ backgroundColor: '#fff', color: '#333', border: '1px solid #ccc', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}
          >
            <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="Google" style={{ width: 18, height: 18 }} />
            Continue with Google
          </button>
        </form>
      </div>
    </div>
  )
}

export default LoginPage
