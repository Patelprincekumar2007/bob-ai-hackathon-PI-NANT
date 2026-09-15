import { useEffect, useState } from 'react'
import { apiFetch } from '../api'
import { KpiCard, Badge, Card, Section, PageHeader, Spinner, Empty, riskColor, DataTable } from './ui'

export default function Disruptions() {
  const [data, setData]       = useState([])
  const [loading, setLoading] = useState(true)
  const [selected, setSel]    = useState(null)

  useEffect(() => {
    apiFetch('/api/disruptions').then(d => { setData(d); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  const active = data.filter(d => ['active','monitoring'].includes(d.status))
  const total  = active.length || 1
  const critical = active.filter(d => d.severity?.toLowerCase() === 'critical').length
  const high     = active.filter(d => d.severity?.toLowerCase() === 'high').length
  const affected = [...new Set(active.flatMap(d => d.affected_routes || []))].length

  const sel = active.find(d => d.id === selected)
  const c   = sel ? riskColor(sel.severity) : {}

  const columns = [
    { key: 'id',    label: 'ID',       render: v => <span className="font-mono text-xs" style={{ color: '#38BDF8' }}>{v}</span> },
    { key: 'type',  label: 'Type',     render: v => <span style={{ color: '#64748B' }}>{v}</span> },
    { key: 'title', label: 'Title',    render: v => <span style={{ color: '#F1F5F9' }}>{v}</span> },
    { key: 'severity', label: 'Severity', render: v => <Badge level={v} label={v} /> },
    { key: 'status',   label: 'Status',  render: v => <span style={{ color: '#64748B' }}>{v}</span> },
    { key: 'estimated_delay_days', label: 'Delay (d)', render: v => <span style={{ color: '#FB923C' }}>+{v}d</span> },
    { key: 'additional_cost_usd',  label: 'Add. Cost', render: v => <span style={{ color: '#94A3B8' }}>${v?.toLocaleString()}</span> },
  ]

  return (
    <div className="fade-in">
      <PageHeader title="🌩️ Active Disruptions" subtitle="Real-time port, weather, strike and vessel disruption tracking" />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
        <KpiCard icon="🌩️" value={active.length} label="Active Disruptions" />
        <KpiCard icon="📦" value={affected}        label="Affected Routes" />
        <KpiCard icon="🔴" value={critical}        label="Critical" accent="#F87171" />
        <KpiCard icon="🟠" value={high}            label="High" accent="#FB923C" />
      </div>

      {loading ? <Spinner /> : active.length === 0 ? <Empty icon="✅" message="No active disruptions at this time." /> : (
        <>
          <Section title="Disruption Register" />
          <div className="cursor-pointer" onClick={e => {
            const row = e.target.closest('tr')
            if (row) {
              const id = row.querySelector('span.font-mono')?.textContent
              if (id) setSel(id)
            }
          }}>
            <DataTable columns={columns} rows={active} />
          </div>

          {sel && (
            <div className="mt-6 fade-in">
              <Section title={`Detail — ${sel.id}`} />
              <Card className="p-5 mb-3" accent={c.text}>
                <div className="flex items-center gap-3 mb-3">
                  <Badge level={sel.severity} label={sel.severity} />
                  <span className="font-semibold" style={{ color: '#F1F5F9' }}>{sel.title}</span>
                  <span className="font-mono text-xs ml-auto" style={{ color: '#475569' }}>{sel.id}</span>
                </div>
                <p className="text-sm leading-relaxed" style={{ color: '#64748B' }}>{sel.description}</p>
              </Card>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <Card className="p-4">
                  {[['Type', sel.type], ['Status', sel.status], ['Est. Delay', `${sel.estimated_delay_days} days`], ['Add. Cost', `$${sel.additional_cost_usd?.toLocaleString()}`]].map(([k,v]) => (
                    <div key={k} className="flex gap-2 mb-2">
                      <span className="text-xs w-28 flex-shrink-0" style={{ color: '#475569' }}>{k}</span>
                      <span className="text-sm font-medium" style={{ color: '#F1F5F9' }}>{v}</span>
                    </div>
                  ))}
                </Card>
                <Card className="p-4">
                  {[
                    ['Affected Ports',    sel.affected_ports],
                    ['Affected Routes',   sel.affected_routes],
                    ['Affected Carriers', sel.affected_carriers],
                    ['Affected Vessels',  sel.affected_vessel_ids],
                  ].map(([k, arr]) => (
                    <div key={k} className="flex flex-wrap gap-1 mb-2 items-start">
                      <span className="text-xs w-28 flex-shrink-0 mt-0.5" style={{ color: '#475569' }}>{k}</span>
                      <div className="flex flex-wrap gap-1">
                        {arr?.length ? arr.map(a => (
                          <span key={a} className="text-xs px-2 py-0.5 rounded-full" style={{ background: 'rgba(255,255,255,0.05)', color: '#94A3B8', border: '1px solid rgba(255,255,255,0.08)' }}>{a}</span>
                        )) : <span className="text-xs" style={{ color: '#334155' }}>—</span>}
                      </div>
                    </div>
                  ))}
                </Card>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
