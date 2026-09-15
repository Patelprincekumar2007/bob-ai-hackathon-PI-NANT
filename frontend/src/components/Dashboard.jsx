import { useEffect, useState } from 'react'
import { apiFetch } from '../api'
import { KpiCard, Section, Badge, Card, Spinner, Empty, riskColor, DataTable } from './ui'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    apiFetch('/api/dashboard').then(d => { setData(d); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  if (loading) return <Spinner />
  if (!data) return <Empty icon="⚠️" message="Failed to load dashboard data." />

  const { risk, disruptions, fleet, cold_chain } = data
  const riskBreakdown = [
    { label: 'Critical', count: risk.critical_count, key: 'CRITICAL' },
    { label: 'High',     count: risk.high_count,     key: 'HIGH' },
    { label: 'Medium',   count: risk.medium_count,   key: 'MEDIUM' },
    { label: 'Low',      count: risk.low_count,      key: 'LOW' },
  ]
  const total = risk.total_shipments || 1

  return (
    <div className="fade-in">
      <div className="mb-6 pb-5" style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
        <h1 className="font-head text-2xl font-extrabold tracking-tight flex items-center gap-3" style={{ color: '#F1F5F9', letterSpacing: '-0.03em' }}>
          <span className="shimmer-text">⚓ SmartRoute AI</span>
        </h1>
        <p className="text-sm mt-1" style={{ color: '#475569' }}>Supply Chain Control Tower — real-time risk, disruption & fleet intelligence</p>
      </div>

      {/* KPI row */}
      <Section title="Overview" />
      <div className="grid grid-cols-4 xl:grid-cols-7 gap-3 mb-6">
        <KpiCard icon="📦" value={risk.total_shipments}                  label="Total Shipments" />
        <KpiCard icon="⚠️"  value={disruptions.total_affected_shipments} label="At-Risk" />
        <KpiCard icon="🔴" value={risk.critical_count}                   label="Critical" accent="#F87171" />
        <KpiCard icon="🌩️" value={disruptions.total_active_disruptions} label="Disruptions" />
        <KpiCard icon="🚢" value={fleet.available}                       label="Available Vessels" />
        <KpiCard icon="📊" value={`${fleet.utilisation_pct}%`}          label="Fleet Utilisation" />
        <KpiCard icon="🌡️" value={cold_chain.shipments_with_excursions}  label="Cold-Chain Alerts" accent="#F87171" />
      </div>

      {/* Risk breakdown */}
      <Section title="Risk Breakdown" />
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
        {riskBreakdown.map(rb => {
          const c = riskColor(rb.key)
          const pct = Math.round(rb.count / total * 100)
          return (
            <Card key={rb.key} className="p-4 hover:-translate-y-1 hover:shadow-lg overflow-hidden relative">
              <div className="absolute top-0 left-0 right-0 h-0.5" style={{ background: c.text }} />
              <div className="flex justify-between items-start mb-2">
                <div>
                  <div className="text-3xl font-extrabold font-head" style={{ color: c.text }}>{rb.count}</div>
                  <div className="text-xs uppercase tracking-widest font-bold mt-0.5" style={{ color: '#475569' }}>{rb.label}</div>
                </div>
                <span className="text-xs font-bold px-2 py-1 rounded-lg" style={{ background: c.bg, color: c.text }}>{pct}%</span>
              </div>
              <div className="rounded-full overflow-hidden h-1.5 mt-3" style={{ background: 'rgba(255,255,255,0.06)' }}>
                <div className="h-1.5 rounded-full transition-all duration-700" style={{ width: `${pct}%`, background: c.text }} />
              </div>
            </Card>
          )
        })}
      </div>

      {/* Risk chart */}
      <Section title="Risk Distribution" />
      <Card className="p-4 mb-6">
        <ResponsiveContainer width="100%" height={160}>
          <BarChart data={riskBreakdown} barSize={40}>
            <XAxis dataKey="label" tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={{ background: '#0D1424', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10, fontSize: 12 }} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
            <Bar dataKey="count" radius={[6,6,0,0]}>
              {riskBreakdown.map(rb => <Cell key={rb.key} fill={riskColor(rb.key).text} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Card>
    </div>
  )
}
