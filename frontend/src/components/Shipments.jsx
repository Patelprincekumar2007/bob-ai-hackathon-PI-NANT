import { useEffect, useState } from 'react'
import { apiFetch, apiPost } from '../api'
import { Badge, Card, Section, PageHeader, Spinner, Empty, FactorBar, riskColor, DataTable } from './ui'
import { soundEngine } from './effects'
import { Search, Sparkles, X, ArrowRight, ShieldCheck, Thermometer } from 'lucide-react'

const RISK_LEVELS = ['All', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW']

export default function Shipments() {
  const [scored, setScored]       = useState([])
  const [loading, setLoading]     = useState(true)
  const [riskFilter, setRisk]     = useState('All')
  const [search, setSearch]       = useState('')
  const [selected, setSelected]   = useState(null)
  const [detail, setDetail]       = useState(null)
  const [detailLoading, setDL]    = useState(false)
  const [aiResult, setAiResult]   = useState(null)
  const [aiLoading, setAiLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [predictionResult, setPredictionResult] = useState(null)

  useEffect(() => {
    apiFetch('/api/shipments')
      .then(d => { setScored(d); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!selected) return
    setDetail(null)
    setAiResult(null)
    setDL(true)
    apiFetch(`/api/shipments/${selected}`)
      .then(d => { setDetail(d); setDL(false) })
      .catch(() => setDL(false))
  }, [selected])

  const filtered = scored.filter(s => {
    if (riskFilter !== 'All' && s.classification !== riskFilter) return false
    if (search) {
      const q = search.toLowerCase()
      if (!s.shipment_id?.toLowerCase().includes(q) && !s.description?.toLowerCase().includes(q)) return false
    }
    return true
  })

  const handleAI = async () => {
    if (!detail) return
    soundEngine.playChime()
    setModalOpen(true)
    setAiLoading(true)
    setPredictionResult(null)
    setAiResult(null)

    // 1. Get ML Features
    const features = await apiFetch(`/api/ml/features/${selected}`).catch(() => null)
    if (!features) {
      setAiLoading(false)
      return
    }

    // 2. Predict Delay
    const predRes = await apiPost('/api/ml/predict', features).catch(() => null)
    const predictedDays = predRes?.success ? predRes.prediction : 0
    setPredictionResult(predictedDays)

    // 3. Gemini Explain
    const { risk, disruptions } = detail
    const dt = disruptions?.map(d => d.title).join('; ') || 'None'
    const prompt = `You are an elite autonomous maritime logistics intelligence analyst. Shipment ${selected} has a ML-predicted delay of ${predictedDays.toFixed(1)} days. Active disruptions & congestion: ${dt}. Risk level: ${risk?.classification}. Provide a precise executive summary explaining this delay prediction and prioritized mitigation vectors.`
    
    const r = await apiPost('/api/ai/explain', { prompt }).catch(() => null)
    setAiResult(r)
    setAiLoading(false)
  }

  const columns = [
    {
      key: 'shipment_id',
      label: 'SHIPMENT ID',
      render: v => (
        <span className="font-mono text-xs font-bold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-lg border border-blue-200">
          {v}
        </span>
      )
    },
    {
      key: 'description',
      label: 'CARGO SPEC & VOYAGE',
      render: (v, r) => (
        <div>
          <div className="text-slate-900 font-bold text-xs sm:text-sm">{v}</div>
          <div className="text-[11px] font-mono text-slate-400 flex items-center gap-1.5 mt-0.5">
            <span>{r.carrier || 'Global Carrier'}</span>
            <span>•</span>
            <span className="text-slate-500">ID: {r.shipment_id}</span>
          </div>
        </div>
      )
    },
    {
      key: 'score',
      label: 'COMPOSITE RISK',
      render: (v, r) => {
        const c = riskColor(r.classification)
        return (
          <div className="flex items-center gap-3">
            <span className="font-mono font-bold text-sm w-7" style={{ color: c.text }}>{v}</span>
            <div className="rounded-full overflow-hidden h-1.5 w-20 bg-slate-100 border border-slate-200">
              <div 
                className="h-full rounded-full transition-all duration-300" 
                style={{ width: `${v}%`, background: c.dot }} 
              />
            </div>
          </div>
        )
      }
    },
    {
      key: 'classification',
      label: 'STATUS TIER',
      render: v => <Badge level={v} label={v} />
    },
    {
      key: 'delay_days',
      label: 'PROJECTED DELAY',
      render: v => v > 0 ? (
        <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200">
          +{v}d Delay
        </span>
      ) : (
        <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
          On Schedule
        </span>
      )
    },
    {
      key: 'requires_cold_chain',
      label: 'REEFER SPECS',
      render: v => v ? (
        <span className="inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded bg-cyan-50 text-cyan-700 border border-cyan-200">
          <Thermometer size={12} />
          Active Reefer
        </span>
      ) : (
        <span className="text-slate-400 font-mono text-xs">— Standard Dry</span>
      )
    },
  ]

  return (
    <div className="space-y-6 animate-fade-in">
      {/* ── Top Header & Panoramic Hero Banner ────────────────────────────── */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-blue-500 text-base">✦</span>
            <h1 className="text-2xl font-black font-head tracking-tight text-slate-900">
              Shipments & Consignments
            </h1>
          </div>
          <p className="text-xs text-slate-500 mt-1 font-sans">
            Track multi-echelon active cargo telemetry, risk stratification, and watsonx dispatch advisories.
          </p>
        </div>

        {/* Hero Photo Banner Card ("Precision Logistics. Global Integrity.") */}
        <div className="relative rounded-2xl overflow-hidden shadow-xs border border-slate-200/80 w-full lg:w-[480px] h-[78px] flex-shrink-0 group">
          <img 
            src="/images/shipment_hero.jpg" 
            alt="Precision Logistics - Container Port Terminal"
            className="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-700"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-sky-950/75 via-blue-900/40 to-transparent flex items-center px-6">
            <div>
              <p className="text-white font-serif italic text-base md:text-lg tracking-wide drop-shadow-md">
                “Precision Logistics. Global Integrity.”
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Control bar: search & risk filter */}
      <div className="bg-white p-3 rounded-2xl border border-slate-200/80 shadow-xs flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div className="relative flex-1">
          <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
          <input
            className="w-full pl-9 pr-4 py-2 rounded-xl text-xs bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
            placeholder="Filter consignments by ID, cargo classification, or destination..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>

        <div className="flex items-center gap-1 bg-slate-50 p-1 rounded-xl border border-slate-200/60 overflow-x-auto">
          {RISK_LEVELS.map(l => {
            const isSel = riskFilter === l
            return (
              <button
                key={l}
                onClick={() => {
                  soundEngine.playClick()
                  setRisk(l)
                }}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                  isSel 
                    ? 'bg-blue-600 text-white shadow-xs' 
                    : 'text-slate-500 hover:text-slate-800 hover:bg-slate-200/60'
                }`}
              >
                {l}
              </button>
            )
          })}
        </div>
      </div>

      {/* Main content table */}
      {loading ? <Spinner /> : (
        <>
          <div className="flex items-center justify-between text-xs font-semibold text-slate-500 px-1">
            <span>SHOWING <b className="text-slate-900">{filtered.length}</b> OF <b className="text-slate-900">{scored.length}</b> ACTIVE CONSIGNMENTS</span>
            <span className="text-blue-600">Click any row to open Deep Telemetry Inspector</span>
          </div>

          {filtered.length === 0 ? (
            <Empty icon="🔍" message="No consignments match the specified criteria." />
          ) : (
            <DataTable
              columns={columns}
              rows={filtered}
              onRowClick={row => {
                soundEngine.playClick()
                setSelected(row.shipment_id)
              }}
            />
          )}
        </>
      )}

      {/* Deep Telemetry Inspector Drawer */}
      {selected && (
        <div className="mt-6 pt-5 border-t border-slate-200 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <span className="w-2.5 h-2.5 rounded-full bg-blue-600 animate-ping" />
              <h2 className="font-head text-lg font-bold text-slate-900">
                DEEP TELEMETRY INSPECTION — <span className="text-blue-600 font-mono">{selected}</span>
              </h2>
            </div>
            <button
              onClick={() => {
                soundEngine.playClick()
                setSelected(null)
              }}
              className="text-xs font-bold px-3 py-1.5 rounded-xl bg-white border border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-colors shadow-xs"
            >
              CLOSE INSPECTOR [ESC]
            </button>
          </div>

          {detailLoading ? <Spinner /> : detail ? (
            <div className="space-y-5">
              {/* Primary overview banner */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
                {/* Consignment Profile */}
                <Card className="lg:col-span-2 p-6">
                  <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-100">
                    <div>
                      <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Consignment Profile</div>
                      <div className="text-lg font-head font-bold text-slate-900 mt-0.5">{detail.raw?.description}</div>
                    </div>
                    <Badge level={detail.risk?.classification} label={detail.risk?.classification} />
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs">
                    <div>
                      <div className="text-slate-400 text-[10px] uppercase font-semibold">CARRIER VESSEL</div>
                      <div className="text-slate-900 font-bold mt-0.5">{detail.raw?.carrier || '—'}</div>
                    </div>
                    <div>
                      <div className="text-slate-400 text-[10px] uppercase font-semibold">CARGO TYPE</div>
                      <div className="text-slate-900 font-bold mt-0.5">{detail.raw?.cargo_type || '—'}</div>
                    </div>
                    <div>
                      <div className="text-slate-400 text-[10px] uppercase font-semibold">STATUS</div>
                      <div className="text-blue-600 font-bold mt-0.5">{detail.raw?.status || 'Active'}</div>
                    </div>
                    <div>
                      <div className="text-slate-400 text-[10px] uppercase font-semibold">ORIGIN HUB</div>
                      <div className="text-slate-900 font-bold mt-0.5">{detail.raw?.origin?.city}, {detail.raw?.origin?.country}</div>
                    </div>
                    <div>
                      <div className="text-slate-400 text-[10px] uppercase font-semibold">DESTINATION PORT</div>
                      <div className="text-slate-900 font-bold mt-0.5">{detail.raw?.destination?.city}, {detail.raw?.destination?.country}</div>
                    </div>
                    <div>
                      <div className="text-slate-400 text-[10px] uppercase font-semibold">DISPATCH PRIORITY</div>
                      <div className="text-amber-600 font-bold mt-0.5">{detail.raw?.priority || 'Standard'}</div>
                    </div>
                  </div>

                  {/* Route corridor transit visualization */}
                  <div className="mt-5 pt-4 border-t border-slate-100">
                    <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 mb-2">
                      <span className="text-blue-600 font-bold">
                        {detail.raw?.origin?.city} (Departure)
                      </span>
                      <span className="text-slate-400">In Transit Across Maritime Waypoint</span>
                      <span className="text-emerald-600 font-bold">
                        {detail.raw?.destination?.city} (Terminal)
                      </span>
                    </div>
                    <div className="relative h-2 rounded-full bg-slate-100 overflow-hidden border border-slate-200">
                      <div className="absolute top-0 left-0 bottom-0 w-3/5 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full" />
                    </div>
                  </div>
                </Card>

                {/* Risk score breakdown */}
                <Card className="p-6 flex flex-col justify-between">
                  <div>
                    <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">
                      Risk Stratification
                    </div>
                    {detail.risk && (
                      <>
                        <div className="flex items-baseline gap-2 mb-4">
                          <span 
                            className="font-head text-5xl font-extrabold tracking-tight"
                            style={{ color: riskColor(detail.risk.classification).text }}
                          >
                            {detail.risk.score}
                          </span>
                          <div>
                            <span className="text-xs font-mono text-slate-400">/ 100 COMPOSITE</span>
                            <div className="text-xs font-bold text-slate-700 mt-0.5">
                              {detail.risk.classification} HAZARD
                            </div>
                          </div>
                        </div>

                        <div className="space-y-2.5">
                          {Object.entries({
                            'Disruption Impact': [detail.risk.factor_breakdown?.disruption_severity, 35],
                            'Waypoint Delay':    [detail.risk.factor_breakdown?.delay, 25],
                            'SLA Pressure':      [detail.risk.factor_breakdown?.deadline_pressure, 20],
                            'Cargo Priority':    [detail.risk.factor_breakdown?.priority, 15],
                            'Thermal Excursion': [detail.risk.factor_breakdown?.cold_chain, 5],
                          }).map(([k, [v, m]]) => (
                            <FactorBar key={k} label={k} val={v || 0} max={m} />
                          ))}
                        </div>
                      </>
                    )}
                  </div>
                </Card>
              </div>

              {/* AI Neural Advisory (Gemini + Model) Button */}
              <div className="p-6 bg-gradient-to-br from-blue-50 via-indigo-50/50 to-white rounded-2xl border border-blue-200/80 shadow-xs space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center shadow-sm flex-shrink-0">
                      <Sparkles size={20} />
                    </div>
                    <div>
                      <h4 className="font-head font-bold text-slate-900 text-sm flex items-center gap-2">
                        AI Autonomous Advisory
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 font-semibold">
                          OUR MODEL + GEMINI
                        </span>
                      </h4>
                      <p className="text-xs text-slate-500">Synthesizes ML predicted delay and congestion mitigation vectors.</p>
                    </div>
                  </div>

                  <button
                    onClick={handleAI}
                    className="px-4 py-2 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-700 text-white shadow-xs transition-colors flex items-center gap-2"
                  >
                    Analyze Delay Prediction
                  </button>
                </div>
              </div>

            </div>
          ) : null}
        </div>
      )}

      {/* Modal for Prediction + Gemini */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl shadow-2xl border border-slate-200/80 w-full max-w-2xl overflow-hidden animate-fade-in duration-200">
            <div className="flex items-center justify-between p-4 border-b border-slate-100 bg-slate-50">
              <h3 className="font-head font-bold text-slate-900 flex items-center gap-2">
                <Sparkles size={18} className="text-blue-600" />
                AI Delay Prediction & Synthesis
              </h3>
              <button onClick={() => setModalOpen(false)} className="text-slate-400 hover:text-slate-600 p-1 rounded-md hover:bg-slate-200 transition-colors">
                <X size={18} />
              </button>
            </div>
            
            <div className="p-6 space-y-5">
              {aiLoading ? (
                <div className="flex flex-col items-center justify-center py-10">
                  <Spinner />
                  <p className="text-xs text-slate-500 mt-4 font-mono">Running ML Prediction Engine & Generating Gemini Synthesis...</p>
                </div>
              ) : (
                <>
                  <div className="flex items-center gap-5 bg-gradient-to-r from-blue-50 to-indigo-50 p-5 rounded-2xl border border-blue-100 shadow-inner">
                    <div className="w-14 h-14 rounded-full bg-blue-600 text-white flex items-center justify-center text-2xl font-black font-head shadow-md flex-shrink-0">
                      {predictionResult?.toFixed(1) || '0.0'}
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-slate-900">Predicted Delay (Days)</h4>
                      <p className="text-xs text-slate-500 mt-0.5">Computed via Random Forest Engine based on real-time features.</p>
                    </div>
                  </div>

                  {aiResult && (
                    <div className="text-sm text-slate-700 leading-relaxed max-h-[350px] overflow-y-auto pr-2 custom-scrollbar">
                      <div className="font-bold text-blue-600 mb-2 flex items-center gap-1.5">
                        <ShieldCheck size={16} />
                        <span>Gemini Executive Synthesis:</span>
                      </div>
                      <p className="whitespace-pre-wrap font-sans bg-white p-4 rounded-xl border border-slate-200 shadow-xs">{aiResult.text}</p>
                    </div>
                  )}
                </>
              )}
            </div>
            
            <div className="p-4 border-t border-slate-100 bg-slate-50 flex justify-end">
              <button 
                onClick={() => setModalOpen(false)}
                className="px-5 py-2.5 rounded-xl text-xs font-bold bg-slate-200 hover:bg-slate-300 text-slate-800 transition-colors shadow-xs"
              >
                Close Synthesis
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
