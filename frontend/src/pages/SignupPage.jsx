import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'
import AuthCarousel from '../components/AuthCarousel'

const validatePassword = (value) => ({
  length: value.length >= 8,
  lower: /[a-z]/.test(value),
  upper: /[A-Z]/.test(value),
  number: /[0-9]/.test(value),
  special: /[^A-Za-z0-9]/.test(value),
})

const SignupPage = () => {
  const navigate = useNavigate()
  const { signupWithEmail, loginWithGoogle } = useAuth()
  const [name, setName] = useState('')
  const [surname, setSurname] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const passwordState = useMemo(() => validatePassword(password), [password])
  const isPasswordValid = Object.values(passwordState).every(Boolean)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!isPasswordValid) {
      setError('Please meet all password requirements before continuing.')
      return
    }

    setLoading(true)
    try {
      await signupWithEmail(name, surname, email, password)
      navigate('/')
    } catch (err) {
      const msg = err.code ? err.message : 'Signup failed. Please try again.'
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
      setError(err.code ? err.message : 'Google Signup failed.')
    } finally {
      setLoading(false)
    }
  }

  const renderRule = (ok, label) => (
    <li className={ok ? 'pw-rule pw-rule-ok' : 'pw-rule'}>{label}</li>
  )

  return (
    <div className="auth-layout">
      <div className="auth-panel image-panel" style={{ position: 'relative', padding: 0 }}>
        <AuthCarousel />
      </div>

      <div className="auth-panel form-panel">
        <div className="form-header">
          <h1>Create an account</h1>
          <p>
            Already have an account?{' '}
            <Link to="/login" className="link-inline">
              Log in
            </Link>
          </p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form wide">
          <div className="field-row">
            <label className="field">
              First name
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                placeholder="Fletcher"
              />
            </label>
            <label className="field">
              Last name
              <input
                type="text"
                value={surname}
                onChange={(e) => setSurname(e.target.value)}
                placeholder="(optional)"
              />
            </label>
          </div>

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
                placeholder="Enter a strong password"
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

          <ul className="pw-rules">
            {renderRule(passwordState.length, 'At least 8 characters')}
            {renderRule(passwordState.lower, 'Contains a lowercase letter')}
            {renderRule(passwordState.upper, 'Contains an uppercase letter')}
            {renderRule(passwordState.number, 'Contains a number')}
            {renderRule(passwordState.special, 'Contains a special character')}
          </ul>

          <label className="checkbox-row">
            <input type="checkbox" required /> I agree to the{' '}
            <a href="#" className="link-inline">
              Terms &amp; Conditions
            </a>
          </label>

          {error && <div className="auth-error">{error}</div>}

          <button type="submit" disabled={loading || !isPasswordValid}>
            {loading ? 'Creating account...' : 'Create account'}
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

export default SignupPage
