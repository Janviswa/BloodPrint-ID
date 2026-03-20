// pages/Research.jsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Btn, DisclaimerBox } from '../components/UI'

// ── Data ─────────────────────────────────────────────────────
const PATTERNS = [
  {
    id: 'loop',
    name: 'Loop Pattern',
    color: 'var(--loop)',
    bg: 'rgba(76,201,240,.08)',
    border: 'rgba(76,201,240,.2)',
    prevalence: '~65%',
    pop: 'Most common fingerprint pattern worldwide',
    icon: '〜',
    subtypes: ['Ulnar Loop — ridges open toward little finger (most common)', 'Radial Loop — ridges open toward thumb (less common)'],
    description: `A loop pattern is formed when ridge lines enter from one side of the finger, curve smoothly around a central focal point called the core, and exit from the same side they entered. This creates a characteristic "U" or hook shape when viewed from above.

The loop is by far the most prevalent fingerprint pattern, found in approximately 60–70% of all human fingerprints. Its high frequency makes it a key reference point in both forensic identification and dermatoglyphic research.`,
    characteristics: [
      'Exactly one delta point (triangular formation of ridges)',
      'Ridges open on one side only — the open end faces either the thumb or little finger',
      'Core is the innermost turning point of the loop',
      'Ridge count: number of ridges crossed between the delta and core',
      'Ulnar loops open toward the ulna bone (little finger side)',
      'Radial loops open toward the radius bone (thumb side)',
    ],
    forensic: 'Ridge count between core and delta is used for sub-classification. Loops with fewer than 10 ridges are "small loops"; 10–14 are "medium"; 15+ are "large loops".',
    blood_correlation: 'Research indicates Loop patterns correlate most strongly with blood groups O+ (~28%) and A+ (~22%), with weaker correlations to B+, B−, and AB types.',
    ridgeCount: 'Typically 5–15 ridges between delta and core',
  },
  {
    id: 'whorl',
    name: 'Whorl Pattern',
    color: 'var(--whorl)',
    bg: 'rgba(247,37,133,.08)',
    border: 'rgba(247,37,133,.2)',
    prevalence: '~30%',
    pop: 'Second most common pattern globally',
    icon: '◎',
    subtypes: [
      'Plain Whorl — concentric circular or oval ridges',
      'Central Pocket Loop Whorl — loop with a whorl in center',
      'Double Loop Whorl — two separate loop formations',
      'Accidental Whorl — irregular, does not fit other types',
    ],
    description: `A whorl pattern occurs when ridge lines form one or more complete circular, spiral, or oval circuits around a central core point. Unlike the loop, at least one ridge in a whorl makes a complete 360-degree revolution.

Whorls are identified by the presence of two delta points — one on each side of the pattern. The relationship between the line connecting the deltas and the innermost whorl tracing is used to sub-classify whorl types.`,
    characteristics: [
      'Always has exactly two delta points (left and right)',
      'At least one ridge completes a full 360° circuit around the core',
      'Core is centrally positioned within the ridge circuits',
      'Inner tracing: line traced from right delta innermost ridge',
      'Classification: Inner (I), Meeting (M), or Outer (O) tracing',
      'Double loop whorl contains two completely separate loop systems',
    ],
    forensic: 'Whorls require "tracing" for classification — the examiner traces from the right delta along the ridge to the left delta. Meeting tracing is the most common. Plain whorls are the most frequent whorl sub-type.',
    blood_correlation: 'Whorl patterns show the strongest correlation with blood group B+ (~28%) followed by AB+ (~14%) and O+ (~18%). The B+ correlation is notably stronger than in other pattern types.',
    ridgeCount: 'Ridge count not used; inner tracing classification applies',
  },
  {
    id: 'arch',
    name: 'Arch Pattern',
    color: 'var(--arch)',
    bg: 'rgba(123,237,159,.08)',
    border: 'rgba(123,237,159,.2)',
    prevalence: '~5%',
    pop: 'Rarest fingerprint pattern in all populations',
    icon: '∩',
    subtypes: [
      'Plain Arch — ridges rise gently like a wave from side to side',
      'Tented Arch — sharp upward spike or tent-like thrust at center',
    ],
    description: `An arch pattern is the simplest and rarest of all fingerprint patterns. Ridge lines enter from one side of the finger, rise in the center to form a wave or tent-like shape, and exit from the opposite side. There are no deltas and no cores.

The absence of a delta and a core is the defining characteristic of arches. Because of this, arches cannot have a ridge count in the forensic sense. Tented arches are distinguished by a sharp upward thrust or spike at the center, which may sometimes give the appearance of an incomplete loop.`,
    characteristics: [
      'No delta points whatsoever (key distinguishing feature)',
      'No core present',
      'Ridges flow smoothly from one side to the other',
      'Plain arch: gentle, wave-like elevation at center',
      'Tented arch: sharp upward thrust or spike at center',
      'Tented arches may contain an angle, an upthrust, or a loop',
    ],
    forensic: 'Arches are the simplest pattern to classify but can be confused with tented arches or very low-count loops. The absence of a delta is the definitive test. Tented arches often look like loops but fail the delta requirement.',
    blood_correlation: 'Arch patterns show unusual correlation with AB+ (~20%) and A+ (~22%), which is higher than expected given arches\' rarity. This is a notable finding in dermatoglyphic research literature.',
    ridgeCount: 'No ridge count possible — no delta or core to measure from',
  },
]

const PAPERS = [
  {
    authors: 'Dogra, T.D. et al.',
    year: '2014',
    title: 'Fingerprint patterns and their correlation with ABO blood groups',
    journal: 'Journal of Forensic Medicine and Toxicology',
    finding: 'Established statistically significant correlations between loop/whorl/arch patterns and ABO blood group distribution in a North Indian population sample of 1,000 subjects.',
    key: 'Loop → O+, Whorl → B+, Arch → AB+',
  },
  {
    authors: 'Nayak, V.C. et al.',
    year: '2010',
    title: 'Correlating fingerprint patterns with blood groups and sex',
    journal: 'Journal of Forensic and Legal Medicine',
    finding: 'Found significant associations between fingerprint patterns, ABO blood groups, and sex. Loop patterns were most common in O+ individuals; whorls were elevated in B+ subjects.',
    key: 'Confirmed Dogra findings in South Indian population',
  },
  {
    authors: 'Igbigbi, P.S. & Thumb, B.',
    year: '2002',
    title: 'Dermatoglyphic patterns of Ugandan and Tanzanian subjects',
    journal: 'West African Journal of Medicine',
    finding: 'Cross-population study comparing East African fingerprint distributions with European data. Established that the loop–whorl–arch frequency hierarchy holds across ethnic groups with minor variation.',
    key: 'Cross-ethnic validity of pattern correlations',
  },
  {
    authors: 'Cummins, H. & Midlo, C.',
    year: '1961',
    title: 'Finger Prints, Palms and Soles: An Introduction to Dermatoglyphics',
    journal: 'Dover Publications (Book)',
    finding: 'The foundational reference text for dermatoglyphics. Established the classification system for fingerprint patterns still used globally, and first documented population-level frequency distributions.',
    key: 'Foundational classification system — still in use today',
  },
]

const CONCEPTS = [
  {
    term: 'Dermatoglyphics',
    def: 'The scientific study of skin ridge patterns on fingers, palms, toes, and soles. The word comes from Greek: "derma" (skin) + "glyph" (carving). These patterns are genetically determined and remain unchanged throughout a person\'s lifetime.',
  },
  {
    term: 'Delta',
    def: 'A triangular area where three ridge systems meet and diverge. Loops have exactly one delta; whorls have exactly two; arches have none. The delta is used as a reference point for ridge counting.',
  },
  {
    term: 'Core',
    def: 'The innermost portion of a loop or whorl pattern — the approximate center of the pattern. In loops, it is the top of the innermost recurving ridge. In whorls, it is the center of the innermost circuit.',
  },
  {
    term: 'Ridge Count',
    def: 'The number of ridges intersected by a straight line drawn from the delta to the core. Used for sub-classifying loop patterns. Arches have no ridge count. Whorls use inner tracing instead.',
  },
  {
    term: 'ABO Blood Group System',
    def: 'A classification of human blood based on the presence or absence of A and B antigens on red blood cells. The four main types are A, B, AB, and O. Combined with the Rh factor (+/−), this gives 8 common blood groups.',
  },
  {
    term: 'Rh Factor',
    def: 'A protein on the surface of red blood cells. If present, the person is Rh positive (+); if absent, Rh negative (−). The Rh protein is controlled by a gene cluster separate from the ABO genes.',
  },
  {
    term: 'Statistical Correlation',
    def: 'A relationship between two variables — here, fingerprint pattern type and blood group frequency — observed in population-level data. A correlation does NOT mean causation, and cannot predict an individual\'s blood group.',
  },
  {
    term: 'Developmental Window',
    def: 'Fingerprint ridge patterns form between weeks 10–16 of fetal development. Interestingly, ABO blood group antigens also begin expressing during this same developmental period, which may explain why weak correlations exist.',
  },
]

// ── Sub-components ────────────────────────────────────────────
function PatternCard({ p, expanded, onClick }) {
  return (
    <div style={{
      background: expanded ? p.bg : 'var(--bg2)',
      border: `1px solid ${expanded ? p.border : 'var(--b1)'}`,
      borderRadius: 16, overflow: 'hidden',
      transition: 'all .3s',
    }}>
      {/* Header */}
      <div onClick={onClick} style={{
        padding: '24px 26px', cursor: 'pointer',
        display: 'flex', alignItems: 'center', gap: 18,
      }}>
        <div style={{
          width: 56, height: 56, borderRadius: 14,
          background: p.bg, border: `1.5px solid ${p.border}`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 26, color: p.color, flexShrink: 0,
          fontFamily: 'Syne, sans-serif',
        }}>{p.icon}</div>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
            <h3 style={{ fontFamily: 'Syne, sans-serif', fontSize: 20, fontWeight: 800, color: p.color }}>
              {p.name}
            </h3>
            <span style={{
              background: p.bg, border: `1px solid ${p.border}`,
              color: p.color, fontSize: 11, fontWeight: 700,
              padding: '3px 10px', borderRadius: 20,
              fontFamily: 'DM Mono, monospace',
            }}>{p.prevalence} of population</span>
          </div>
          <p style={{ fontSize: 13, color: 'var(--text2)', marginTop: 4 }}>{p.pop}</p>
        </div>
        <span style={{ color: 'var(--text3)', fontSize: 18, transition: 'transform .3s',
          transform: expanded ? 'rotate(90deg)' : 'rotate(0)' }}>›</span>
      </div>

      {/* Expanded content */}
      {expanded && (
        <div style={{ padding: '0 26px 26px', borderTop: `1px solid ${p.border}` }}>

          {/* Sub-types */}
          <div style={{ marginTop: 20, marginBottom: 16 }}>
            <p style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase',
              letterSpacing: '.08em', color: 'var(--text3)', marginBottom: 10 }}>Sub-types</p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {p.subtypes.map((s, i) => (
                <div key={i} style={{
                  display: 'flex', gap: 10, alignItems: 'flex-start',
                  background: 'var(--bg3)', borderRadius: 8, padding: '8px 12px',
                }}>
                  <span style={{ color: p.color, fontWeight: 700, flexShrink: 0 }}>0{i+1}</span>
                  <span style={{ fontSize: 13, color: 'var(--text2)', lineHeight: 1.5 }}>{s}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Description */}
          <p style={{ fontSize: 13.5, color: 'var(--text2)', lineHeight: 1.75, marginBottom: 18 }}>
            {p.description.split('\n\n').map((para, i) => (
              <span key={i}>{para}<br/><br/></span>
            ))}
          </p>

          {/* Two columns */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
            <div style={{ background: 'var(--bg3)', borderRadius: 10, padding: '16px' }}>
              <p style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase',
                letterSpacing: '.08em', color: 'var(--text3)', marginBottom: 10 }}>Key Characteristics</p>
              {p.characteristics.map((c, i) => (
                <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 6 }}>
                  <span style={{ color: p.color, fontSize: 14, lineHeight: 1, flexShrink: 0 }}>›</span>
                  <span style={{ fontSize: 12.5, color: 'var(--text2)', lineHeight: 1.5 }}>{c}</span>
                </div>
              ))}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <div style={{ background: 'var(--bg3)', borderRadius: 10, padding: '16px', flex: 1 }}>
                <p style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase',
                  letterSpacing: '.08em', color: 'var(--text3)', marginBottom: 8 }}>Forensic Notes</p>
                <p style={{ fontSize: 12.5, color: 'var(--text2)', lineHeight: 1.6 }}>{p.forensic}</p>
              </div>
              <div style={{ background: p.bg, border: `1px solid ${p.border}`,
                borderRadius: 10, padding: '16px' }}>
                <p style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase',
                  letterSpacing: '.08em', color: p.color, marginBottom: 8 }}>Blood Group Correlation</p>
                <p style={{ fontSize: 12.5, color: 'var(--text2)', lineHeight: 1.6 }}>{p.blood_correlation}</p>
              </div>
            </div>
          </div>

          <div style={{ background: 'var(--bg3)', borderRadius: 8, padding: '10px 14px',
            display: 'flex', gap: 8, alignItems: 'center' }}>
            <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--text3)',
              textTransform: 'uppercase', letterSpacing: '.06em' }}>Ridge Count:</span>
            <span style={{ fontSize: 13, color: 'var(--text)', fontFamily: 'DM Mono, monospace' }}>
              {p.ridgeCount}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}

export default function Research() {
  const nav = useNavigate()
  const [openPattern, setOpenPattern] = useState('loop')
  const [openConcept, setOpenConcept] = useState(null)

  return (
    <div style={{ maxWidth: 1040, margin: '0 auto', padding: '52px 28px 100px' }}>

      {/* ── Hero */}
      <div style={{ marginBottom: 60, position: 'relative' }}>
        <div style={{
          position: 'absolute', top: -40, left: '50%', transform: 'translateX(-50%)',
          width: 600, height: 300,
          background: 'radial-gradient(ellipse, rgba(76,201,240,.07) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 8,
          background: 'var(--cyan2)', border: '1px solid rgba(76,201,240,.2)',
          color: 'var(--cyan)', fontSize: 11, fontWeight: 700,
          textTransform: 'uppercase', letterSpacing: '.1em',
          padding: '5px 14px', borderRadius: 20, marginBottom: 20,
        }}>🔬 Research & Science</div>

        <h1 style={{
          fontFamily: 'Syne, sans-serif', fontWeight: 800,
          fontSize: 'clamp(32px,5vw,56px)', color: 'var(--white)',
          letterSpacing: '-1px', lineHeight: 1.1, marginBottom: 16,
        }}>
          The Science Behind<br />
          <span style={{ color: 'var(--cyan)' }}>BloodPrint ID</span>
        </h1>
        <p style={{ fontSize: 16, color: 'var(--text2)', maxWidth: 620, lineHeight: 1.7, marginBottom: 28 }}>
          Dermatoglyphics is the scientific study of fingerprint ridge patterns. Research spanning
          six decades has found statistically significant — though weak — correlations between
          fingerprint pattern types and ABO blood groups.
        </p>
        <Btn onClick={() => nav('/predict')}>Try the Analysis →</Btn>
      </div>

      {/* ── How correlation works */}
      <section style={{ marginBottom: 64 }}>
        <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: 26, fontWeight: 700,
          color: 'var(--white)', marginBottom: 8 }}>How the Correlation Works</h2>
        <p style={{ fontSize: 14, color: 'var(--text2)', marginBottom: 28 }}>
          Why would fingerprints and blood groups be related?
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 16, marginBottom: 28 }}>
          {[
            { n:'01', color:'var(--red)', title:'Same Developmental Window',
              text:'Fingerprint ridge patterns form in weeks 10–16 of fetal development. ABO blood group antigens begin expressing on red blood cells during this exact same period — a likely reason for the weak correlation.' },
            { n:'02', color:'var(--cyan)', title:'Shared Gene Clusters',
              text:'The HOX gene clusters active during dermal ridge formation are located near chromosomal regions involved in blood group antigen expression, suggesting a developmental co-regulation mechanism.' },
            { n:'03', color:'var(--green)', title:'Population Statistics',
              text:'The correlations are population-level statistical observations — not individual predictions. A person with a loop pattern is statistically more likely to be O+, but this cannot determine any individual\'s blood group.' },
          ].map((s,i) => (
            <div key={i} style={{ background: 'var(--bg2)', border: '1px solid var(--b1)',
              borderRadius: 14, padding: '24px 22px' }}>
              <div style={{ fontFamily: 'Syne, sans-serif', fontSize: 11, fontWeight: 700,
                color: s.color, marginBottom: 12, letterSpacing: '.06em' }}>{s.n}</div>
              <h3 style={{ fontFamily: 'Syne, sans-serif', fontSize: 15, fontWeight: 700,
                color: 'var(--white)', marginBottom: 9 }}>{s.title}</h3>
              <p style={{ fontSize: 13, color: 'var(--text2)', lineHeight: 1.65 }}>{s.text}</p>
            </div>
          ))}
        </div>

        {/* Honest limitations box */}
        <div style={{ background: 'rgba(244,162,97,.06)', border: '1px solid rgba(244,162,97,.2)',
          borderRadius: 12, padding: '20px 22px',
          display: 'flex', gap: 14, alignItems: 'flex-start' }}>
          <span style={{ fontSize: 20, flexShrink: 0 }}>⚠️</span>
          <div>
            <p style={{ fontSize: 12, fontWeight: 700, color: 'var(--gold)',
              textTransform: 'uppercase', letterSpacing: '.06em', marginBottom: 6 }}>
              Honest Limitations of This Research
            </p>
            <p style={{ fontSize: 13, color: 'var(--text2)', lineHeight: 1.65 }}>
              The correlations between fingerprint patterns and blood groups are <strong>weak and statistical</strong> in nature —
              typically explaining only 1–5% of variance in blood group distribution.
              Sample sizes in the original studies ranged from 500 to 2,000 subjects, limiting generalizability.
              This tool should be treated as an educational exploration of dermatoglyphics,
              <strong> never as a substitute for laboratory blood typing.</strong>
            </p>
          </div>
        </div>
      </section>

      {/* ── Fingerprint Patterns */}
      <section style={{ marginBottom: 64 }}>
        <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: 26, fontWeight: 700,
          color: 'var(--white)', marginBottom: 8 }}>Fingerprint Pattern Types</h2>
        <p style={{ fontSize: 14, color: 'var(--text2)', marginBottom: 24 }}>
          Click each pattern to explore its anatomy, characteristics, and blood group correlations.
        </p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {PATTERNS.map(p => (
            <PatternCard
              key={p.id} p={p}
              expanded={openPattern === p.id}
              onClick={() => setOpenPattern(openPattern === p.id ? null : p.id)}
            />
          ))}
        </div>
      </section>

      {/* ── Blood Group Correlation Table */}
      <section style={{ marginBottom: 64 }}>
        <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: 26, fontWeight: 700,
          color: 'var(--white)', marginBottom: 8 }}>Blood Group Probability Table</h2>
        <p style={{ fontSize: 14, color: 'var(--text2)', marginBottom: 24 }}>
          Research-based probability distribution for all 8 blood groups across the 3 pattern types.
        </p>

        <div style={{ background: 'var(--bg2)', border: '1px solid var(--b1)', borderRadius: 14, overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: 'var(--bg3)' }}>
                {['Blood Group','Loop (~65%)','Whorl (~30%)','Arch (~5%)'].map(h => (
                  <th key={h} style={{ padding: '13px 18px', textAlign: 'left',
                    fontSize: 11, fontWeight: 700, textTransform: 'uppercase',
                    letterSpacing: '.07em', color: 'var(--text3)',
                    borderBottom: '1px solid var(--b1)' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[
                ['O+',  '28.0%','18.0%','18.0%'],
                ['A+',  '22.0%','15.0%','22.0%'],
                ['B+',  '16.0%','28.0%','12.0%'],
                ['AB+', '10.0%','14.0%','20.0%'],
                ['O-',  ' 8.0%',' 5.0%',' 6.0%'],
                ['A-',  ' 6.0%',' 4.0%',' 8.0%'],
                ['B-',  ' 5.0%',' 8.0%',' 4.0%'],
                ['AB-', ' 5.0%',' 8.0%','10.0%'],
              ].map((row, i) => (
                <tr key={row[0]} style={{ borderBottom: i<7 ? '1px solid var(--b1)' : 'none',
                  background: i%2===0 ? 'var(--bg2)' : 'var(--bg)' }}>
                  <td style={{ padding: '12px 18px', fontFamily: 'DM Mono, monospace',
                    fontSize: 13, fontWeight: 700, color: 'var(--gold)' }}>{row[0]}</td>
                  {[row[1],row[2],row[3]].map((v,ci) => (
                    <td key={ci} style={{ padding: '12px 18px',
                      fontFamily: 'DM Mono, monospace', fontSize: 13,
                      color: 'var(--text2)' }}>{v}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ padding: '12px 18px', borderTop: '1px solid var(--b1)',
            background: 'var(--bg3)', fontSize: 11, color: 'var(--text3)' }}>
            Sources: Dogra et al. (2014), Nayak et al. (2010), Igbigbi & Thumb (2002)
          </div>
        </div>
      </section>

      {/* ── Research Papers */}
      <section style={{ marginBottom: 64 }}>
        <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: 26, fontWeight: 700,
          color: 'var(--white)', marginBottom: 8 }}>Research References</h2>
        <p style={{ fontSize: 14, color: 'var(--text2)', marginBottom: 24 }}>
          The four foundational papers that form the scientific basis of BloodPrint ID.
        </p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {PAPERS.map((p, i) => (
            <div key={i} style={{ background: 'var(--bg2)', border: '1px solid var(--b1)',
              borderRadius: 12, padding: '22px 24px',
              display: 'flex', gap: 16, alignItems: 'flex-start' }}>
              <div style={{
                width: 36, height: 36, borderRadius: 10, background: 'var(--bg3)',
                border: '1px solid var(--b1)', display: 'flex', alignItems: 'center',
                justifyContent: 'center', fontSize: 13, fontWeight: 700,
                fontFamily: 'DM Mono, monospace', color: 'var(--cyan)', flexShrink: 0,
              }}>{String(i+1).padStart(2,'0')}</div>
              <div style={{ flex: 1 }}>
                <p style={{ fontFamily: 'Syne, sans-serif', fontSize: 14, fontWeight: 700,
                  color: 'var(--white)', marginBottom: 4 }}>{p.title}</p>
                <p style={{ fontSize: 12, color: 'var(--cyan)', marginBottom: 8,
                  fontFamily: 'DM Mono, monospace' }}>
                  {p.authors} · {p.year} · <em style={{ color: 'var(--text2)' }}>{p.journal}</em>
                </p>
                <p style={{ fontSize: 13, color: 'var(--text2)', lineHeight: 1.65, marginBottom: 10 }}>
                  {p.finding}
                </p>
                <span style={{
                  background: 'var(--cyan2)', border: '1px solid rgba(76,201,240,.2)',
                  color: 'var(--cyan)', fontSize: 11, padding: '3px 10px', borderRadius: 20,
                  fontFamily: 'DM Mono, monospace',
                }}>Key finding: {p.key}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Key Concepts Glossary */}
      <section style={{ marginBottom: 64 }}>
        <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: 26, fontWeight: 700,
          color: 'var(--white)', marginBottom: 8 }}>Key Concepts Glossary</h2>
        <p style={{ fontSize: 14, color: 'var(--text2)', marginBottom: 24 }}>
          Essential terms used in dermatoglyphics and blood group science.
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2,1fr)', gap: 10 }}>
          {CONCEPTS.map((c, i) => (
            <div key={i}
              onClick={() => setOpenConcept(openConcept === i ? null : i)}
              style={{
                background: openConcept===i ? 'var(--bg3)' : 'var(--bg2)',
                border: `1px solid ${openConcept===i ? 'var(--b2)' : 'var(--b1)'}`,
                borderRadius: 10, padding: '14px 16px', cursor: 'pointer',
                transition: 'all .2s',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontFamily: 'Syne, sans-serif', fontSize: 14,
                  fontWeight: 700, color: 'var(--white)' }}>{c.term}</span>
                <span style={{ color: 'var(--text3)', transition: 'transform .2s',
                  transform: openConcept===i ? 'rotate(90deg)' : 'none' }}>›</span>
              </div>
              {openConcept === i && (
                <p style={{ fontSize: 13, color: 'var(--text2)', lineHeight: 1.65,
                  marginTop: 10, paddingTop: 10, borderTop: '1px solid var(--b1)' }}>
                  {c.def}
                </p>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* ── Model section */}
      <section style={{ marginBottom: 64 }}>
        <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: 26, fontWeight: 700,
          color: 'var(--white)', marginBottom: 8 }}>The AI Model</h2>
        <p style={{ fontSize: 14, color: 'var(--text2)', marginBottom: 24 }}>
          How BloodPrint ID classifies fingerprint patterns.
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          {[
            { title:'EfficientNetB0', color:'var(--cyan)',
              desc:'The base feature extractor. Pre-trained on ImageNet with 5.3M parameters — lighter and faster than ResNet50 while achieving comparable or better accuracy on small datasets.' },
            { title:'CLAHE Enhancement', color:'var(--green)',
              desc:'Contrast Limited Adaptive Histogram Equalization is applied to each image channel before prediction. This corrects uneven scanner lighting that would otherwise degrade classification accuracy.' },
            { title:'Two-Phase Training', color:'var(--gold)',
              desc:'Phase 1 trains only the classification head while the EfficientNet base is frozen. Phase 2 fine-tunes the top 20 base layers at a much lower learning rate (1e-5 vs 1e-3).' },
            { title:'KMeans Clustering', color:'var(--whorl)',
              desc:'Since SOCOFing dataset images are not labeled by pattern type, KMeans clustering on extracted features groups them into 3 clusters (loop/whorl/arch) for supervised training.' },
          ].map((m,i) => (
            <div key={i} style={{ background: 'var(--bg2)', border: '1px solid var(--b1)',
              borderRadius: 12, padding: '20px 22px' }}>
              <p style={{ fontFamily: 'Syne, sans-serif', fontSize: 15, fontWeight: 700,
                color: m.color, marginBottom: 8 }}>{m.title}</p>
              <p style={{ fontSize: 13, color: 'var(--text2)', lineHeight: 1.65 }}>{m.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA */}
      <DisclaimerBox />
      <div style={{ textAlign: 'center', marginTop: 40 }}>
        <p style={{ fontSize: 14, color: 'var(--text2)', marginBottom: 18 }}>
          Ready to try the analysis on your own fingerprint image?
        </p>
        <Btn onClick={() => nav('/predict')}>Start Fingerprint Analysis →</Btn>
      </div>
    </div>
  )
}