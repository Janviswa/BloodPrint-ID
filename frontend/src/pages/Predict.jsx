// pages/Predict.jsx
import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'
import api from '../utils/api'
import {
  Card, CardTitle, PageHeader, Btn, Spinner,
  ProbBar, MetaChip, DisclaimerBox, Tag,
} from '../components/UI'

const BG_COLORS = {
  'O+':'#27ae60','O-':'#1e8449','A+':'#2980b9','A-':'#1f618d',
  'B+':'#c0392b','B-':'#922b21','AB+':'#7d3c98','AB-':'#6c3483',
}
const PAT_COLORS = { loop:'var(--loop)', whorl:'var(--whorl)', arch:'var(--arch)' }

export default function Predict() {
  const [file,    setFile]    = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result,  setResult]  = useState(null)

  const onDrop = useCallback(accepted => {
    const f = accepted[0]
    if (!f) return
    setFile(f)
    setPreview(URL.createObjectURL(f))
    setResult(null)
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { 'image/*': ['.jpg','.jpeg','.png','.bmp','.tif','.tiff'] },
    maxFiles: 1,
  })

  const analyze = async () => {
    if (!file) return
    setLoading(true)
    const form = new FormData()
    form.append('file', file)
    try {
      const { data } = await api.post('/predict', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setResult(data)
    } catch (e) {
      toast.error(e.response?.data?.error || 'Analysis failed. Check backend.')
    } finally {
      setLoading(false)
    }
  }

  const downloadReport = async () => {
    try {
      const res = await api.get(`/report/${result.id}`, { responseType: 'blob' })
      const url = URL.createObjectURL(res.data)
      const a   = document.createElement('a')
      a.href = url; a.download = `BloodPrint_Report_${result.id}.pdf`; a.click()
      toast.success('Report downloaded!')
    } catch { toast.error('Failed to download report.') }
  }

  return (
    <div style={{ maxWidth: 1120, margin: '0 auto', padding: '52px 28px 80px' }}>
      <PageHeader
        title="Fingerprint Analysis"
        subtitle="Upload a fingerprint image to classify its pattern and view blood group correlations"
      />

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'minmax(0,360px) 1fr',
        gap: 22, alignItems: 'start',
      }}>

        {/* ── LEFT: Upload panel */}
        <div style={{ position: 'sticky', top: 80, display: 'flex', flexDirection: 'column', gap: 16 }}>
          <Card>
            <CardTitle>Upload Image <span style={{ fontSize: 11, fontWeight: 400, color: 'var(--text3)' }}>PNG / JPG / BMP</span></CardTitle>

            {/* Dropzone */}
            <div {...getRootProps()} style={{
              border: `2px dashed ${isDragActive ? 'var(--cyan)' : 'var(--b2)'}`,
              borderRadius: 12, padding: '44px 20px', textAlign: 'center',
              cursor: 'pointer', marginBottom: 16,
              background: isDragActive ? 'var(--cyan3)' : 'transparent',
              transition: 'all .2s',
            }}>
              <input {...getInputProps()} />
              <span style={{ fontSize: 44, display: 'block', marginBottom: 12 }}>🫆</span>
              <p style={{ fontSize: 14, color: 'var(--text2)', marginBottom: 4 }}>
                {isDragActive ? 'Drop it here…' : 'Drag & drop fingerprint here'}
              </p>
              <p style={{ fontSize: 11.5, color: 'var(--text3)' }}>or click to browse files</p>
            </div>

            {/* Preview */}
            {preview && (
              <div style={{
                borderRadius: 10, overflow: 'hidden',
                border: '1px solid var(--b1)', marginBottom: 14,
              }}>
                <img src={preview} alt="Preview" style={{
                  width: '100%', display: 'block',
                  maxHeight: 240, objectFit: 'contain',
                  background: 'var(--bg3)',
                }} />
                <div style={{
                  padding: '8px 13px', background: 'var(--bg3)',
                  fontFamily: 'DM Mono, monospace', fontSize: 11,
                  color: 'var(--text2)', borderTop: '1px solid var(--b1)',
                  whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                }}>
                  {file?.name}
                </div>
              </div>
            )}

            <Btn
              onClick={analyze}
              disabled={!file || loading}
              style={{ width: '100%' }}
            >
              {loading
                ? <><Spinner size={18} /> Analyzing…</>
                : '🔬 Analyze Fingerprint'
              }
            </Btn>
          </Card>
        </div>

        {/* ── RIGHT: Results */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
          {!result && !loading && (
            <Card>
              <div style={{
                display: 'flex', flexDirection: 'column',
                alignItems: 'center', padding: '80px 30px', textAlign: 'center',
              }}>
                <span style={{ fontSize: 56, opacity: .18, marginBottom: 16 }}>🔬</span>
                <p style={{ fontSize: 14, color: 'var(--text3)', lineHeight: 1.65 }}>
                  Upload a fingerprint image and click<br />
                  <strong style={{ color: 'var(--text2)' }}>Analyze Fingerprint</strong> to see results.
                </p>
              </div>
            </Card>
          )}

          {loading && (
            <Card>
              <div style={{
                display: 'flex', flexDirection: 'column',
                alignItems: 'center', gap: 14,
                padding: '72px 40px', color: 'var(--text2)', fontSize: 13,
              }}>
                <Spinner />
                <span>Running EfficientNetB0 analysis…</span>
              </div>
            </Card>
          )}

          {result && !loading && <Results result={result} onDownload={downloadReport} />}
        </div>
      </div>
    </div>
  )
}

/* ── Results sub-component ─────────────────────────────── */
function Results({ result, onDownload }) {
  const info    = result.pattern_info || {}
  const isHi    = !result.low_confidence
  const topBg   = result.top_blood_group
  const patCol  = PAT_COLORS[result.pattern] || 'var(--cyan)'

  const sortedBg = Object.entries(result.blood_group_probs || {})
    .sort((a,b) => b[1]-a[1])

  return (
    <>
      {/* Warnings */}
      {result.low_confidence && (
        <div style={{
          background: 'rgba(244,162,97,.08)', border: '1px solid rgba(244,162,97,.3)',
          borderRadius: 8, padding: '10px 14px',
          display: 'flex', gap: 9, alignItems: 'center',
          fontSize: 12.5, color: 'var(--gold)',
        }}>
          ⚠️ Low confidence — try a clearer image for better accuracy.
        </div>
      )}
      {!result.valid_fingerprint && (
        <div style={{
          background: 'rgba(244,162,97,.08)', border: '1px solid rgba(244,162,97,.3)',
          borderRadius: 8, padding: '10px 14px',
          display: 'flex', gap: 9, alignItems: 'center',
          fontSize: 12.5, color: 'var(--gold)',
        }}>
          ⚠️ Low edge ratio detected — image may not be a fingerprint.
        </div>
      )}

      {/* ── Pattern Card */}
      <Card>
        <CardTitle>Pattern Classification</CardTitle>

        <div style={{
          display: 'flex', alignItems: 'center',
          justifyContent: 'space-between', flexWrap: 'wrap', gap: 12,
          marginBottom: 22,
        }}>
          <span style={{
            fontFamily: 'Syne, sans-serif', fontSize: 32,
            fontWeight: 800, color: patCol,
          }}>
            {result.pattern?.charAt(0).toUpperCase() + result.pattern?.slice(1)} Pattern
          </span>
          <span style={{
            padding: '7px 16px', borderRadius: 20,
            fontSize: 13, fontFamily: 'DM Mono, monospace',
            background: isHi ? 'var(--green2)' : 'var(--gold2)',
            color: isHi ? 'var(--green)' : 'var(--gold)',
            border: `1px solid ${isHi ? 'rgba(123,237,159,.25)' : 'rgba(244,162,97,.25)'}`,
          }}>
            {(result.confidence*100).toFixed(1)}% — {isHi ? '✓ High Confidence' : '⚠ Low Confidence'}
          </span>
        </div>

        {/* Meta chips */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10, marginBottom: 20 }}>
          <MetaChip label="Prevalence"    value={info.prevalence   || 'N/A'} />
          <MetaChip label="Ridge Count"   value={info.ridge_count  || 'N/A'} />
          <MetaChip label="Image Quality" value={result.image_quality} />
          <MetaChip label="Ridge Density" value={result.ridge_density} />
          <MetaChip label="Clarity Score" value={result.clarity_score} />
          <MetaChip label="Edge Ratio"    value={result.edge_ratio} />
        </div>

        {/* Description */}
        <p style={{ fontSize: 13.5, color: 'var(--text2)', lineHeight: 1.72, marginBottom: 18 }}>
          {info.description}
        </p>

        {/* Characteristics */}
        <ul style={{ listStyle: 'none' }}>
          {(info.characteristics || []).map((c, i) => (
            <li key={i} style={{
              fontSize: 13, color: 'var(--text2)',
              padding: '7px 0 7px 20px', position: 'relative',
              borderBottom: i < (info.characteristics.length-1) ? '1px solid var(--b1)' : 'none',
              lineHeight: 1.5,
            }}>
              <span style={{
                position: 'absolute', left: 4, color: 'var(--cyan)',
                fontSize: 16, lineHeight: 1,
              }}>›</span>
              {c}
            </li>
          ))}
        </ul>
      </Card>

      {/* ── Pattern Probabilities */}
      <Card>
        <CardTitle>Pattern Probabilities</CardTitle>
        {Object.entries(result.pattern_probs || {})
          .sort((a,b) => b[1]-a[1])
          .map(([p, v]) => (
            <ProbBar
              key={p}
              label={p.charAt(0).toUpperCase()+p.slice(1)}
              value={v}
              color={PAT_COLORS[p]}
              highlight={p === result.pattern}
            />
          ))
        }
      </Card>

      {/* ── Blood Group */}
      <Card>
        <CardTitle>Blood Group Likelihood
          <span style={{ fontSize: 10, fontWeight: 400, color: 'var(--text3)', textTransform: 'none', letterSpacing: 0 }}>
            Statistical correlation only
          </span>
        </CardTitle>

        {/* Top prediction display */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: 16, marginBottom: 22,
        }}>
          <div style={{
            width: 60, height: 60, borderRadius: '50%',
            background: BG_COLORS[topBg] || '#4cc9f0',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontFamily: 'Syne, sans-serif', fontSize: 17, fontWeight: 800,
            color: '#fff', flexShrink: 0,
          }}>{topBg}</div>
          <div>
            <p style={{ fontSize: 11, color: 'var(--text3)', marginBottom: 3 }}>Top Prediction</p>
            <p style={{ fontFamily: 'Syne, sans-serif', fontSize: 26, fontWeight: 800, color: 'var(--gold)' }}>
              {topBg}
            </p>
            <p style={{ fontFamily: 'DM Mono, monospace', fontSize: 11.5, color: 'var(--text2)' }}>
              {result.top_3?.join('  ·  ')}
            </p>
          </div>
        </div>

        {/* All 8 bars */}
        {sortedBg.map(([bg, prob]) => (
          <ProbBar
            key={bg}
            label={bg}
            value={prob}
            max={1}
            color={BG_COLORS[bg]}
            highlight={bg === topBg}
          />
        ))}
      </Card>

      {/* ── Report + Disclaimer */}
      <Card>
        <CardTitle>Download Report</CardTitle>
        <Btn variant="cyan" onClick={onDownload} style={{ marginBottom: 20 }}>
          ⬇ Download PDF Report
        </Btn>
        <DisclaimerBox />
      </Card>
    </>
  )
}