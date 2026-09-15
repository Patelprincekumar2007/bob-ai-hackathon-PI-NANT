import { useEffect, useState } from 'react'
import { apiFetch } from '../api'
import { KpiCard, Badge, Card, Section, PageHeader, Spinner, Empty, riskColor, ChartTooltip, DataTable } from './ui'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, ReferenceArea } from 'recharts'

export default function ColdChain() {
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(true)
  const [selected, setSel]    = useState(null)
  const [detail, setDetail]   = useState(null)
  const [detailLoading, setDL] = useState(false)
  const [shipmentIds, setIds]  = useState([])

  useEffect(() => {
    Promise.all([apiFetch('/api/cold-chain'), apiFetch('/api/shipments')])
      .then(([cc, shp]) => {
        setData(cc)
        setIds(shp.filter(s => s.requires_cold_chain).map(s => s.shipment_id))
        setLoading(false)
      }).catch(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!selected) return
    setDetail(null); setDL(true)
    apiFetch(`/api/cold-chain/${selected}`).then(d => { setDetail(d); setDL(false) }).catch(() => setDL(false))
  }, [selected])

  if (loading) return <Spinner />
  if (!data) return <Empty icon="⚠️" message="Failed to load cold-chain data." />

  const { summary: s, alerts } = data

  const alertColumns = [
    { key: 'shipment_id',          label: 'Shipment',    render: v => <span className="font-mono text-xs" style={{ color: '#38BDF8' }}>{v}</span> },
    { key: 'cargo_type',           label: 'Cargo',       render: v => <span style={{ color: '#94A3B8' }}>{v}</span> },
    { key: 'excursion_severity',   label: 'Severity',    render: v => <Badge level={v} label={v} /> },
    { key: 'excursion_count',      label: 'Excursions',  render: v => <span style={{ color: '#FB923C' }}>{v}</span> },
    { key: 'cold_chain_risk_score',label: 'Risk Score',  render: v => <span className="font-bold" style={{ color: riskColor(v>=75?'CRITICAL':v>=50?'HIGH':v>=25?'MEDIUM':'LOW').text }}>{v}</span> },
    { key: 'latest_temp_c',        label: 'Latest (°C)', render: v => <span style={{ color: '#F1F5F9' }}>{v ?? '—'}</span> },
  ]

  // Build chart data
  const chartData = detail?.readings?.map((r, i) => ({
    idx: i + 1,
    temp: r.temperature_c,
    status: r.status,
    label: r.location || '',
  })) || []

  const tMin = detail?.required_temp_min_c
  const tMax = detail?.required_temp_max_c
  const sevClr = detail ? riskColor(detail.excursion_severity).text : '#38BDF8'

  return (
    <div className="fade-in">
      <PageHeader title="🌡️ Cold-Chain Monitor" subtitle="Temperature excursion alerts and shipment cold-chain history" />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
        <KpiCard icon="📦" value={s.total_tracked}   label="Tracked Shipments" />
        <KpiCard icon="🟢" value={s.normal_count}    label="Normal" accent="#34D399" />
        <KpiCard icon="🟡" value={s.warning_count}   label="Warning" accent="#FBBF24" />
        <KpiCard icon="🔴" value={s.critical_count}  label="Critical Excursions" accent="#F87171" />
      </div>

      {alerts?.length > 0 && (
        <>
          <Section title="Temperature Alerts" />
          <DataTable columns={alertColumns} rows={alerts} />
        </>
      )}

      {/* Shipment selector */}
      <Section title="Temperature History" />
      <div className="flex flex-wrap gap-2 mb-4">
        {shipmentIds.map(id => (
          <button key={id} onClick={() => setSel(id)}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold transition-all font-mono"
            style={{
              background: selected === id ? 'rgba(56,189,248,0.15)' : 'rgba(255,255,255,0.04)',
              color: selected === id ? '#38BDF8' : '#64748B',
              border: `1px solid ${selected === id ? 'rgba(56,189,248,0.3)' : 'rgba(255,255,255,0.07)'}`,
            }}
          >{id}</button>
        ))}
      </div>

      {detailLoading && <Spinner />}

      {detail && !detailLoading && (
        <div className="fade-in">
          {/* Status card */}
          <Card className="p-4 mb-4" accent={sevClr}>
            <div className="flex items-center gap-3 mb-2">
              <Badge level={detail.excursion_severity} label={detail.excursion_severity} />
              <span className="text-sm" style={{ color: '#94A3B8' }}>{detail.explanation}</span>
            </div>
            <div className="flex flex-wrap gap-4 text-xs mt-2" style={{ color: '#475569' }}>
              <span>Safe range: <b style={{ color: '#94A3B8' }}>{tMin}°C – {tMax}°C</b></span>
              <span>Risk: <b style={{ color: '#38BDF8' }}>{detail.cold_chain_risk_score}/100</b></span>
              <span>Latest: <b style={{ color: '#F1F5F9' }}>{detail.latest_temp_c ?? '—'}°C</b></span>
              <span>Min observed: {detail.min_observed_c ?? '—'}°C</span>
              <span>Max observed: {detail.max_observed_c ?? '—'}°C</span>
              <span>Excursions: <b style={{ color: '#FB923C' }}>{detail.excursion_count}</b></span>
            </div>
          </Card>

          {/* Chart */}
          {chartData.length > 0 && (
            <Card className="p-4">
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                  <XAxis dataKey="idx" tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} label={{ value: 'Reading #', position: 'insideBottom', offset: -2, fill: '#475569', fontSize: 11 }} />
                  <YAxis tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} label={{ value: '°C', position: 'insideLeft', fill: '#475569', fontSize: 11 }} />
                  <Tooltip content={<ChartTooltip />} />
                  {tMin != null && tMax != null && (
                    <ReferenceArea y1={tMin} y2={tMax} fill="rgba(52,211,153,0.07)" strokeOpacity={0} />
                  )}
                  {tMin != null && <ReferenceLine y={tMin} stroke="#34D399" strokeDasharray="4 4" strokeOpacity={0.5} />}
                  {tMax != null && <ReferenceLine y={tMax} stroke="#34D399" strokeDasharray="4 4" strokeOpacity={0.5} />}
                  <Line
                    type="monotone" dataKey="temp" name="Temp (°C)"
                    stroke="#38BDF8" strokeWidth={2.5} dot={{ r: 4, fill: '#38BDF8', stroke: '#070B14', strokeWidth: 1.5 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
              <div className="text-xs mt-2 text-center" style={{ color: '#475569' }}>
                Safe range: {tMin}°C – {tMax}°C · Readings: {detail.reading_count} · Excursions: {detail.excursion_count}
              </div>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}
