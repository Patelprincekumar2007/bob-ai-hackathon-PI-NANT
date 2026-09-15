import { useEffect, useState } from 'react'
import { apiFetch } from '../api'
import { KpiCard, Card, Section, PageHeader, Spinner, Empty, DataTable } from './ui'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

export default function Fleet() {
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    apiFetch('/api/fleet').then(d => { setData(d); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  if (loading) return <Spinner />
  if (!data) return <Empty icon="⚠️" message="Failed to load fleet data." />

  const { summary: s, utilisation } = data

  const columns = [
    { key: 'vehicle_id', label: 'ID',      render: v => <span className="font-mono text-xs" style={{ color: '#38BDF8' }}>{v}</span> },
    { key: 'name',       label: 'Name',    render: v => <span style={{ color: '#F1F5F9' }}>{v}</span> },
    { key: 'carrier',    label: 'Carrier', render: v => <span style={{ color: '#94A3B8' }}>{v}</span> },
    { key: 'status',     label: 'Status',  render: v => <span style={{ color: '#64748B' }}>{v}</span> },
    { key: 'load_pct',   label: 'Load %',  render: v => (
      <div className="flex items-center gap-2">
        <span className="text-xs font-bold w-10" style={{ color: v >= 85 ? '#F87171' : v >= 60 ? '#FBBF24' : '#34D399' }}>{v}%</span>
        <div className="rounded-full overflow-hidden h-1.5 w-20" style={{ background: 'rgba(255,255,255,0.06)' }}>
          <div className="h-1.5 rounded-full" style={{ width: `${v}%`, background: v >= 85 ? '#F87171' : v >= 60 ? '#FBBF24' : '#34D399' }} />
        </div>
      </div>
    )},
    { key: 'available_teu', label: 'Avail. TEU', render: v => <span style={{ color: '#94A3B8' }}>{v}</span> },
    { key: 'assigned',   label: 'Assigned', render: v => v ? <span style={{ color: '#38BDF8' }}>Yes</span> : <span style={{ color: '#334155' }}>No</span> },
  ]

  return (
    <div className="fade-in">
      <PageHeader title="🚢 Fleet Management" subtitle="Vehicle utilisation, availability and assignment tracking" />

      <div className="grid grid-cols-3 lg:grid-cols-5 gap-3 mb-4">
        <KpiCard icon="🚢" value={s.total}                   label="Total Vehicles" />
        <KpiCard icon="✅" value={s.available}               label="Available" accent="#34D399" />
        <KpiCard icon="📦" value={s.assigned}               label="Assigned" />
        <KpiCard icon="💤" value={s.idle}                   label="Idle" />
        <KpiCard icon="📊" value={`${s.utilisation_pct}%`} label="Utilisation" />
      </div>
      <div className="grid grid-cols-3 gap-3 mb-6">
        <KpiCard icon="❄️" value={s.reefer_capable_count}              label="Reefer-Capable" />
        <KpiCard icon="📐" value={s.available_total_teu}               label="Available TEU" />
        <KpiCard icon="⚖️" value={s.available_total_weight_kg?.toLocaleString()} label="Avail. Weight kg" />
      </div>

      {/* Utilisation chart */}
      <Section title="Load Distribution" />
      <Card className="p-4 mb-6">
        <ResponsiveContainer width="100%" height={160}>
          <BarChart data={utilisation} barSize={20}>
            <XAxis dataKey="name" tick={{ fill: '#475569', fontSize: 10 }} axisLine={false} tickLine={false} interval={0} />
            <YAxis domain={[0,100]} tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={{ background: '#0D1424', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10, fontSize: 12 }} formatter={(v) => [`${v}%`, 'Load']} />
            <Bar dataKey="load_pct" radius={[4,4,0,0]}>
              {utilisation.map((v, i) => (
                <Cell key={i} fill={v.load_pct >= 85 ? '#F87171' : v.load_pct >= 60 ? '#FBBF24' : '#34D399'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Card>

      <Section title="Per-Vehicle Utilisation" />
      <DataTable columns={columns} rows={utilisation} />
    </div>
  )
}
