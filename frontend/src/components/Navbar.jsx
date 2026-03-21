import { useState, useRef, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import logo from '../../logo.png'

const links = [
  { to:'/',         label:'Home'     },
  { to:'/predict',  label:'Analyze'  },
  { to:'/history',  label:'History'  },
  { to:'/research', label:'Research' },
  { to:'/settings', label:'Settings' },
]

export default function Navbar() {
  const { user, fullName, logout } = useAuth()
  const nav = useNavigate()
  const loc = useLocation()
  const [open, setOpen] = useState(false)
  const ref  = useRef(null)

  useEffect(() => {
    const h = e => { if (ref.current && !ref.current.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', h)
    return () => document.removeEventListener('mousedown', h)
  }, [])

  // extract first letter for avatar, joined date
  const initial   = (fullName || user || 'U')[0].toUpperCase()
  const joinedDate = localStorage.getItem('bp_joined') || new Date().toLocaleDateString('en-GB', { month:'short', year:'numeric' })
  if (!localStorage.getItem('bp_joined')) localStorage.setItem('bp_joined', joinedDate)

  const menuItems = [
    {
      icon: '🚪',
      label: 'Logout',
      sub: 'Sign out of this device',
      action: () => {
        logout();
        setOpen(false);
      },
      danger: true,
    },
  ];

  return (
    <nav style={{
      position:'fixed', top:0, left:0, right:0, zIndex:900,
      height:62, display:'flex', alignItems:'center', padding:'0 32px',
      background:'var(--nav-bg)', backdropFilter:'blur(24px) saturate(1.8)',
      borderBottom:'1px solid var(--b1)', transition:'background .25s',
    }}>
      {/* Logo */}
      <div onClick={() => nav('/')} style={{
        display:'flex', alignItems:'center', gap:10, cursor:'pointer', marginRight:36, flexShrink:0,
      }}>
        <img src={logo} alt="logo" style={{ width:30, height:30 }} />
        <span style={{ fontFamily:'Syne,sans-serif', fontWeight:800, fontSize:16,
          color:'var(--white)', letterSpacing:'-.4px' }}>BloodPrint ID</span>
      </div>

      {/* Links */}
      <div style={{ display:'flex', alignItems:'center', gap:1, flex:1 }}>
        {links.map(l => {
          const active = loc.pathname === l.to
          return (
            <button key={l.to} onClick={() => nav(l.to)} style={{
              padding:'7px 15px', borderRadius:8, fontSize:13.5, fontWeight: active ? 600 : 400,
              color: active ? 'var(--white)' : 'var(--text2)',
              background: active ? 'var(--bg4)' : 'none', border:'none',
              cursor:'pointer', transition:'all .18s', letterSpacing: active ? '-.1px' : 'normal',
            }}
            onMouseEnter={e=>{ if(!active){ e.target.style.color='var(--text)'; e.target.style.background='var(--bg3)' }}}
            onMouseLeave={e=>{ if(!active){ e.target.style.color='var(--text2)'; e.target.style.background='none' }}}
            >{l.label}</button>
          )
        })}
      </div>

      {/* User dropdown */}
      {user && (
        <div ref={ref} style={{ position:'relative' }}>
          <button onClick={() => setOpen(o => !o)} style={{
            display:'flex', alignItems:'center', gap:9,
            padding:'6px 12px 6px 7px',
            background: open ? 'var(--bg4)' : 'var(--bg3)',
            border:`1px solid ${open ? 'var(--b2)' : 'var(--b1)'}`,
            borderRadius:22, cursor:'pointer', transition:'all .18s',
            boxShadow: open ? 'var(--card-shadow)' : 'none',
          }}>
            <div style={{
              width:28, height:28, borderRadius:'50%',
              background:'linear-gradient(135deg,var(--red),var(--pink))',
              display:'flex', alignItems:'center', justifyContent:'center',
              fontSize:12, fontWeight:700, color:'#fff', flexShrink:0,
              boxShadow:'0 0 0 2px var(--bg3)',
            }}>{initial}</div>
            <span style={{ fontFamily:'Outfit,sans-serif', fontSize:13.5,
              color:'var(--white)', fontWeight:600, letterSpacing:'-.1px' }}>
              {fullName || user}
            </span>
            <span style={{
              color:'var(--text3)', fontSize:9, marginLeft:1,
              transform: open ? 'rotate(180deg)' : 'none',
              transition:'transform .2s', display:'inline-block',
            }}>▼</span>
          </button>

          {/* Dropdown panel */}
          {open && (
            <div style={{
              position:'absolute', top:'calc(100% + 10px)', right:0,
              background:'var(--bg2)', border:'1px solid var(--b1)',
              borderRadius:14, width:240, zIndex:1000,
              boxShadow:'0 20px 60px rgba(0,0,0,.45), 0 0 0 1px rgba(255,255,255,.04)',
              overflow:'hidden',
              animation:'dropIn .2s cubic-bezier(.34,1.3,.64,1)',
            }}>

              {/* User info block */}
              <div style={{ padding:'16px', background:'var(--bg3)',
                borderBottom:'1px solid var(--b1)' }}>
                <div style={{ display:'flex', gap:11, alignItems:'center' }}>
                  <div style={{
                    width:40, height:40, borderRadius:'50%',
                    background:'linear-gradient(135deg,var(--red),var(--pink))',
                    display:'flex', alignItems:'center', justifyContent:'center',
                    fontSize:16, fontWeight:700, color:'#fff', flexShrink:0,
                    boxShadow:'0 0 0 3px var(--bg4)',
                  }}>{initial}</div>
                  <div>
                    <p style={{ fontSize:14, fontWeight:700, color:'var(--white)',
                      fontFamily:'Syne,sans-serif', lineHeight:1.2 }}>
                      {fullName || user}
                    </p>
                    <p style={{ fontSize:10.5, color:'var(--text3)',
                      fontFamily:'DM Mono,monospace', marginTop:2 }}>{user}</p>
                  </div>
                </div>

                {/* Stats row */}
                <div style={{ display:'flex', gap:8, marginTop:12 }}>
                  {[
                    { label:'Member since', value: joinedDate },
                    { label:'Role', value:'Researcher' },
                  ].map((s,i) => (
                    <div key={i} style={{
                      flex:1, background:'var(--bg4)', borderRadius:8,
                      padding:'7px 10px', border:'1px solid var(--b1)',
                    }}>
                      <p style={{ fontSize:9, color:'var(--text3)', textTransform:'uppercase',
                        letterSpacing:'.06em', marginBottom:2 }}>{s.label}</p>
                      <p style={{ fontSize:11.5, color:'var(--text)',
                        fontFamily:'DM Mono,monospace', fontWeight:500 }}>{s.value}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Menu items */}
              <div style={{ padding:'6px 0 4px' }}>
                {menuItems.map((item, i) =>
                  item.divider ? (
                    <div key={i} style={{ borderTop:'1px solid var(--b1)', margin:'4px 0' }} />
                  ) : (
                    <button key={i} onClick={item.action} style={{
                      width:'100%', padding:'9px 14px', textAlign:'left',
                      display:'flex', alignItems:'center', gap:11,
                      background:'none', border:'none', cursor:'pointer', transition:'background .15s',
                    }}
                    onMouseEnter={e => e.currentTarget.style.background = 'var(--bg3)'}
                    onMouseLeave={e => e.currentTarget.style.background = 'none'}
                    >
                      <span style={{ fontSize:15, width:22, textAlign:'center',
                        flexShrink:0 }}>{item.icon}</span>
                      <div>
                        <p style={{ fontSize:13, fontWeight:500,
                          color: item.danger ? 'var(--red2)' : 'var(--text)',
                          lineHeight:1.2 }}>{item.label}</p>
                        <p style={{ fontSize:10.5, color:'var(--text3)', lineHeight:1.2,
                          marginTop:1 }}>{item.sub}</p>
                      </div>
                    </button>
                  )
                )}
              </div>

            </div>
          )}
        </div>
      )}

      <style>{`@keyframes dropIn{from{opacity:0;transform:translateY(-8px) scale(.97)}to{opacity:1;transform:translateY(0) scale(1)}}`}</style>
    </nav>
  )
}