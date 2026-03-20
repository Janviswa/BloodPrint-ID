import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'
import toast from 'react-hot-toast'
import api from '../utils/api'
import { PageHeader, Btn } from '../components/UI'

function Toggle({ checked, onChange }) {
  return (
    <label style={{ position:'relative', width:46, height:26, flexShrink:0, cursor:'pointer', display:'block' }}>
      <input type="checkbox" checked={checked} onChange={onChange}
        style={{ opacity:0, width:0, height:0, position:'absolute' }} />
      <span style={{
        position:'absolute', inset:0, borderRadius:26,
        background: checked ? 'rgba(230,57,70,.2)' : 'var(--bg4)',
        border:`1px solid ${checked ? 'var(--red)' : 'var(--b2)'}`,
        transition:'all .25s',
      }}>
        <span style={{
          position:'absolute', width:18, height:18,
          left: checked ? 'calc(100% - 21px)' : 3, bottom:3,
          borderRadius:'50%', background: checked ? 'var(--red)' : 'var(--text3)',
          transition:'all .25s',
        }} />
      </span>
    </label>
  )
}

function SCard({ title, children, danger }) {
  return (
    <div style={{
      background:'var(--bg2)',
      border:`1px solid ${danger ? 'rgba(230,57,70,.25)' : 'var(--b1)'}`,
      borderRadius:14, overflow:'hidden',
    }}>
      <div style={{
        padding:'18px 24px', borderBottom:`1px solid ${danger ? 'rgba(230,57,70,.15)' : 'var(--b1)'}`,
        fontFamily:'Syne,sans-serif', fontSize:15, fontWeight:700,
        color: danger ? 'var(--red2)' : 'var(--white)',
      }}>{title}</div>
      <div style={{ padding:'4px 24px 20px' }}>{children}</div>
    </div>
  )
}

function SRow({ label, desc, right, last }) {
  return (
    <div style={{
      display:'flex', alignItems:'center', justifyContent:'space-between',
      padding:'14px 0',
      borderBottom: last ? 'none' : '1px solid var(--b1)',
    }}>
      <div style={{ flex:1, paddingRight:20 }}>
        <p style={{ fontSize:14, fontWeight:500, color:'var(--text)', marginBottom:3 }}>{label}</p>
        {desc && <p style={{ fontSize:12, color:'var(--text2)', lineHeight:1.5 }}>{desc}</p>}
      </div>
      {right}
    </div>
  )
}

function Field({ label, type='text', value, onChange, placeholder }) {
  const [f, setF] = useState(false)
  return (
    <div style={{ marginBottom:14 }}>
      <label style={{ display:'block', fontSize:11, fontWeight:700, color:'var(--text3)',
        textTransform:'uppercase', letterSpacing:'.08em', marginBottom:7 }}>{label}</label>
      <input type={type} value={value} onChange={onChange} placeholder={placeholder}
        style={{
          width:'100%', padding:'11px 14px', background:'var(--input-bg)',
          border:`1px solid ${f ? 'var(--cyan)' : 'var(--b1)'}`, borderRadius:8,
          color:'var(--text)', fontSize:14, outline:'none', transition:'border-color .2s',
        }}
        onFocus={() => setF(true)} onBlur={() => setF(false)} />
    </div>
  )
}

export default function Settings() {
  const { user, fullName, logout } = useAuth()
  const { dark, toggle: toggleTheme } = useTheme()

  // Username / display name
  const [newName,    setNewName]    = useState('')
  const [nameErr,    setNameErr]    = useState('')
  const [nameSaving, setNameSaving] = useState(false)

  // Password
  const [oldPw,  setOldPw]  = useState('')
  const [newPw,  setNewPw]  = useState('')
  const [confPw, setConfPw] = useState('')
  const [pwErr,  setPwErr]  = useState('')

  // Prefs
  const getP = k => JSON.parse(localStorage.getItem('bp_prefs')||'{}')[k] ?? true
  const [showConf,  setShowConf]  = useState(() => getP('showConfWarn'))
  const [showValid, setShowValid] = useState(() => getP('showValidWarn'))
  const [autoScroll,setScroll]    = useState(() => getP('autoScroll'))
  const saveP = (k,v) => {
    const p = JSON.parse(localStorage.getItem('bp_prefs')||'{}')
    localStorage.setItem('bp_prefs', JSON.stringify({...p,[k]:v}))
  }

  const saveName = async () => {
    setNameErr('')
    if (!newName.trim()) { setNameErr('Name cannot be empty.'); return }
    setNameSaving(true)
    try {
      const { data } = await api.post('/auth/update-name', { full_name: newName.trim() })
      // Update localStorage
      localStorage.setItem('bp_name', data.full_name)
      // Force page reload so navbar updates
      toast.success('Display name updated! Refreshing…')
      setTimeout(() => window.location.reload(), 1000)
    } catch (e) {
      setNameErr(e.response?.data?.error || 'Failed to update name.')
    } finally { setNameSaving(false) }
  }

  const savePw = async () => {
    setPwErr('')
    if (!oldPw || !newPw || !confPw) { setPwErr('All fields are required.'); return }
    if (newPw !== confPw)            { setPwErr('New passwords do not match.'); return }
    if (newPw.length < 6)            { setPwErr('Password must be at least 6 characters.'); return }
    try {
      await api.post('/auth/change-password', { old_password:oldPw, new_password:newPw })
      toast.success('Password updated!')
      setOldPw(''); setNewPw(''); setConfPw('')
    } catch (e) { setPwErr(e.response?.data?.error || 'Failed.') }
  }

  const clearHistory = async () => {
    if (!confirm('Clear all prediction history?')) return
    await api.delete('/history')
    toast.success('History cleared.')
  }

  return (
    <div style={{ maxWidth:780, margin:'0 auto', padding:'52px 28px 80px' }}>
      <PageHeader title="Settings" subtitle="Manage your account and preferences" />

      <div style={{ display:'flex', flexDirection:'column', gap:20 }}>

        {/* Account */}
        <SCard title="👤 Account">
          {/* Current identity */}
          <SRow
            label="Email"
            desc="Your login email address"
            right={
              <span style={{ fontFamily:'DM Mono,monospace', fontSize:12,
                color:'var(--text2)', textAlign:'right' }}>
                {user}
              </span>
            }
          />
          <SRow
            label="Display Name"
            desc="Name shown in the navbar and reports"
            last
            right={
              <span style={{ fontFamily:'Outfit,sans-serif', fontSize:13,
                color:'var(--cyan)', fontWeight:600 }}>
                {fullName || '—'}
              </span>
            }
          />

          {/* Change display name */}
          <div style={{ paddingTop:16, borderTop:'1px solid var(--b1)', marginTop:4 }}>
            <p style={{ fontSize:13, fontWeight:600, color:'var(--text)', marginBottom:14 }}>
              Change Display Name
            </p>
            {nameErr && (
              <div style={{ background:'rgba(230,57,70,.1)', border:'1px solid rgba(230,57,70,.25)',
                color:'#ff8080', fontSize:12, padding:'9px 13px', borderRadius:8, marginBottom:12 }}>
                {nameErr}
              </div>
            )}
            <Field label="New Display Name" value={newName}
              onChange={e => setNewName(e.target.value)}
              placeholder={`Current: ${fullName || user}`} />
            <Btn onClick={saveName} style={{ marginTop:4 }} disabled={nameSaving}>
              {nameSaving ? 'Saving…' : 'Update Name'}
            </Btn>
          </div>

          {/* Change password */}
          <div style={{ paddingTop:16, borderTop:'1px solid var(--b1)', marginTop:16 }}>
            <p style={{ fontSize:13, fontWeight:600, color:'var(--text)', marginBottom:14 }}>
              Change Password
            </p>
            {pwErr && (
              <div style={{ background:'rgba(230,57,70,.1)', border:'1px solid rgba(230,57,70,.25)',
                color:'#ff8080', fontSize:12, padding:'9px 13px', borderRadius:8, marginBottom:12 }}>
                {pwErr}
              </div>
            )}
            <Field label="Current Password" type="password" value={oldPw}
              onChange={e => setOldPw(e.target.value)} placeholder="Current password" />
            <Field label="New Password" type="password" value={newPw}
              onChange={e => setNewPw(e.target.value)} placeholder="New password (min 6 chars)" />
            <Field label="Confirm New Password" type="password" value={confPw}
              onChange={e => setConfPw(e.target.value)} placeholder="Repeat new password" />
            <Btn onClick={savePw} style={{ marginTop:4 }}>Update Password</Btn>
          </div>
        </SCard>

        {/* Appearance */}
        <SCard title="🎨 Appearance">
          <SRow
            label="Dark Mode"
            desc="Toggle between dark and light theme. Default: Dark."
            last
            right={<Toggle checked={dark} onChange={toggleTheme} />}
          />
        </SCard>

        {/* Preferences */}
        <SCard title="⚙ Preferences">
          <SRow label="Show Low Confidence Warning"
            desc="Display banner when model confidence is below 55%"
            right={<Toggle checked={showConf} onChange={e=>{setShowConf(e.target.checked);saveP('showConfWarn',e.target.checked)}} />}
          />
          <SRow label="Show Fingerprint Validity Warning"
            desc="Warn when image may not be a fingerprint"
            right={<Toggle checked={showValid} onChange={e=>{setShowValid(e.target.checked);saveP('showValidWarn',e.target.checked)}} />}
          />
          <SRow label="Auto-scroll to Results"
            desc="Scroll to results automatically after analysis"
            last
            right={<Toggle checked={autoScroll} onChange={e=>{setScroll(e.target.checked);saveP('autoScroll',e.target.checked)}} />}
          />
        </SCard>

        {/* Danger */}
        <SCard title="⚠ Danger Zone" danger>
          <SRow label="Clear Prediction History"
            desc="Permanently delete all your saved predictions"
            right={<Btn variant="danger" size="sm" onClick={clearHistory}>Clear History</Btn>}
          />
          <SRow label="Sign Out" desc="Log out of your account on this device" last
            right={<Btn variant="danger" size="sm" onClick={logout}>Sign Out</Btn>}
          />
        </SCard>

        {/* About */}
        <SCard title="ℹ About BloodPrint ID">
          {[
            ['Version',      'v1.0.0'],
            ['Model',        'EfficientNetB0 (ImageNet weights)'],
            ['Framework',    'React + Flask'],
            ['Research',     'Dogra et al. (2014), Nayak et al. (2010), Igbigbi & Thumb (2002)'],
            ['Purpose',      'Educational & research use only — not a medical tool'],
          ].map(([k,v]) => (
            <div key={k} style={{ padding:'12px 0', borderBottom:'1px solid var(--b1)',
              display:'flex', gap:16 }}>
              <span style={{ fontSize:11.5, color:'var(--text3)', width:120, flexShrink:0 }}>{k}</span>
              <span style={{ fontSize:13.5,
                color: k==='Purpose' ? 'var(--red2)' : 'var(--text)' }}>{v}</span>
            </div>
          ))}
        </SCard>

      </div>
    </div>
  )
}