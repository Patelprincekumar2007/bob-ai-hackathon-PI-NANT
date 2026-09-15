import { useState, useEffect } from 'react'
import Dashboard   from './components/Dashboard'
import Shipments   from './components/Shipments'
import Disruptions from './components/Disruptions'
import Fleet       from './components/Fleet'
import ColdChain   from './components/ColdChain'
import { apiFetch } from './api'

const NAV = [
  { id: 'dashboard',   label: 'Dashboard',    icon: '◈' },
  { id: 'shipments',   label: 'Shipments',    icon: '◻' },
  { id: 'disruptions', label: 'Disruptions',  icon: '◬' },
  { id: 'fleet',       label: 'Fleet',        icon: '◉' },
  { id: 'cold-chain',  label: 'Cold Chain',   icon: '◎' },
]

const PAGES = {
  dashboard:   <Dashboard />,
  shipments:   <Shipments />,
  disruptions: <Disruptions />,
  fleet:       <Fleet />,
  'cold-chain':<ColdChain />,
}

export default function App() {
  const [page, setPage]   = useState('dashboard')
  const [aiOn, setAiOn]   = useState(false)
  const [sideOpen, setSO] = useState(true)

  useEffect(() => {
    apiFetch('/api/ai/status').then(d => setAiOn(d.configured)).catch(() => {})
  }, [])

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: '#070B14' }}>

      {/* ── Sidebar ────────────────────────────────────────────────── */}
      <aside
        className="flex flex-col flex-shrink-0 overflow-y-auto transition-all duration-300"
        style={{
          width: sideOpen ? 220 : 60,
          background: '#080C17',
          borderRight: '1px solid rgba(56,189,248,0.07)',
        }}
      >
        {/* Logo */}
        <div className="p-4 pb-3" style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
          <div className="flex items-center gap-3">
            <div
              className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 text-lg font-bold"
              style={{ background: 'linear-gradient(135deg,#38BDF8,#818CF8)', boxShadow: '0 4px 12px rgba(56,189,248,0.3)' }}
            >⚓</div>
            {sideOpen && (
              <div>
                <div className="font-head font-extrabold text-sm leading-tight" style={{ color: '#F1F5F9', letterSpacing: '-0.01em' }}>SmartRoute AI</div>
                <div className="text-xs font-semibold tracking-widest" style={{ color: '#334155', fontSize: '0.6rem' }}>CONTROL TOWER</div>
              </div>
            )}
          </div>
          {/* collapse button */}
          <button
            onClick={() => setSO(o => !o)}
            className="mt-3 w-full flex justify-center items-center h-6 rounded-lg transition-colors"
            style={{ background: 'rgba(255,255,255,0.03)', color: '#334155' }}
            title={sideOpen ? 'Collapse' : 'Expand'}
          >
            <span className="text-xs">{sideOpen ? '◀' : '▶'}</span>
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 p-2 pt-3">
          {sideOpen && <div className="text-xs font-bold tracking-widest px-2 mb-2" style={{ color: '#1E293B', fontSize: '0.6rem' }}>NAVIGATION</div>}
          {NAV.map(n => {
            const active = page === n.id
            return (
              <button
                key={n.id}
                onClick={() => setPage(n.id)}
                title={n.label}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl mb-1 text-sm font-medium transition-all duration-150"
                style={{
                  background: active ? 'rgba(56,189,248,0.1)' : 'transparent',
                  color: active ? '#38BDF8' : '#475569',
                  border: active ? '1px solid rgba(56,189,248,0.2)' : '1px solid transparent',
                  justifyContent: sideOpen ? 'flex-start' : 'center',
                }}
              >
                <span className="text-base flex-shrink-0">{n.icon}</span>
                {sideOpen && <span>{n.label}</span>}
                {active && sideOpen && <span className="ml-auto w-1.5 h-1.5 rounded-full" style={{ background: '#38BDF8' }} />}
              </button>
            )
          })}
        </nav>

        {/* AI Status */}
        <div className="p-3" style={{ borderTop: '1px solid rgba(255,255,255,0.04)' }}>
          <div
            className="rounded-xl p-3"
            style={{
              background: aiOn ? 'rgba(52,211,153,0.06)' : 'rgba(251,191,36,0.06)',
              border: `1px solid ${aiOn ? 'rgba(52,211,153,0.15)' : 'rgba(251,191,36,0.15)'}`,
            }}
          >
            <div className="flex items-center gap-2">
              <span
                className="pulse-dot w-2 h-2 rounded-full flex-shrink-0"
                style={{ background: aiOn ? '#34D399' : '#FBBF24', boxShadow: `0 0 6px ${aiOn ? '#34D399' : '#FBBF24'}` }}
              />
              {sideOpen && (
                <span className="text-xs font-bold" style={{ color: aiOn ? '#34D399' : '#FBBF24' }}>
                  {aiOn ? 'watsonx.ai Live' : 'Demo Mode'}
                </span>
              )}
            </div>
            {sideOpen && (
              <div className="text-xs mt-1 ml-4" style={{ color: '#334155' }}>
                {aiOn ? 'IBM watsonx.ai connected' : 'Mock AI simulation'}
              </div>
            )}
          </div>
          {sideOpen && (
            <div className="text-xs mt-3 text-center font-medium" style={{ color: '#1E293B' }}>
              Team PI-NANT · IBM Hackathon
            </div>
          )}
        </div>
      </aside>

      {/* ── Main content ───────────────────────────────────────────── */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto p-6">
          {PAGES[page]}
        </div>
      </main>
    </div>
  )
}
