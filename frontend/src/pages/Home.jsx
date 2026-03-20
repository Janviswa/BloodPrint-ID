// pages/Home.jsx
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Btn, DisclaimerBox } from '../components/UI'

const STATS = [
  { num: '3',  suf: '+', lbl: 'Pattern Types Classified' },
  { num: '8',  suf: '',  lbl: 'Blood Groups Correlated'  },
  { num: 'AI', suf: '',  lbl: 'EfficientNetB0 Model'     },
  { num: '4',  suf: '+', lbl: 'Research Papers Referenced'},
]
const STEPS = [
  {
    n: '01', icon: '🫆', col: 'rgba(57, 152, 230, 0.12)',
    title: 'Upload Fingerprint',
    desc: 'Upload a clear fingerprint scan. The system applies CLAHE enhancement to correct uneven lighting before analysis.',
  },
  {
    n: '02', icon: '🧠', col: 'rgba(156, 59, 59, 0.11)',
    title: 'AI Classification',
    desc: 'EfficientNetB0 classifies the fingerprint into Loop, Whorl, or Arch pattern with a real-time confidence score.',
  },
  {
    n: '03', icon: '📑', col: 'rgba(206, 233, 215, 0.11)',
    title: 'Statistical Report',
    desc: 'Pattern is cross-referenced with published studies to generate blood group likelihood distributions across all 8 types.',
  },
]

export default function Home() {
  const nav  = useNavigate()
  const { user } = useAuth()

  return (
    <div style={{ maxWidth: 1120, margin: '0 auto', padding: '52px 28px 80px' }}>

      {/* ── Hero */}
      <div style={{ textAlign: 'center', padding: '72px 0 60px', position: 'relative' }}>
        <div style={{
          position: 'absolute', top: 0, left: '50%', transform: 'translateX(-50%)',
          width: 640, height: 320,
          background: 'radial-gradient(ellipse, rgba(230,57,70,.11) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />

        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 8,
          background: 'var(--cyan2)', border: '1px solid rgba(76,201,240,.2)',
          color: 'var(--cyan)', fontSize: 11.5, fontWeight: 600,
          textTransform: 'uppercase', letterSpacing: '.1em',
          padding: '6px 16px', borderRadius: 20, marginBottom: 28,
        }}>
          🔬 Research Tool &nbsp;·&nbsp; Educational Use Only
        </div>

        <h1 style={{
          fontFamily: 'Syne, sans-serif', fontWeight: 800,
          fontSize: 'clamp(44px, 6.5vw, 80px)', lineHeight: 1.02,
          color: 'var(--white)', letterSpacing: '-1.5px', marginBottom: 22,
        }}>
          Fingerprint<br />
          <span style={{ color: 'var(--red)' }}>Blood Group</span><br />
          Correlation
        </h1>

        <p style={{
          fontSize: 17, color: 'var(--text2)', maxWidth: 520,
          margin: '0 auto 38px', lineHeight: 1.65, fontWeight: 300,
        }}>
          An AI-powered research tool that analyzes fingerprint ridge patterns
          and maps them to statistical blood group correlations using EfficientNetB0.
        </p>

        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Btn onClick={() => nav(user ? '/predict' : '/')}>
            Start Analysis →
          </Btn>
          <Btn variant="secondary" onClick={() => nav('/history')}>
            View History
          </Btn>
        </div>
      </div>

      {/* ── Stats */}
      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)',
        gap: 16, margin: '0 0 60px',
      }}>
        {STATS.map((s, i) => (
          <div key={i} style={{
            background: 'var(--bg2)', border: '1px solid var(--b1)',
            borderRadius: 14, padding: '26px 22px', textAlign: 'center',
            transition: 'all .2s',
          }}
          onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--b2)'}
          onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--b1)'}
          >
            <div style={{
              fontFamily: 'Syne, sans-serif', fontSize: 40,
              fontWeight: 800, color: 'var(--white)', lineHeight: 1,
            }}>
              {s.num}<span style={{ color: 'var(--red)' }}>{s.suf}</span>
            </div>
            <div style={{ fontSize: 12.5, color: 'var(--text2)', marginTop: 7 }}>{s.lbl}</div>
          </div>
        ))}
      </div>

      {/* ── How it works */}
      <p style={{
        fontFamily: 'Syne, sans-serif', fontSize: 28, fontWeight: 700,
        color: 'var(--white)', marginBottom: 8,
      }}>How It Works</p>
      <p style={{ fontSize: 14, color: 'var(--text2)', marginBottom: 36 }}>
        Three steps from fingerprint image to statistical report
      </p>

      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20,
      }}>
        {STEPS.map((s, i) => (
          <div key={i} style={{
            background: 'var(--bg2)', border: '1px solid var(--b1)',
            borderRadius: 14, padding: '32px 26px',
            position: 'relative', overflow: 'hidden',
            transition: 'all .2s',
          }}
          onMouseEnter={e => { e.currentTarget.style.borderColor='var(--b2)'; e.currentTarget.style.transform='translateY(-3px)' }}
          onMouseLeave={e => { e.currentTarget.style.borderColor='var(--b1)'; e.currentTarget.style.transform='translateY(0)' }}
          >
            <div style={{
              position: 'absolute', bottom: -14, right: 12,
              fontFamily: 'Syne, sans-serif', fontSize: 88,
              fontWeight: 800, color: 'rgba(255,255,255,.025)',
              lineHeight: 1, pointerEvents: 'none', userSelect: 'none',
            }}>{s.n}</div>

            <div style={{
              width: 48, height: 48, borderRadius: 12,
              background: s.col, display: 'flex',
              alignItems: 'center', justifyContent: 'center',
              fontSize: 22, marginBottom: 18,
            }}>{s.icon}</div>

            <h3 style={{
              fontFamily: 'Syne, sans-serif', fontSize: 17,
              fontWeight: 700, color: 'var(--white)', marginBottom: 9,
            }}>{s.title}</h3>
            <p style={{ fontSize: 13.5, color: 'var(--text2)', lineHeight: 1.65 }}>{s.desc}</p>
          </div>
        ))}
      </div>

      {/* ── Disclaimer */}
      <div style={{ marginTop: 48 }}>
        <DisclaimerBox />
      </div>
    </div>
  )
}
