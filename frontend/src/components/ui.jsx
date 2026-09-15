import { clsx } from 'clsx'

// ── Risk / severity palettes ──────────────────────────────────────────────
export const RISK_COLOR = {
  CRITICAL: { text: '#F87171', bg: 'rgba(248,113,113,0.12)', border: 'rgba(248,113,113,0.3)' },
  HIGH:     { text: '#FB923C', bg: 'rgba(251,146,60,0.12)',  border: 'rgba(251,146,60,0.3)'  },
  MEDIUM:   { text: '#FBBF24', bg: 'rgba(251,191,36,0.12)',  border: 'rgba(251,191,36,0.3)'  },
  LOW:      { text: '#34D399', bg: 'rgba(52,211,153,0.12)',  border: 'rgba(52,211,153,0.3)'  },
  NORMAL:   { text: '#34D399', bg: 'rgba(52,211,153,0.12)',  border: 'rgba(52,211,153,0.3)'  },
  WARNING:  { text: '#FB923C', bg: 'rgba(251,146,60,0.12)',  border: 'rgba(251,146,60,0.3)'  },
}
export const riskColor = (lvl) => RISK_COLOR[(lvl||'').toUpperCase()] || { text: '#64748B', bg: 'rgba(100,116,139,0.1)', border: 'rgba(100,116,139,0.2)' }

// ── Card ──────────────────────────────────────────────────────────────────
export function Card({ children, className = '', accent, style }) {
  return (
    <div
      className={clsx('rounded-xl border transition-all duration-200', className)}
      style={{
        background: '#0D1424',
        borderColor: accent ? accent : 'rgba(255,255,255,0.07)',
        borderLeftColor: accent || undefined,
        borderLeftWidth: accent ? 3 : undefined,
        ...style,
      }}
    >
      {children}
    </div>
  )
}

// ── Badge ─────────────────────────────────────────────────────────────────
export function Badge({ label, level }) {
  const c = riskColor(level || label)
  return (
    <span
      className="inline-block text-xs font-bold px-2 py-0.5 rounded-md tracking-wide"
      style={{ color: c.text, background: c.bg, border: `1px solid ${c.border}` }}
    >
      {(label || level || '').toUpperCase()}
    </span>
  )
}

// ── KPI card ──────────────────────────────────────────────────────────────
export function KpiCard({ icon, value, label, sub, accent }) {
  return (
    <Card
      className="p-5 hover:-translate-y-1 hover:shadow-lg cursor-default relative overflow-hidden"
      style={{ background: '#0D1424' }}
    >
      <div className="absolute top-0 left-0 right-0 h-px" style={{ background: 'linear-gradient(90deg, transparent, rgba(56,189,248,0.2), transparent)' }} />
      <div className="text-xl mb-2">{icon}</div>
      <div className="text-3xl font-extrabold font-head tracking-tight" style={{ color: accent || '#F1F5F9' }}>
        {value}
      </div>
      <div className="text-xs uppercase tracking-widest mt-1.5 font-semibold" style={{ color: '#475569' }}>
        {label}
      </div>
      {sub && <div className="text-xs mt-1 font-medium" style={{ color: '#38BDF8' }}>{sub}</div>}
    </Card>
  )
}

// ── Section header ────────────────────────────────────────────────────────
export function Section({ title }) {
  return (
    <div className="flex items-center gap-3 my-5">
      <span className="text-xs uppercase tracking-widest font-bold" style={{ color: '#334155' }}>{title}</span>
      <div className="flex-1 h-px" style={{ background: 'rgba(255,255,255,0.05)' }} />
    </div>
  )
}

// ── Page header ───────────────────────────────────────────────────────────
export function PageHeader({ title, subtitle }) {
  return (
    <div className="mb-6 pb-5" style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
      <h1 className="font-head text-2xl font-extrabold tracking-tight" style={{ color: '#F1F5F9', letterSpacing: '-0.03em' }}>{title}</h1>
      <p className="text-sm mt-1" style={{ color: '#475569' }}>{subtitle}</p>
    </div>
  )
}

// ── Empty state ───────────────────────────────────────────────────────────
export function Empty({ icon = '📭', message }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 rounded-xl" style={{ border: '1px dashed rgba(255,255,255,0.07)', background: 'rgba(255,255,255,0.01)' }}>
      <span className="text-3xl mb-3 opacity-40">{icon}</span>
      <p className="text-sm" style={{ color: '#475569' }}>{message}</p>
    </div>
  )
}

// ── Loading spinner ───────────────────────────────────────────────────────
export function Spinner() {
  return (
    <div className="flex items-center justify-center py-16">
      <div className="w-8 h-8 rounded-full border-2 border-transparent animate-spin" style={{ borderTopColor: '#38BDF8', borderRightColor: '#818CF8' }} />
    </div>
  )
}

// ── Factor progress bar ───────────────────────────────────────────────────
export function FactorBar({ label, val, max }) {
  const pct = max ? Math.min(100, Math.round(val / max * 100)) : 0
  return (
    <div className="mb-3">
      <div className="flex justify-between items-center mb-1">
        <span className="text-xs font-medium" style={{ color: '#94A3B8' }}>{label}</span>
        <span className="text-xs font-bold font-mono" style={{ color: '#38BDF8' }}>{val}/{max}</span>
      </div>
      <div className="rounded-full overflow-hidden h-1" style={{ background: 'rgba(255,255,255,0.06)' }}>
        <div className="h-1 rounded-full" style={{ width: `${pct}%`, background: 'linear-gradient(90deg,#38BDF8,#818CF8)' }} />
      </div>
    </div>
  )
}

// ── Custom tooltip for Recharts ───────────────────────────────────────────
export function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-xl border p-3 text-xs" style={{ background: '#0D1424', borderColor: 'rgba(255,255,255,0.1)' }}>
      <div className="font-bold mb-1" style={{ color: '#F1F5F9' }}>Reading #{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ color: p.color }}>{p.name}: <b>{p.value}</b></div>
      ))}
    </div>
  )
}

// ── Data table ────────────────────────────────────────────────────────────
export function DataTable({ columns, rows }) {
  return (
    <div className="rounded-xl overflow-hidden" style={{ border: '1px solid rgba(255,255,255,0.07)' }}>
      <table className="w-full text-sm">
        <thead>
          <tr style={{ background: 'rgba(255,255,255,0.03)', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
            {columns.map(c => (
              <th key={c.key} className="text-left px-4 py-3 text-xs font-bold uppercase tracking-widest" style={{ color: '#475569' }}>
                {c.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, ri) => (
            <tr key={ri} className="transition-colors" style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}
              onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.02)'}
              onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
            >
              {columns.map(c => (
                <td key={c.key} className="px-4 py-3" style={{ color: c.color?.(row[c.key]) || '#94A3B8' }}>
                  {c.render ? c.render(row[c.key], row) : row[c.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
