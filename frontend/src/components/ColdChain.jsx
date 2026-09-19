import { useEffect, useState } from 'react'
import { apiFetch } from '../api'
import { KpiCard, Badge, Card, Section, PageHeader, Spinner, Empty, riskColor, ChartTooltip, DataTable } from './ui'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, ReferenceArea } from 'recharts'
import { soundEngine } from './effects'
import { Thermometer, CheckCircle2, AlertTriangle, Flame } from 'lucide-react'

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
        const reeferIds = shp.filter(s => s.requires_cold_chain).map(s => s.shipment_id)
        setIds(reeferIds)
        if (reeferIds.length > 0) setSel(reeferIds[0])
        setLoading(false)
      }).catch(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!selected) return
    setDetail(null)
    setDL(true)
    apiFetch(`/api/cold-chain/${selected}`)
      .then(d => { setDetail(d); setDL(false) })
      .catch(() => setDL(false))
  }, [selected])

  if (loading) return <Spinner />
  if (!data) return <Empty icon="⚠️" message="Failed to load cold chain telemetry data." />

  const { summary: s, alerts } = data

  const alertColumns = [
    {
      key: 'shipment_id',
      label: 'REEFER ID',
      render: v => (
        <span className="font-mono text-xs font-bold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-lg border border-blue-200">
          {v}
        </span>
      )
    },
    {
      key: 'cargo_type',
      label: 'PERISHABLE COMMODITY',
      render: v => <span className="text-slate-900 font-bold text-xs sm:text-sm">{v}</span>
    },
    {
      key: 'excursion_severity',
      label: 'EXCURSION SEVERITY',
      render: v => <Badge level={v} label={v} />
    },
    {
      key: 'excursion_count',
      label: 'EXCURSION EVENTS',
      render: v => (
        <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200">
          {v} Breaches
        </span>
      )
    },
    {
      key: 'cold_chain_risk_score',
      label: 'SPOILAGE RISK',
      render: v => {
        const c = riskColor(v >= 75 ? 'CRITICAL' : v >= 50 ? 'HIGH' : v >= 25 ? 'MEDIUM' : 'LOW')
        return (
          <span className="font-mono font-bold text-xs sm:text-sm" style={{ color: c.text }}>
            {v} / 100
          </span>
        )
      }
    },
    {
      key: 'latest_temp_c',
      label: 'TELEMETRY TEMP',
      render: v => (
        <span className="font-mono text-xs font-bold px-2.5 py-0.5 rounded bg-slate-100 text-slate-800 border border-slate-200">
          {v != null ? `${v}°C` : '—'}
        </span>
      )
    },
  ]

  const chartData = detail?.readings?.map((r, i) => ({
    idx: i + 1,
    temp: r.temperature_c,
    status: r.status,
    label: r.location || `Sample ${i + 1}`,
  })) || []

  const tMin = detail?.required_temp_min_c
  const tMax = detail?.required_temp_max_c
  const sevClr = detail ? riskColor(detail.excursion_severity).text : '#2563EB'

  return (
    <div className="space-y-6 animate-fade-in">
      {/* ── Top Header & Panoramic Hero Banner ────────────────────────────── */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-blue-500 text-base">✦</span>
            <h1 className="text-2xl font-black font-head tracking-tight text-slate-900">
              Cold Chain & Reefer Telemetry
            </h1>
          </div>
          <p className="text-xs text-slate-500 mt-1 font-sans">
            Real-time IoT temperature sensor monitoring, spoilage risk indexes, and thermal compliance boundaries.
          </p>
        </div>

        {/* Hero Photo Banner Card ("Unbroken Cold Chain. Uncompromising Quality.") */}
        <div className="relative rounded-2xl overflow-hidden shadow-xs border border-slate-200/80 w-full lg:w-[480px] h-[78px] flex-shrink-0 group">
          <img 
            src="/images/coldchain_hero.jpg" 
            alt="Unbroken Cold Chain - Oceanus Reefer Vessel"
            className="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-700"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-sky-950/75 via-blue-900/40 to-transparent flex items-center px-6">
            <div>
              <p className="text-white font-serif italic text-base md:text-lg tracking-wide drop-shadow-md">
                “Unbroken Cold Chain. Uncompromising Quality.”
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          icon={<Thermometer size={20} className="text-blue-600" />}
          value={s.total_tracked}
          label="Monitored Reefer Consignments"
          sub="Live Active Sensors"
        />
        <KpiCard
          icon={<CheckCircle2 size={20} className="text-emerald-600" />}
          value={s.normal_count}
          label="Nominal Compliance"
          accent="#10B981"
          sub="Within Thermal Band"
        />
        <KpiCard
          icon={<AlertTriangle size={20} className="text-amber-500" />}
          value={s.warning_count}
          label="Thermal Warning"
          accent="#F59E0B"
          sub="Approaching Excursion Limits"
        />
        <KpiCard
          icon={<Flame size={20} className="text-rose-600" />}
          value={s.critical_count}
          label="Critical Excursions"
          accent="#F43F5E"
          sub="Immediate Reefer Check Required"
        />
      </div>

      {/* Alerts Table */}
      {alerts?.length > 0 && (
        <div>
          <Section title={`Active Temperature Excursion Alerts (${alerts.length})`} />
          <DataTable
            columns={alertColumns}
            rows={alerts}
            onRowClick={row => {
              soundEngine.playClick()
              setSel(row.shipment_id)
            }}
          />
        </div>
      )}

      {/* Reefer Selector */}
      <div className="space-y-4">
        <Section title="Real-Time Thermal History Inspector" />
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          {shipmentIds.map(id => {
            const isSel = selected === id
            return (
              <button
                key={id}
                onClick={() => {
                  soundEngine.playClick()
                  setSel(id)
                }}
                className={`px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all flex items-center gap-2 whitespace-nowrap shadow-xs ${
                  isSel
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-600/25'
                    : 'bg-white text-slate-600 hover:text-slate-900 border border-slate-200/80 hover:bg-slate-50'
                }`}
              >
                <span className={`w-2 h-2 rounded-full ${isSel ? 'bg-white animate-pulse' : 'bg-slate-400'}`} />
                {id}
              </button>
            )
          })}
        </div>

        {detailLoading && <Spinner />}

        {detail && !detailLoading && (
          <div className="space-y-4">
            {/* Status Card */}
            <Card className="p-6" accent={sevClr}>
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 mb-4 border-b border-slate-100">
                <div className="flex items-center gap-3">
                  <Badge level={detail.excursion_severity} label={detail.excursion_severity} />
                  <span className="font-head font-bold text-base text-slate-900">{detail.explanation}</span>
                </div>
                <span className="font-mono text-xs text-blue-700 bg-blue-50 px-3 py-1 rounded-full border border-blue-200 font-bold">
                  SPOILAGE RISK: {detail.cold_chain_risk_score} / 100
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-5 gap-4 text-xs">
                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-semibold block">TARGET RANGE</span>
                  <span className="text-emerald-600 font-bold mt-0.5 block">{tMin}°C to {tMax}°C</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-semibold block">LATEST READING</span>
                  <span className="text-slate-900 font-bold mt-0.5 block">{detail.latest_temp_c ?? '—'}°C</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-semibold block">MIN OBSERVED</span>
                  <span className="text-slate-700 font-bold mt-0.5 block">{detail.min_observed_c ?? '—'}°C</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-semibold block">MAX OBSERVED</span>
                  <span className="text-slate-700 font-bold mt-0.5 block">{detail.max_observed_c ?? '—'}°C</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-semibold block">BREACH EVENTS</span>
                  <span className="text-amber-600 font-bold mt-0.5 block">{detail.excursion_count} Recorded</span>
                </div>
              </div>
            </Card>

            {/* Sensor Timeline Chart */}
            {chartData.length > 0 && (
              <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="font-head font-bold text-sm text-slate-900">Continuous IoT Thermal Timeline</h3>
                    <p className="text-xs text-slate-500 font-medium">Green shaded zone defines regulatory safe temperature envelope</p>
                  </div>
                  <div className="flex items-center gap-3 text-xs font-mono text-slate-500">
                    <span className="flex items-center gap-1.5">
                      <span className="w-2.5 h-2.5 rounded-full bg-blue-600" /> Sensor Stream
                    </span>
                    <span className="flex items-center gap-1.5">
                      <span className="w-2.5 h-1 bg-emerald-500" /> Safe Envelope
                    </span>
                  </div>
                </div>

                <ResponsiveContainer width="100%" height={260}>
                  <LineChart data={chartData} margin={{ top: 12, right: 12, left: -10, bottom: 0 }}>
                    <XAxis dataKey="idx" tick={{ fill: '#64748B', fontSize: 10, fontFamily: 'monospace' }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: '#64748B', fontSize: 10, fontFamily: 'monospace' }} axisLine={false} tickLine={false} />
                    <Tooltip content={<ChartTooltip />} />
                    {tMin != null && tMax != null && (
                      <ReferenceArea y1={tMin} y2={tMax} fill="rgba(16,185,129,0.08)" strokeOpacity={0} />
                    )}
                    {tMin != null && <ReferenceLine y={tMin} stroke="#10B981" strokeDasharray="4 4" strokeOpacity={0.6} />}
                    {tMax != null && <ReferenceLine y={tMax} stroke="#10B981" strokeDasharray="4 4" strokeOpacity={0.6} />}
                    <Line
                      type="monotone"
                      dataKey="temp"
                      name="Temperature (°C)"
                      stroke="#2563EB"
                      strokeWidth={3}
                      dot={{ r: 4, fill: '#2563EB', stroke: '#FFFFFF', strokeWidth: 2 }}
                      activeDot={{ r: 7, fill: '#2563EB', stroke: '#FFFFFF', strokeWidth: 2 }}
                    />
                  </LineChart>
                </ResponsiveContainer>

                <div className="text-[11px] font-mono text-slate-400 mt-4 text-center">
                  Total Telemetry Samples: {detail.reading_count} • Nominal Envelope: [{tMin}°C to {tMax}°C] • Excursions: {detail.excursion_count}
                </div>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
