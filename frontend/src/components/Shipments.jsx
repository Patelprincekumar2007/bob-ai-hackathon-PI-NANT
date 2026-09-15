import { useEffect, useState } from 'react'
import { apiFetch, apiPost } from '../api'
import { Badge, Card, Section, PageHeader, Spinner, Empty, FactorBar, riskColor, DataTable } from './ui'

const RISK_LEVELS = ['All','CRITICAL','HIGH','MEDIUM','LOW']

export default function Shipments({ filters }) {
  const [scored, setScored]       = useState([])
  const [loading, setLoading]     = useState(true)
  const [riskFilter, setRisk]     = useState('All')
  const [search, setSearch]       = useState('')
  const [selected, setSelected]   = useState(null)
  const [detail, setDetail]       = useState(null)
  const [detailLoading, setDL]    = useState(false)
  const [aiResult, setAiResult]   = useState(null)
  const [aiLoading, setAiLoading] = useState(false)

  useEffect(() => {
    apiFetch('/api/shipments').then(d => { setScored(d); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!selected) return
    setDetail(null); setAiResult(null); setDL(true)
    apiFetch(`/api/shipments/${selected}`).then(d => { setDetail(d); setDL(false) }).catch(() => setDL(false))
  }, [selected])

  const filtered = scored.filter(s => {
    if (riskFilter !== 'All' && s.classification !== riskFilter) return false
    if (search) {
      const q = search.toLowerCase()
      if (!s.shipment_id.toLowerCase().includes(q) && !s.description?.toLowerCase().includes(q)) return false
    }
    return true
  })

  const handleAI = async () => {
    if (!detail) return
    const { risk, disruptions } = detail
    const rc = risk?.classification || 'UNKNOWN'
    const rs = risk?.score || 0
    const dt = disruptions?.map(d => d.title).join('; ') || 'None'
    const prompt = `You are a supply chain risk analyst. Shipment ${selected} has a risk score of ${rs}/100 (${rc}). Active disruptions: ${dt}. Provide a brief, actionable explanation for a logistics coordinator.`
    setAiLoading(true)
    const r = await apiPost('/api/ai/explain', { prompt }).catch(() => null)
    setAiResult(r); setAiLoading(false)
  }

  const columns = [
    { key: 'shipment_id', label: 'ID', render: v => <span className="font-mono text-xs" style={{ color: '#38BDF8' }}>{v}</span> },
    { key: 'description', label: 'Description', render: v => <span style={{ color: '#94A3B8' }}>{v}</span> },
    { key: 'score', label: 'Score', render: (v) => (
      <div className="flex items-center gap-2">
        <span className="font-bold text-sm" style={{ color: riskColor(v >= 75 ? 'CRITICAL' : v >= 50 ? 'HIGH' : v >= 25 ? 'MEDIUM' : 'LOW').text }}>{v}</span>
        <div className="rounded-full overflow-hidden h-1 w-16" style={{ background: 'rgba(255,255,255,0.06)' }}>
          <div className="h-1 rounded-full" style={{ width: `${v}%`, background: riskColor(v >= 75 ? 'CRITICAL' : v >= 50 ? 'HIGH' : v >= 25 ? 'MEDIUM' : 'LOW').text }} />
        </div>
      </div>
    )},
    { key: 'classification', label: 'Risk', render: v => <Badge level={v} label={v} /> },
    { key: 'status', label: 'Status', render: v => <span style={{ color: '#64748B' }}>{v}</span> },
    { key: 'delay_days', label: 'Delay (d)', render: v => v > 0 ? <span style={{ color: '#FB923C' }}>+{v}d</span> : <span style={{ color: '#34D399' }}>—</span> },
    { key: 'requires_cold_chain', label: 'Cold Chain', render: v => v ? <span>❄️</span> : <span style={{ color: '#334155' }}>—</span> },
  ]

  return (
    <div className="fade-in">
      <PageHeader title="📋 Shipments" subtitle="Risk-scored shipment register with disruption, route and AI analysis" />

      {/* Filters row */}
      <div className="flex flex-wrap gap-3 mb-4">
        <input
          className="flex-1 min-w-48 rounded-lg px-3 py-2 text-sm outline-none transition-all"
          style={{ background: '#111827', border: '1px solid rgba(255,255,255,0.09)', color: '#F1F5F9' }}
          placeholder="🔍  Search by ID or description…"
          value={search} onChange={e => setSearch(e.target.value)}
          onFocus={e => e.target.style.borderColor='#38BDF8'}
          onBlur={e => e.target.style.borderColor='rgba(255,255,255,0.09)'}
        />
        <div className="flex gap-1 rounded-lg p-1" style={{ background: '#111827', border: '1px solid rgba(255,255,255,0.07)' }}>
          {RISK_LEVELS.map(l => (
            <button key={l} onClick={() => setRisk(l)}
              className="px-3 py-1.5 rounded-md text-xs font-semibold transition-all"
              style={{
                background: riskFilter === l ? (l === 'All' ? '#1E3A5F' : riskColor(l).bg) : 'transparent',
                color: riskFilter === l ? (l === 'All' ? '#38BDF8' : riskColor(l).text) : '#475569',
              }}
            >{l}</button>
          ))}
        </div>
      </div>

      {loading ? <Spinner /> : (
        <>
          <Section title={`${filtered.length} Shipments`} />
          {filtered.length === 0 ? <Empty icon="🔍" message="No shipments match the filters." /> : (
            <div onClick={e => {
              const row = e.target.closest('tr')
              if (row) {
                const id = row.querySelector('span.font-mono')?.textContent
                if (id) setSelected(id)
              }
            }} className="cursor-pointer">
              <DataTable columns={columns} rows={filtered} />
            </div>
          )}
        </>
      )}

      {/* Detail panel */}
      {selected && (
        <div className="mt-6 fade-in">
          <Section title={`Detail — ${selected}`} />
          {detailLoading ? <Spinner /> : detail ? (
            <>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {/* Shipment info */}
                <Card className="p-5">
                  <div className="text-xs font-bold uppercase tracking-widest mb-3" style={{ color: '#334155' }}>Shipment Info</div>
                  {[
                    ['ID', <span className="font-mono text-xs" style={{ color: '#38BDF8' }}>{selected}</span>],
                    ['Description', detail.raw?.description],
                    ['Carrier', detail.raw?.carrier],
                    ['Origin', `${detail.raw?.origin?.city} · ${detail.raw?.origin?.country}`],
                    ['Destination', `${detail.raw?.destination?.city} · ${detail.raw?.destination?.country}`],
                    ['Status', detail.raw?.status],
                    ['Priority', detail.raw?.priority],
                    ['Cargo', detail.raw?.cargo_type],
                  ].map(([k, v]) => (
                    <div key={k} className="flex items-start gap-2 mb-2">
                      <span className="text-xs w-24 flex-shrink-0 pt-0.5" style={{ color: '#475569' }}>{k}</span>
                      <span className="text-sm font-medium" style={{ color: '#F1F5F9' }}>{v}</span>
                    </div>
                  ))}
                </Card>

                {/* Risk assessment */}
                <Card className="p-5">
                  <div className="text-xs font-bold uppercase tracking-widest mb-3" style={{ color: '#334155' }}>Risk Assessment</div>
                  {detail.risk && (
                    <>
                      <div className="flex items-end gap-3 mb-4">
                        <span className="font-head text-5xl font-extrabold" style={{ color: riskColor(detail.risk.classification).text, letterSpacing: '-0.04em' }}>
                          {detail.risk.score}
                        </span>
                        <div>
                          <div className="text-xs" style={{ color: '#475569' }}>/ 100</div>
                          <Badge level={detail.risk.classification} label={detail.risk.classification} />
                        </div>
                      </div>
                      {Object.entries({
                        'Disruption Severity': [detail.risk.factor_breakdown?.disruption_severity, 35],
                        'Delay Factor':        [detail.risk.factor_breakdown?.delay, 25],
                        'Deadline Pressure':   [detail.risk.factor_breakdown?.deadline_pressure, 20],
                        'Priority Factor':     [detail.risk.factor_breakdown?.priority, 15],
                        'Cold-Chain Factor':   [detail.risk.factor_breakdown?.cold_chain, 5],
                      }).map(([k,[v,m]]) => <FactorBar key={k} label={k} val={v||0} max={m} />)}
                    </>
                  )}
                </Card>
              </div>

              {/* Disruptions */}
              {detail.disruptions?.length > 0 && (
                <>
                  <Section title="Active Disruptions" />
                  {detail.disruptions.map(d => {
                    const c = riskColor(d.severity)
                    return (
                      <Card key={d.id} className="p-4 mb-2" accent={c.text}>
                        <div className="flex items-center gap-2 mb-1">
                          <Badge level={d.severity} label={d.severity} />
                          <span className="font-semibold text-sm" style={{ color: '#F1F5F9' }}>{d.title}</span>
                          <span className="text-xs ml-auto" style={{ color: '#475569' }}>+{d.estimated_delay_days}d · +${d.additional_cost_usd?.toLocaleString()}</span>
                        </div>
                        <p className="text-xs" style={{ color: '#64748B' }}>{d.description}</p>
                      </Card>
                    )
                  })}
                </>
              )}

              {/* Route alternatives */}
              {detail.routes?.alternatives?.length > 0 && (
                <>
                  <Section title="Route Alternatives" />
                  {detail.routes.alternatives.map((alt, i) => (
                    <Card key={i} className="p-4 mb-2">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-semibold text-sm" style={{ color: '#F1F5F9' }}>Option {i+1}: {alt.description}</span>
                        <div className="flex gap-2">
                          <span className="text-xs px-2 py-0.5 rounded" style={{ background: 'rgba(251,146,60,0.1)', color: '#FB923C' }}>
                            {alt.extra_delay_days >= 0 ? `+${alt.extra_delay_days}d` : `${Math.abs(alt.extra_delay_days)}d faster`}
                          </span>
                          <span className="text-xs px-2 py-0.5 rounded" style={{ background: 'rgba(56,189,248,0.1)', color: '#38BDF8' }}>
                            +${alt.extra_cost_usd?.toLocaleString()}
                          </span>
                        </div>
                      </div>
                      <p className="text-xs" style={{ color: '#64748B' }}>{alt.reason}</p>
                    </Card>
                  ))}
                </>
              )}

              {/* AI Explanation */}
              <Section title="AI Risk Explanation" />
              <Card className="p-5" style={{ background: 'linear-gradient(135deg, rgba(56,189,248,0.04), rgba(129,140,248,0.04))', borderColor: 'rgba(56,189,248,0.12)' }}>
                <div className="flex items-center justify-between mb-4">
                  <span className="font-head font-bold text-sm" style={{ color: '#F1F5F9' }}>Generate AI Analysis</span>
                  <span className="text-xs px-2 py-1 rounded-full" style={{ background: 'rgba(56,189,248,0.1)', color: '#38BDF8', border: '1px solid rgba(56,189,248,0.2)' }}>
                    <span className="pulse-dot inline-block w-1.5 h-1.5 rounded-full mr-1.5 align-middle" style={{ background: '#38BDF8' }}></span>
                    watsonx.ai
                  </span>
                </div>
                <button onClick={handleAI} disabled={aiLoading}
                  className="px-5 py-2.5 rounded-lg font-bold text-sm transition-all disabled:opacity-50"
                  style={{ background: 'linear-gradient(135deg,#38BDF8,#818CF8)', color: '#070B14', boxShadow: '0 4px 15px rgba(56,189,248,0.25)' }}
                >
                  {aiLoading ? 'Analysing…' : 'Generate Explanation'}
                </button>
                {aiResult && (
                  <div className="mt-4 p-4 rounded-xl" style={{ background: '#0D1424', border: '1px solid rgba(56,189,248,0.15)' }}>
                    <p className="text-sm leading-relaxed" style={{ color: '#94A3B8' }}>{aiResult.text}</p>
                  </div>
                )}
              </Card>
            </>
          ) : null}
        </div>
      )}
    </div>
  )
}
