// pages/History.jsx
import { useState, useEffect } from 'react'
import toast from 'react-hot-toast'
import api from '../utils/api'
import { Card, PageHeader, Btn, Tag, LoadingBox, ProbBar, MetaChip } from '../components/UI'

const PAT_COLORS = { loop:'var(--loop)', whorl:'var(--whorl)', arch:'var(--arch)' }
const BG_COLORS  = {
  'O+':'#27ae60','O-':'#1e8449','A+':'#2980b9','A-':'#1f618d',
  'B+':'#c0392b','B-':'#922b21','AB+':'#7d3c98','AB-':'#6c3483',
}

export default function History() {
  const [rows,      setRows]      = useState([])
  const [loading,   setLoading]   = useState(true)
  const [detail,    setDetail]    = useState(null)
  const [panelOpen, setPanel]     = useState(false)
  const [pdfLoading, setPdfLoad]  = useState(null)   // id of report being generated

  const load = async () => {
    setLoading(true)
    try {
      const { data } = await api.get('/history')
      setRows(data)
    } catch { toast.error('Failed to load history.') }
    finally  { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  const openDetail = async (id) => {
    try {
      const { data } = await api.get(`/history/${id}`)
      setDetail(data)
      setPanel(true)
    } catch { toast.error('Failed to load record.') }
  }

  const closePanel = () => { setPanel(false); setTimeout(() => setDetail(null), 320) }

  const deleteOne = async (id, e) => {
    e.stopPropagation()
    if (!confirm('Delete this record?')) return
    await api.delete(`/history/${id}`)
    toast.success('Record deleted.')
    setRows(r => r.filter(x => x.id !== id))
    if (detail?.id === id) closePanel()
  }

  const clearAll = async () => {
    if (!confirm('Clear all history? This cannot be undone.')) return
    await api.delete('/history')
    setRows([])
    closePanel()
    toast.success('History cleared.')
  }

  const downloadReport = async (id, e) => {
    e?.stopPropagation()
    if (pdfLoading === id) return   // prevent double-click
    setPdfLoad(id)
    const toastId = toast.loading('Generating PDF report… this may take up to 30s', { duration: 40000 })
    try {
      const res = await api.get(`/report/${id}`, {
        responseType: 'blob',
        timeout: 60000,
      })
      const url = URL.createObjectURL(res.data)
      const a   = document.createElement('a')
      a.href = url
      a.download = `BloodPrint_Report_${id}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      setTimeout(() => URL.revokeObjectURL(url), 1000)
      toast.success('Report downloaded!', { id: toastId })
    } catch (err) {
      const status = err?.response?.status
      if (status === 404) toast.error('Report not found.', { id: toastId })
      else toast.error('Failed to generate report. Try again.', { id: toastId })
    } finally {
      setPdfLoad(null)
    }
  }

  return (
    <div style={{ maxWidth: 1120, margin: '0 auto', padding: '52px 28px 80px' }}>
      <PageHeader
        title="Analysis History"
        subtitle={`${rows.length} prediction${rows.length !== 1 ? 's' : ''} saved`}
        right={
          rows.length > 0 && (
            <Btn variant="danger" size="sm" onClick={clearAll}>
              🗑 Clear All
            </Btn>
          )
        }
      />

      {loading ? (
        <Card><LoadingBox label="Loading history…" /></Card>
      ) : rows.length === 0 ? (
        <Card>
          <div style={{ textAlign: 'center', padding: '80px 40px' }}>
            <div style={{ fontSize: 44, opacity: .3, marginBottom: 14 }}>📋</div>
            <p style={{ fontSize: 14, color: 'var(--text3)', lineHeight: 1.65 }}>
              No predictions yet.<br />Go to Analyze to run your first fingerprint analysis.
            </p>
          </div>
        </Card>
      ) : (
        <div style={{
          background: 'var(--bg2)', border: '1px solid var(--b1)',
          borderRadius: 14, overflow: 'hidden',
        }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: 'var(--bg3)', borderBottom: '1px solid var(--b1)' }}>
                {['#','Filename','Pattern','Top Blood Group','Confidence','Quality','Date','Actions'].map(h => (
                  <th key={h} style={{
                    padding: '13px 18px', textAlign: 'left',
                    fontSize: 10.5, fontWeight: 700, textTransform: 'uppercase',
                    letterSpacing: '.08em', color: 'var(--text3)',
                  }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={r.id}
                  onClick={() => openDetail(r.id)}
                  style={{
                    borderBottom: i < rows.length-1 ? '1px solid var(--b1)' : 'none',
                    cursor: 'pointer', transition: 'background .15s',
                  }}
                  onMouseEnter={e => e.currentTarget.style.background = 'var(--bg3)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                >
                  <td style={{ padding: '14px 18px', fontFamily: 'DM Mono, monospace', fontSize: 12, color: 'var(--text3)' }}>
                    {r.id}
                  </td>
                  <td style={{ padding: '14px 18px', fontFamily: 'DM Mono, monospace', fontSize: 11.5, color: 'var(--text2)', maxWidth: 160, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {r.filename}
                  </td>
                  <td style={{ padding: '14px 18px' }}>
                    <Tag variant={r.pattern}>{r.pattern?.charAt(0).toUpperCase()+r.pattern?.slice(1)}</Tag>
                  </td>
                  <td style={{ padding: '14px 18px' }}>
                    <span style={{
                      display: 'inline-block', padding: '3px 10px', borderRadius: 4,
                      fontSize: 12, fontWeight: 700, fontFamily: 'DM Mono, monospace',
                      background: 'rgba(244,162,97,.12)', color: 'var(--gold)',
                    }}>{r.top_bg}</span>
                  </td>
                  <td style={{ padding: '14px 18px', fontFamily: 'DM Mono, monospace', fontSize: 12.5, color: 'var(--text2)' }}>
                    {(r.confidence*100).toFixed(1)}%
                  </td>
                  <td style={{ padding: '14px 18px', fontSize: 13, color: 'var(--text2)' }}>
                    {r.image_quality}
                  </td>
                  <td style={{ padding: '14px 18px', fontFamily: 'DM Mono, monospace', fontSize: 11.5, color: 'var(--text3)' }}>
                    {r.created_at}
                  </td>
                  <td style={{ padding: '14px 18px' }}>
                    <div style={{ display: 'flex', gap: 6 }}>
                      <Btn
                        variant="cyan" size="sm"
                        disabled={pdfLoading === r.id}
                        onClick={e => { e.stopPropagation(); downloadReport(r.id, e) }}
                      >
                        {pdfLoading === r.id ? '⏳ Generating…' : '⬇ PDF'}
                      </Btn>
                      <Btn variant="danger" size="sm" onClick={e => deleteOne(r.id, e)}>
                        🗑
                      </Btn>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ── Detail slide panel overlay */}
      <div
        onClick={closePanel}
        style={{
          position: 'fixed', inset: 0, zIndex: 799,
          background: 'rgba(6,6,15,.5)',
          opacity: panelOpen ? 1 : 0,
          pointerEvents: panelOpen ? 'all' : 'none',
          transition: 'opacity .3s',
        }}
      />

      {/* ── Detail slide panel */}
      <div style={{
        position: 'fixed', top: 0, right: 0, bottom: 0,
        width: 520, maxWidth: '100vw',
        background: 'var(--bg2)', borderLeft: '1px solid var(--b1)',
        zIndex: 800, overflowY: 'auto',
        transform: panelOpen ? 'translateX(0)' : 'translateX(100%)',
        transition: 'transform .32s cubic-bezier(.4,0,.2,1)',
        boxShadow: '-24px 0 80px rgba(0,0,0,.6)',
      }}>
        {detail && <DetailPanel record={detail} onClose={closePanel} onDownload={downloadReport} pdfLoading={pdfLoading} />}
      </div>
    </div>
  )
}

function DetailPanel({ record, onClose, onDownload, pdfLoading }) {
  const r      = record.result || {}
  const info   = r.pattern_info || {}
  const patCol = PAT_COLORS[r.pattern] || 'var(--cyan)'
  const topBg  = r.top_blood_group

  const sortedBg = Object.entries(r.blood_group_probs || {}).sort((a,b) => b[1]-a[1])

  return (
    <>
      {/* Sticky header */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '20px 24px', borderBottom: '1px solid var(--b1)',
        position: 'sticky', top: 0, background: 'var(--bg2)', zIndex: 10,
      }}>
        <div>
          <p style={{ fontFamily: 'Syne, sans-serif', fontSize: 18, fontWeight: 800, color: 'var(--white)' }}>
            Record #{record.id}
          </p>
          <p style={{ fontSize: 11.5, fontFamily: 'DM Mono, monospace', color: 'var(--text2)', marginTop: 3 }}>
            {record.filename}  ·  {record.created_at}
          </p>
        </div>
        <button onClick={onClose} style={{
          width: 32, height: 32, borderRadius: 8,
          background: 'var(--bg3)', border: 'none',
          color: 'var(--text2)', fontSize: 18, cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>✕</button>
      </div>

      <div style={{ padding: '22px 24px', display: 'flex', flexDirection: 'column', gap: 20 }}>
        {/* Pattern */}
        <div>
          <p style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '.08em', color: 'var(--text3)', marginBottom: 8 }}>Pattern</p>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
            <span style={{ fontFamily: 'Syne, sans-serif', fontSize: 26, fontWeight: 800, color: patCol }}>
              {r.pattern?.charAt(0).toUpperCase()+r.pattern?.slice(1)} Pattern
            </span>
            <span style={{ fontFamily: 'DM Mono, monospace', fontSize: 13, color: 'var(--text2)' }}>
              {(r.confidence*100).toFixed(1)}% confidence
            </span>
          </div>
        </div>

        {/* Chips */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
          <MetaChip label="Quality"  value={r.image_quality} />
          <MetaChip label="Density"  value={r.ridge_density} />
          <MetaChip label="Clarity"  value={r.clarity_score} />
          <MetaChip label="Top BG"   value={topBg} />
        </div>

        {/* Blood group bars */}
        <div>
          <p style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '.08em', color: 'var(--text3)', marginBottom: 10 }}>
            Blood Group Likelihoods
          </p>
          {sortedBg.map(([bg, prob]) => (
            <ProbBar
              key={bg} label={bg} value={prob}
              max={1}
              color={BG_COLORS[bg]}
              highlight={bg === topBg}
            />
          ))}
        </div>

        {/* Actions */}
        <div style={{ display: 'flex', gap: 10, paddingTop: 4 }}>
          <Btn
            variant="cyan"
            disabled={pdfLoading === record.id}
            onClick={() => onDownload(record.id)}
          >
            {pdfLoading === record.id ? '⏳ Generating…' : '⬇ Download PDF'}
          </Btn>
          <Btn variant="ghost" onClick={onClose}>Close</Btn>
        </div>
      </div>
    </>
  )
}