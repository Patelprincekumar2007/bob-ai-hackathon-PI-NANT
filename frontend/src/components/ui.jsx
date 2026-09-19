import { clsx } from 'clsx'
import { AnimatedCounter } from './effects'

// ── Subtle, Soothing Risk & Severity Palettes ──────────────────────────────
export const RISK_COLOR = {
  CRITICAL: { text: '#E11D48', bg: '#FFF1F2', border: '#FECDD3', dot: '#F43F5E' },
  HIGH:     { text: '#D97706', bg: '#FFFBEB', border: '#FDE68A', dot: '#F59E0B' },
  MEDIUM:   { text: '#2563EB', bg: '#EFF6FF', border: '#BFDBFE', dot: '#3B82F6' },
  LOW:      { text: '#059669', bg: '#ECFDF5', border: '#A7F3D0', dot: '#10B981' },
  NORMAL:   { text: '#059669', bg: '#ECFDF5', border: '#A7F3D0', dot: '#10B981' },
  WARNING:  { text: '#D97706', bg: '#FFFBEB', border: '#FDE68A', dot: '#F59E0B' },
}
export const riskColor = (lvl) => 
  RISK_COLOR[(lvl || '').toUpperCase()] || { text: '#475569', bg: '#F1F5F9', border: '#E2E8F0', dot: '#64748B' }

// ── Executive White Card ──────────────────────────────────────────────────
export function Card({ children, className = '', accent, style, onClick }) {
  return (
    <div
      onClick={onClick}
      className={clsx('bg-white border border-slate-200/80 rounded-2xl p-5 shadow-xs transition-all duration-200', className)}
      style={{
        borderLeftColor: accent || undefined,
        borderLeftWidth: accent ? '3px' : undefined,
        ...style,
      }}
    >
      {children}
    </div>
  )
}

// ── Clean Pill Badge ──────────────────────────────────────────────────────
export function Badge({ label, level }) {
  const c = riskColor(level || label)
  return (
    <span
      className="inline-flex items-center gap-1.5 text-[11px] font-mono font-bold px-2.5 py-0.5 rounded-full tracking-wide"
      style={{ 
        color: c.text, 
        background: c.bg, 
        border: `1px solid ${c.border}`,
      }}
    >
      <span className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ background: c.dot }} />
      {(label || level || '').toUpperCase()}
    </span>
  )
}

// ── Executive KPI Card ────────────────────────────────────────────────────
export function KpiCard({ icon, value, label, sub, accent }) {
  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs flex flex-col justify-between hover:shadow-sm transition-all">
      <div className="flex items-center justify-between mb-3">
        <span className="p-2.5 rounded-xl bg-slate-50 border border-slate-100 text-slate-600">
          {icon}
        </span>
        {accent && (
          <span className="w-2 h-2 rounded-full" style={{ background: accent }} />
        )}
      </div>
      <div>
        <div className="text-2xl sm:text-3xl font-extrabold font-head tracking-tight text-slate-900">
          {typeof value === 'number' ? <AnimatedCounter value={value} /> : value}
        </div>
        <div className="text-xs font-semibold text-slate-700 mt-1">
          {label}
        </div>
        {sub && (
          <div className="text-[11px] font-medium text-slate-400 mt-0.5">
            {sub}
          </div>
        )}
      </div>
    </div>
  )
}

// ── Section Divider ───────────────────────────────────────────────────────
export function Section({ title, action }) {
  return (
    <div className="flex items-center justify-between gap-4 my-5 mt-6">
      <div className="flex items-center gap-2">
        <span className="w-1.5 h-3.5 rounded-full bg-blue-600" />
        <span className="text-xs font-bold uppercase tracking-wider text-slate-800 font-head">{title}</span>
      </div>
      <div className="flex-1 h-px bg-slate-200/80" />
      {action && <div>{action}</div>}
    </div>
  )
}

// ── Page Header ───────────────────────────────────────────────────────────
export function PageHeader({ title, subtitle, badge = 'CONTROL TOWER' }) {
  return (
    <div className="mb-5 pb-4 border-b border-slate-200/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div>
        <div className="flex items-center gap-3">
          <h1 className="font-head text-2xl font-extrabold tracking-tight text-slate-900">
            {title}
          </h1>
          {badge && (
            <span className="text-[10px] font-mono px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 font-bold">
              {badge}
            </span>
          )}
        </div>
        {subtitle && <p className="text-xs sm:text-sm mt-1 text-slate-500 font-medium">{subtitle}</p>}
      </div>
    </div>
  )
}

// ── Interactive Global Route Map (Executive Marine Radar) ─────────────────
export function InteractiveGlobalMap() {
  const routes = [
    // Shanghai -> Rotterdam
    { from: [121.5, 31.2], to: [4.4, 51.9], color: '#F43F5E', name: 'Asia-Europe Mainline', delay: '+36h' },
    // Singapore -> New York
    { from: [103.8, 1.3], to: [-74.0, 40.7], color: '#F59E0B', name: 'Transpacific Feeder', delay: '+18h' },
    // Antwerp -> Santos
    { from: [4.4, 51.2], to: [-46.3, -23.9], color: '#10B981', name: 'South America Corridor', delay: 'Nominal' },
    // Hamburg -> Mumbai
    { from: [9.9, 53.5], to: [72.8, 19.0], color: '#F43F5E', name: 'Indian Ocean Express', delay: '+28h' }
  ]

  const project = ([lon, lat]) => {
    const x = ((lon + 180) / 360) * 800
    const y = ((90 - lat) / 180) * 400
    return [x, y]
  }

  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs relative overflow-hidden">
      <div className="flex items-center justify-between mb-3.5">
        <div>
          <h3 className="font-head font-bold text-sm text-slate-900 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-blue-600 animate-pulse" />
            Global Maritime Transit Vectors & Active Risk Corridors
          </h3>
          <p className="text-xs text-slate-400 font-mono">Live automated transit vector projections</p>
        </div>
        <span className="text-[10px] font-mono text-blue-700 px-2.5 py-0.5 rounded-full bg-blue-50 border border-blue-200 font-semibold">
          Natural Earth Projection
        </span>
      </div>

      <div className="relative w-full aspect-[2/1] rounded-xl bg-[#091122] border border-slate-800 overflow-hidden shadow-inner">
        <svg viewBox="0 0 800 400" className="w-full h-full">
          {/* Latitude & Longitude graticules */}
          {[100, 200, 300].map(y => (
            <line key={`lat-${y}`} x1="0" y1={y} x2="800" y2={y} stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
          ))}
          {[160, 320, 480, 640].map(x => (
            <line key={`lon-${x}`} x1={x} y1="0" x2={x} y2="400" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
          ))}

          {/* Continents */}
          <path d="M 120 70 Q 200 60 220 120 T 170 200 T 130 150 Z" fill="rgba(30, 41, 59, 0.7)" stroke="rgba(56, 189, 248, 0.2)" strokeWidth="0.8" />
          <path d="M 210 200 Q 260 240 240 330 T 200 280 T 190 220 Z" fill="rgba(30, 41, 59, 0.7)" stroke="rgba(56, 189, 248, 0.2)" strokeWidth="0.8" />
          <path d="M 380 60 Q 430 50 450 110 T 400 140 T 360 100 Z" fill="rgba(30, 41, 59, 0.7)" stroke="rgba(56, 189, 248, 0.2)" strokeWidth="0.8" />
          <path d="M 390 140 Q 460 170 440 280 T 370 240 T 380 150 Z" fill="rgba(30, 41, 59, 0.7)" stroke="rgba(56, 189, 248, 0.2)" strokeWidth="0.8" />
          <path d="M 460 50 Q 620 40 680 130 T 570 220 T 470 140 Z" fill="rgba(30, 41, 59, 0.7)" stroke="rgba(56, 189, 248, 0.2)" strokeWidth="0.8" />
          <path d="M 640 250 Q 720 260 700 320 T 630 300 Z" fill="rgba(30, 41, 59, 0.7)" stroke="rgba(56, 189, 248, 0.2)" strokeWidth="0.8" />

          {/* Route Arcs */}
          {routes.map((r, i) => {
            const [x1, y1] = project(r.from)
            const [x2, y2] = project(r.to)
            const cx = (x1 + x2) / 2
            const cy = Math.min(y1, y2) - 45
            const d = `M ${x1} ${y1} Q ${cx} ${cy} ${x2} ${y2}`
            return (
              <g key={`route-${i}`}>
                <path d={d} fill="none" stroke={r.color} strokeWidth="2.5" opacity="0.25" />
                <path d={d} fill="none" stroke={r.color} strokeWidth="1.4" strokeDasharray="4 3" opacity="0.9" />
                <circle cx={x1} cy={y1} r="4" fill={r.color} />
                <circle cx={x1} cy={y1} r="7" fill="none" stroke={r.color} strokeWidth="1" opacity="0.6">
                  <animate attributeName="r" values="4;9;4" dur="2.5s" repeatCount="indefinite" />
                  <animate attributeName="opacity" values="0.8;0;0.8" dur="2.5s" repeatCount="indefinite" />
                </circle>
                <circle cx={x2} cy={y2} r="4" fill={r.color} />
              </g>
            )
          })}
        </svg>

        {/* Radar Legend */}
        <div className="absolute bottom-2.5 left-2.5 right-2.5 flex items-center justify-between text-[11px] font-mono text-slate-300 bg-slate-950/80 backdrop-blur-md px-3.5 py-2 rounded-lg border border-white/10">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-rose-500" /> Critical Hotspot</span>
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-amber-400" /> Delay Advisory</span>
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-emerald-400" /> Nominal Route</span>
          </div>
          <span className="text-cyan-400 font-bold">4 Active Corridors Monitored</span>
        </div>
      </div>
    </div>
  )
}

// ── Factor Progress Bar ───────────────────────────────────────────────────
export function FactorBar({ label, val, max }) {
  const pct = max ? Math.min(100, Math.round(val / max * 100)) : 0
  return (
    <div className="mb-3">
      <div className="flex justify-between items-center mb-1 text-xs">
        <span className="font-semibold text-slate-700">{label}</span>
        <span className="font-mono font-bold text-blue-600">{val} / {max}</span>
      </div>
      <div className="rounded-full overflow-hidden h-1.5 bg-slate-100 border border-slate-200">
        <div 
          className="h-full rounded-full transition-all duration-500" 
          style={{ 
            width: `${pct}%`, 
            background: 'linear-gradient(90deg, #2563EB, #6366F1)',
          }} 
        />
      </div>
    </div>
  )
}

// ── Custom Tooltip for Charts ─────────────────────────────────────────────
export function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-xl border border-slate-200 p-3 text-xs bg-white shadow-xl">
      <div className="font-bold mb-1 font-head text-slate-900">Sample #{label}</div>
      {payload.map((p, i) => (
        <div key={i} className="flex items-center gap-2 font-mono text-slate-700">
          <span style={{ color: p.color }}>{p.name}:</span>
          <span className="font-bold">{p.value}</span>
        </div>
      ))}
    </div>
  )
}

// ── Executive Data Table ──────────────────────────────────────────────────
export function DataTable({ columns = [], rows = [], onRowClick }) {
  return (
    <div className="overflow-x-auto rounded-2xl border border-slate-200/80 bg-white shadow-xs">
      <table className="w-full text-left text-xs border-collapse">
        <thead>
          <tr className="border-b border-slate-200/80 bg-slate-50/70">
            {columns.map(c => (
              <th key={c.key} className="px-4 py-3 text-[11px] font-bold uppercase tracking-wider text-slate-500 font-head">
                {c.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {rows.map((row, ri) => (
            <tr
              key={ri}
              onClick={() => onRowClick && onRowClick(row)}
              className="transition-colors duration-150 hover:bg-slate-50/80 cursor-pointer group"
            >
              {columns.map(c => (
                <td key={c.key} className="px-4 py-3.5 text-slate-700 font-medium">
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

// ── Empty State ───────────────────────────────────────────────────────────
export function Empty({ icon = '📭', message }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 rounded-2xl border border-dashed border-slate-200 bg-white">
      <span className="text-2xl mb-2.5 opacity-60">{icon}</span>
      <p className="text-xs font-semibold text-slate-500">{message}</p>
    </div>
  )
}

// ── Loading Spinner ───────────────────────────────────────────────────────
export function Spinner() {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-3">
      <div className="w-8 h-8 rounded-full border-2 border-slate-200 animate-spin border-t-blue-600" />
      <span className="text-xs font-mono text-slate-500 uppercase tracking-wider">Streaming Control Tower Feeds...</span>
    </div>
  )
}
