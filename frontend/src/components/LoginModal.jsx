import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'
import logo from '../../logo.png'

const inputStyle = (focus) => ({
  width: '100%', padding: '11px 14px',
  background: 'var(--input-bg)', border: `1px solid ${focus ? 'var(--cyan)' : 'var(--b1)'}`,
  borderRadius: 8, color: 'var(--text)', fontSize: 14, outline: 'none',
  transition: 'border-color .2s', boxShadow: focus ? '0 0 0 3px var(--cyan3)' : 'none',
})
const labelStyle = {
  display: 'block', fontSize: 11, fontWeight: 600, color: 'var(--text3)',
  textTransform: 'uppercase', letterSpacing: '.08em', marginBottom: 6,
}

function Field({ label, type='text', value, onChange, placeholder, autoComplete }) {
  const [focus, setFocus] = useState(false)
  return (
    <div style={{ marginBottom: 14 }}>
      <label style={labelStyle}>{label}</label>
      <input type={type} value={value} onChange={onChange} placeholder={placeholder}
        autoComplete={autoComplete}
        style={inputStyle(focus)}
        onFocus={() => setFocus(true)} onBlur={() => setFocus(false)} />
    </div>
  )
}

export default function LoginModal() {
  const { login, register, loading } = useAuth()
  const [tab,    setTab]   = useState('login')
  const [name,   setName]  = useState('')
  const [email,  setEmail] = useState('')
  const [pass,   setPass]  = useState('')
  const [show,   setShow]  = useState(false)
  const [err,    setErr]   = useState('')

  const reset = () => { setErr(''); setName(''); setEmail(''); setPass('') }

  const switchTab = (t) => { setTab(t); setErr('') }

  const submit = async (e) => {
    e.preventDefault(); setErr('')
    if (!email.trim() || !pass) { setErr('All fields are required.'); return }
    if (tab === 'register' && !name.trim()) { setErr('Full name is required.'); return }

    const res = tab === 'login'
      ? await login(email.trim(), pass)
      : await register(email.trim(), pass, name.trim())

    res.ok ? toast.success(`Welcome${tab === 'register' ? ', ' + name : ''}!`) : setErr(res.error)
  }

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 2000,
      background: 'rgba(6,6,15,.93)',
      backdropFilter: 'blur(20px) saturate(1.4)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
    }}>
      <div style={{
        width: 440, maxWidth: '94vw',
        background: 'var(--bg2)', border: '1px solid var(--b1)',
        borderRadius: 20, padding: '44px 40px',
        boxShadow: 'var(--shadow), 0 0 0 1px rgba(76,201,240,.06)',
        position: 'relative', overflow: 'hidden',
        animation: 'modalIn .38s cubic-bezier(.34,1.36,.64,1)',
      }}>
        <div style={{ position:'absolute', top:0, left:0, right:0, height:2,
          background:'linear-gradient(90deg,var(--red),var(--cyan))' }} />

        {/* Logo + title */}
        <div style={{ display:'flex', alignItems:'center', gap:12, marginBottom:6 }}>
          <img src={logo} alt="logo" style={{ width:40, height:40, objectFit:'contain' }} />
          <span style={{ fontFamily:'Syne,sans-serif', fontWeight:800, fontSize:21, color:'var(--white)' }}>
            BloodPrint ID
          </span>
        </div>
        <p style={{ color:'var(--text2)', fontSize:13, marginBottom:26 }}>
          Fingerprint Pattern Analysis Platform
        </p>

        {/* Tabs */}
        <div style={{ display:'flex', background:'var(--bg3)', borderRadius:10, padding:4, marginBottom:24, gap:2 }}>
          {['login','register'].map(t => (
            <button key={t} onClick={() => switchTab(t)} style={{
              flex:1, padding:'9px 0', textAlign:'center', fontSize:13, fontWeight:500,
              color: tab===t ? 'var(--white)' : 'var(--text2)',
              background: tab===t ? 'var(--bg5)' : 'none',
              border:'none', borderRadius:7,
              boxShadow: tab===t ? '0 2px 8px rgba(0,0,0,.4)' : 'none',
              transition:'all .2s', cursor:'pointer',
            }}>
              {t === 'login' ? 'Sign In' : 'Create Account'}
            </button>
          ))}
        </div>

        <form onSubmit={submit}>
          {err && (
            <div style={{ background:'rgba(230,57,70,.1)', border:'1px solid rgba(230,57,70,.25)',
              color:'#ff8080', fontSize:12.5, padding:'10px 13px', borderRadius:8, marginBottom:14 }}>
              {err}
            </div>
          )}

          {/* Full name — register only */}
          {tab === 'register' && (
            <Field label="Full Name" value={name} onChange={e => setName(e.target.value)}
              placeholder="e.g. Janani Viswa" autoComplete="name" />
          )}

          <Field label={tab === 'register' ? 'Email Address' : 'Email or Username'}
            type={tab === 'register' ? 'email' : 'text'}
            value={email} onChange={e => setEmail(e.target.value)}
            placeholder={tab === 'register' ? 'you@example.com' : 'Enter email or username'}
            autoComplete="username" />

          {/* Password with eye toggle */}
          <div style={{ marginBottom: 22 }}>
            <label style={labelStyle}>Password</label>
            <div style={{ position:'relative' }}>
              <input type={show ? 'text' : 'password'} value={pass}
                onChange={e => setPass(e.target.value)}
                placeholder={tab === 'register' ? 'Min. 6 characters' : 'Enter password'}
                autoComplete={tab === 'login' ? 'current-password' : 'new-password'}
                style={{ ...inputStyle(false), paddingRight: 42 }} />
              <button type="button" onClick={() => setShow(s => !s)} style={{
                position:'absolute', right:12, top:'50%', transform:'translateY(-50%)',
                background:'none', border:'none', color:'var(--text3)', fontSize:15, cursor:'pointer',
              }}>{show ? '🙈' : '👁'}</button>
            </div>
          </div>

          <button type="submit" disabled={loading} style={{
            width:'100%', padding:13,
            background:'linear-gradient(135deg, var(--red), #c1121f)',
            border:'none', borderRadius:8, color:'#fff', fontSize:14, fontWeight:600,
            cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? .6 : 1,
            boxShadow:'0 4px 20px rgba(230,57,70,.35)', transition:'all .2s',
          }}>
            {loading ? 'Please wait…' : tab === 'login' ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        <p style={{ textAlign:'center', marginTop:18, fontSize:12, color:'var(--text3)' }}>
          Demo: <code style={{ background:'var(--bg3)', padding:'2px 7px', borderRadius:5,
            fontFamily:'DM Mono,monospace', color:'var(--cyan)', fontSize:11 }}>demo</code>
          {' '}/ <code style={{ background:'var(--bg3)', padding:'2px 7px', borderRadius:5,
            fontFamily:'DM Mono,monospace', color:'var(--cyan)', fontSize:11 }}>demo123</code>
        </p>

        <style>{`
          @keyframes modalIn { from{transform:scale(.92) translateY(16px);opacity:0} to{transform:scale(1) translateY(0);opacity:1} }
        `}</style>
      </div>
    </div>
  )
}