import { useEffect, useRef, useState } from 'react'

/* ─── Web Audio API Sound Synthesizer (Pure Web Audio, Zero External Assets) ── */
class AmbientSoundEngine {
  constructor() {
    this.ctx = null
    this.muted = true
    this.isPlaying = false
  }

  init() {
    if (this.ctx) return
    const AudioCtx = window.AudioContext || window.webkitAudioContext
    if (!AudioCtx) return
    this.ctx = new AudioCtx()
  }

  toggle() {
    this.init()
    if (!this.ctx) return false
    if (this.ctx.state === 'suspended') {
      this.ctx.resume()
    }
    this.muted = !this.muted
    return !this.muted
  }

  playClick() {
    if (this.muted || !this.ctx) return
    try {
      if (this.ctx.state === 'suspended') this.ctx.resume()
      const now = this.ctx.currentTime
      const osc = this.ctx.createOscillator()
      const gain = this.ctx.createGain()

      osc.type = 'sine'
      osc.frequency.setValueAtTime(800, now)
      osc.frequency.exponentialRampToValueAtTime(400, now + 0.035)

      gain.gain.setValueAtTime(0.015, now)
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.035)

      osc.connect(gain)
      gain.connect(this.ctx.destination)
      osc.start(now)
      osc.stop(now + 0.04)
    } catch {}
  }

  playChime() {
    if (this.muted || !this.ctx) return
    try {
      if (this.ctx.state === 'suspended') this.ctx.resume()
      const now = this.ctx.currentTime
      const osc = this.ctx.createOscillator()
      const gain = this.ctx.createGain()

      osc.type = 'sine'
      osc.frequency.setValueAtTime(587.33, now) // D5
      osc.frequency.exponentialRampToValueAtTime(880, now + 0.15) // A5

      gain.gain.setValueAtTime(0.02, now)
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.3)

      osc.connect(gain)
      gain.connect(this.ctx.destination)
      osc.start(now)
      osc.stop(now + 0.3)
    } catch {}
  }

  playSuccess() {
    if (this.muted || !this.ctx) return
    try {
      if (this.ctx.state === 'suspended') this.ctx.resume()
      const now = this.ctx.currentTime
      const osc = this.ctx.createOscillator()
      const gain = this.ctx.createGain()

      osc.type = 'triangle'
      osc.frequency.setValueAtTime(523.25, now) // C5
      osc.frequency.setValueAtTime(659.25, now + 0.08) // E5
      osc.frequency.setValueAtTime(783.99, now + 0.16) // G5

      gain.gain.setValueAtTime(0.02, now)
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.35)

      osc.connect(gain)
      gain.connect(this.ctx.destination)
      osc.start(now)
      osc.stop(now + 0.35)
    } catch {}
  }

  playAlert() {
    if (this.muted || !this.ctx) return
    try {
      if (this.ctx.state === 'suspended') this.ctx.resume()
      const now = this.ctx.currentTime
      const osc = this.ctx.createOscillator()
      const gain = this.ctx.createGain()

      osc.type = 'sawtooth'
      osc.frequency.setValueAtTime(440, now)
      osc.frequency.setValueAtTime(330, now + 0.1)

      gain.gain.setValueAtTime(0.015, now)
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.25)

      osc.connect(gain)
      gain.connect(this.ctx.destination)
      osc.start(now)
      osc.stop(now + 0.25)
    } catch {}
  }

  playSonar() {
    if (this.muted || !this.ctx) return
    try {
      if (this.ctx.state === 'suspended') this.ctx.resume()
      const now = this.ctx.currentTime
      const osc = this.ctx.createOscillator()
      const gain = this.ctx.createGain()

      osc.type = 'sine'
      osc.frequency.setValueAtTime(1046.5, now) // C6
      osc.frequency.exponentialRampToValueAtTime(523.25, now + 0.4)

      gain.gain.setValueAtTime(0.02, now)
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.45)

      osc.connect(gain)
      gain.connect(this.ctx.destination)
      osc.start(now)
      osc.stop(now + 0.45)
    } catch {}
  }
}

export const soundEngine = new AmbientSoundEngine()

/* ─── Soothing Atmospheric Minimalist Background ─────────────── */
export function AtmosphericBackground() {
  return (
    <div className="atmospheric-bg-wrapper">
      {/* Delicate Architectural Grid */}
      <div className="atmospheric-grid" />
      {/* Soft Vignette Mask */}
      <div className="atmospheric-vignette" />
    </div>
  )
}

/* Backward compatibility export */
export const CinematicBackground = AtmosphericBackground

/* ─── Ultra-Soft Ambient Pointer Glow (GPU-Accelerated) ───────── */
export function AmbientPointerGlow() {
  const glowRef = useRef(null)

  useEffect(() => {
    const glow = glowRef.current
    if (!glow) return

    const handlePointerMove = (e) => {
      glow.style.transform = `translate3d(${e.clientX - 250}px, ${e.clientY - 250}px, 0)`
    }

    const handleClick = () => {
      soundEngine.playClick()
    }

    window.addEventListener('pointermove', handlePointerMove, { passive: true })
    window.addEventListener('click', handleClick)

    return () => {
      window.removeEventListener('pointermove', handlePointerMove)
      window.removeEventListener('click', handleClick)
    }
  }, [])

  return <div id="ambient-pointer-glow" ref={glowRef} />
}

export const CustomCursor = AmbientPointerGlow

/* ─── Spotlight Card (Subtle Interactive Border Illumination) ─── */
export function SpotlightCard({ children, className = '', style, onClick }) {
  const ref = useRef(null)

  const handleMove = e => {
    if (!ref.current) return
    const rect = ref.current.getBoundingClientRect()
    ref.current.style.setProperty('--mx', `${e.clientX - rect.left}px`)
    ref.current.style.setProperty('--my', `${e.clientY - rect.top}px`)
  }

  return (
    <div
      ref={ref}
      onMouseMove={handleMove}
      onClick={onClick}
      className={`spotlight-card ${className}`}
      style={style}
    >
      {children}
    </div>
  )
}

/* ─── Animated Counter ────────────────────────────────────────── */
export function AnimatedCounter({ value, duration = 800 }) {
  const [display, setDisplay] = useState(0)

  useEffect(() => {
    if (typeof value !== 'number') return
    let start = 0
    const end = value
    const startTime = performance.now()

    const update = (now) => {
      const elapsed = now - startTime
      const progress = Math.min(elapsed / duration, 1)
      const ease = 1 - Math.pow(1 - progress, 3)
      const current = Math.round(start + (end - start) * ease)
      setDisplay(current)

      if (progress < 1) {
        requestAnimationFrame(update)
      }
    }

    requestAnimationFrame(update)
  }, [value, duration])

  if (typeof value !== 'number') return <span>{value}</span>
  return <span>{display}</span>
}
