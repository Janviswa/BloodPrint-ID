import { useTheme } from '../context/ThemeContext'

export default function Background() {
  const { dark } = useTheme()
  if (!dark) return (
    <div style={{
      position:'fixed', inset:0, zIndex:0, pointerEvents:'none',
      backgroundImage:`linear-gradient(rgba(0,119,182,.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,119,182,.04) 1px, transparent 1px)`,
      backgroundSize:'48px 48px',
    }} />
  )
  return (
    <>
      <div style={{
        position:'fixed', inset:0, zIndex:0, pointerEvents:'none',
        backgroundImage:`linear-gradient(rgba(76,201,240,.03) 1px, transparent 1px),
          linear-gradient(90deg, rgba(76,201,240,.03) 1px, transparent 1px)`,
        backgroundSize:'48px 48px',
      }} />
      <div style={{ position:'fixed', top:-200, right:-100,
        width:600, height:600, borderRadius:'50%',
        background:'var(--red)', filter:'blur(140px)',
        opacity:.18, zIndex:0, pointerEvents:'none' }} />
      <div style={{ position:'fixed', bottom:-200, left:-150,
        width:700, height:500, borderRadius:'50%',
        background:'var(--cyan)', filter:'blur(160px)',
        opacity:.08, zIndex:0, pointerEvents:'none' }} />
    </>
  )
}