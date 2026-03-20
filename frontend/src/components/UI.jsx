// UI.jsx — unified design system components

export function Card({ children, style={} }) {
  return (
    <div style={{
      background:'var(--bg2)', border:'1px solid var(--b1)',
      borderRadius:14, padding:28,
      boxShadow:'var(--card-shadow)', ...style,
    }}>{children}</div>
  )
}

export function CardTitle({ children, style={} }) {
  return (
    <div style={{
      fontFamily:'Syne,sans-serif', fontSize:12, fontWeight:700,
      color:'var(--text2)', textTransform:'uppercase', letterSpacing:'.08em',
      marginBottom:20, display:'flex', alignItems:'center', gap:8, ...style,
    }}>
      <span style={{ width:5, height:5, borderRadius:'50%',
        background:'var(--red)', display:'inline-block',
        boxShadow:'0 0 6px var(--red)' }} />
      {children}
    </div>
  )
}

export function PageHeader({ title, subtitle, right }) {
  return (
    <div style={{ display:'flex', alignItems:'flex-start',
      justifyContent:'space-between', gap:16, marginBottom:36, flexWrap:'wrap' }}>
      <div>
        <h1 style={{ fontFamily:'Syne,sans-serif', fontWeight:800, fontSize:30,
          color:'var(--white)', letterSpacing:'-.6px', marginBottom:5 }}>{title}</h1>
        {subtitle && <p style={{ fontSize:14, color:'var(--text2)', fontWeight:300 }}>{subtitle}</p>}
      </div>
      {right && <div>{right}</div>}
    </div>
  )
}

const BTN = {
  primary:   { background:'linear-gradient(135deg,var(--red),#b01020)', color:'#fff', border:'none', boxShadow:'0 4px 18px rgba(230,57,70,.28)' },
  secondary: { background:'var(--bg3)', color:'var(--text)', border:'1px solid var(--b1)' },
  cyan:      { background:'var(--cyan2)', color:'var(--cyan)', border:'1px solid rgba(76,201,240,.18)' },
  danger:    { background:'var(--red3)', color:'var(--red2)', border:'1px solid rgba(230,57,70,.18)' },
  ghost:     { background:'none', color:'var(--text2)', border:'1px solid var(--b1)' },
}
export function Btn({ variant='primary', size='md', children, style={}, disabled, ...props }) {
  const pad = size==='sm' ? '7px 16px' : '11px 24px'
  const fnt = size==='sm' ? 12.5 : 14
  const rad = size==='sm' ? 8 : 10
  return (
    <button disabled={disabled} style={{
      display:'inline-flex', alignItems:'center', justifyContent:'center', gap:7,
      padding:pad, borderRadius:rad, fontSize:fnt, fontWeight:600,
      cursor: disabled ? 'not-allowed' : 'pointer',
      opacity: disabled ? .5 : 1,
      whiteSpace:'nowrap', transition:'all .18s', fontFamily:'Outfit,sans-serif',
      letterSpacing:'-.1px',
      ...BTN[variant], ...style,
    }} {...props}>{children}</button>
  )
}

export function Spinner({ size=28 }) {
  return (
    <>
      <div style={{ width:size, height:size, border:'2px solid var(--b2)',
        borderTopColor:'var(--cyan)', borderRadius:'50%',
        animation:'spin .65s linear infinite' }} />
      <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
    </>
  )
}

export function LoadingBox({ label='Loading…' }) {
  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center',
      gap:14, padding:'72px 40px', color:'var(--text2)', fontSize:13 }}>
      <Spinner /><span style={{ fontFamily:'Outfit,sans-serif' }}>{label}</span>
    </div>
  )
}

export function ProbBar({ label, value, color, highlight=false, max=1 }) {
  const pct = Math.min((value / Math.max(max, 0.0001)) * 100, 100)
  return (
    <div style={{ display:'flex', alignItems:'center', gap:12, padding:'5px 0' }}>
      <span style={{ width:54, fontFamily:'DM Mono,monospace', fontSize:12,
        color: highlight ? 'var(--gold)' : 'var(--text)',
        fontWeight: highlight ? 600 : 400, flexShrink:0 }}>{label}</span>
      <div style={{ flex:1, height:7, background:'var(--bg3)',
        borderRadius:4, overflow:'hidden' }}>
        <div style={{ width:`${pct}%`, height:'100%', background: color || 'var(--cyan)',
          borderRadius:4, transition:'width .9s cubic-bezier(.34,1.1,.64,1)' }} />
      </div>
      <span style={{ width:44, textAlign:'right', flexShrink:0,
        fontFamily:'DM Mono,monospace', fontSize:11.5,
        color: highlight ? 'var(--gold)' : 'var(--text2)',
        fontWeight: highlight ? 700 : 400 }}>{(value*100).toFixed(1)}%</span>
    </div>
  )
}

const TAGS = {
  loop:  { bg:'rgba(76,201,240,.1)',  color:'var(--loop)'  },
  whorl: { bg:'rgba(247,37,133,.1)',  color:'var(--whorl)' },
  arch:  { bg:'rgba(123,237,159,.1)', color:'var(--arch)'  },
  gold:  { bg:'var(--gold2)',         color:'var(--gold)'  },
  red:   { bg:'var(--red3)',          color:'var(--red2)'  },
  cyan:  { bg:'var(--cyan2)',         color:'var(--cyan)'  },
}
export function Tag({ variant='cyan', children, style={} }) {
  const s = TAGS[variant] || TAGS.cyan
  return (
    <span style={{ display:'inline-flex', alignItems:'center',
      padding:'3px 10px', borderRadius:20, fontSize:11.5, fontWeight:600,
      fontFamily:'DM Mono,monospace', ...s, ...style }}>{children}</span>
  )
}

export function Divider({ style={} }) {
  return <div style={{ borderTop:'1px solid var(--b1)', margin:'20px 0', ...style }} />
}

export function MetaChip({ label, value }) {
  return (
    <div style={{ background:'var(--bg3)', border:'1px solid var(--b1)',
      borderRadius:8, padding:'9px 14px',
      display:'flex', flexDirection:'column', gap:4 }}>
      <span style={{ fontSize:9.5, textTransform:'uppercase', letterSpacing:'.07em',
        color:'var(--text3)', fontFamily:'Outfit,sans-serif', fontWeight:600 }}>{label}</span>
      <span style={{ fontSize:13.5, fontWeight:600, color:'var(--text)',
        fontFamily:'Outfit,sans-serif' }}>{value}</span>
    </div>
  )
}

export function SectionLabel({ children }) {
  return (
    <p style={{ fontSize:10.5, fontWeight:700, textTransform:'uppercase',
      letterSpacing:'.1em', color:'var(--text3)', marginBottom:12,
      fontFamily:'Outfit,sans-serif' }}>{children}</p>
  )
}

export function DisclaimerBox() {
  return (
    <div style={{ background:'var(--red3)', border:'1px solid rgba(230,57,70,.2)',
      borderRadius:12, padding:'18px 20px',
      display:'flex', gap:14, alignItems:'flex-start' }}>
      <span style={{ fontSize:18, flexShrink:0 }}>⚠️</span>
      <div>
        <p style={{ fontSize:11, fontWeight:700, color:'var(--red2)',
          textTransform:'uppercase', letterSpacing:'.05em', marginBottom:6,
          fontFamily:'Outfit,sans-serif' }}>Research Tool — Not for Medical Use</p>
        <p style={{ fontSize:13, color:'var(--text2)', lineHeight:1.65,
          fontFamily:'Outfit,sans-serif', fontWeight:300 }}>
          Blood group predictions are <strong>statistical correlations</strong> from published
          dermatoglyphic research — not a medical diagnosis. Always use a certified
          laboratory test for actual blood typing.
        </p>
      </div>
    </div>
  )
}

// Input with unified styling
export function Input({ label, ...props }) {
  return (
    <div style={{ marginBottom:14 }}>
      {label && <label style={{ display:'block', fontSize:11, fontWeight:600,
        color:'var(--text3)', textTransform:'uppercase', letterSpacing:'.08em',
        marginBottom:7, fontFamily:'Outfit,sans-serif' }}>{label}</label>}
      <input className="bp-input" {...props} />
    </div>
  )
}