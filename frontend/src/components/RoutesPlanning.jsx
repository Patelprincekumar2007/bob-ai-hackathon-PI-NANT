import { useState, useEffect } from 'react'
import { apiFetch } from '../api'
import { 
  Route as RouteIcon, 
  ArrowRight, 
  ShieldCheck, 
  AlertTriangle, 
  Compass, 
  Ship, 
  Wind, 
  DollarSign, 
  Clock, 
  CheckCircle2, 
  Sliders, 
  Sparkles,
  Zap,
  ExternalLink,
  ChevronRight,
  Anchor
} from 'lucide-react'
import { soundEngine } from './effects'

export default function RoutesPlanning() {
  const [corridors, setCorridors] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedCorridorId, setSelectedCorridorId] = useState('ROUTE-EU-INDIA-01')
  const [selectedAltIndex, setSelectedAltIndex] = useState(0)
  const [speedKnots, setSpeedKnots] = useState(18)
  const [avoidCyclone, setAvoidCyclone] = useState(true)
  const [avoidStrike, setAvoidStrike] = useState(true)
  const [priorityReefer, setPriorityReefer] = useState(true)
  const [dispatchStatus, setDispatchStatus] = useState(null)

  useEffect(() => {
    apiFetch('/api/routes')
      .then(res => {
        setCorridors(res)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  // Comprehensive corridor definitions with rich operational telemetry
  const corridorCatalog = [
    {
      id: 'ROUTE-EU-INDIA-01',
      name: 'Europe → Western India Maritime Highway',
      origin: 'Rotterdam / Hamburg (DEHAM)',
      destination: 'Mumbai (INBOM)',
      carrier: 'MSC / Hapag-Lloyd',
      distanceNM: 6850,
      activeDisruption: 'Severe Cyclone – Arabian Sea (DISR-002)',
      disruptionSeverity: 'CRITICAL',
      baseTransitDays: 21,
      currentRiskScore: 75,
      baseRouteDesc: 'Via English Channel → Mediterranean → Suez Canal → Red Sea → Arabian Sea',
      alternatives: [
        {
          id: 'ALT-EU-IND-01',
          name: 'Cape of Good Hope Southern Divergence',
          via: 'ZACPT (Cape Town Offshore)',
          vessel: 'MV Nordic Frost (Reefer / V-003)',
          extraDays: 6,
          extraCost: 14000,
          riskMitigationPct: 72,
          projectedRiskScore: 21,
          fuelImpact: '+18% Marine Gasoil',
          co2Delta: '+124 MT',
          reason: 'Fully circumvents the Arabian Sea tropical cyclone track. Preserves cargo structural integrity for high-value pharmaceuticals.',
          steps: [
            'Depart Rotterdam Terminal ECT via Dover Strait',
            'South Atlantic passage clearing Canary Islands',
            'Transit Cape of Good Hope at 19.5 knots',
            'Ascend western Indian Ocean 400 NM south of cyclone cone',
            'Arrive Mumbai Port (INBOM) with 100% weather safety guarantee'
          ]
        },
        {
          id: 'ALT-EU-IND-02',
          name: 'Emergency Multimodal Air-Sea Relay',
          via: 'Frankfurt Air Cargo Hub (EDDF)',
          vessel: 'Lufthansa Cargo B777F + Feeder',
          extraDays: -4,
          extraCost: 95000,
          riskMitigationPct: 94,
          projectedRiskScore: 8,
          fuelImpact: '+280% Jet A-1',
          co2Delta: '+410 MT',
          reason: 'Emergency expedited option for time-critical pharmaceutical shipments. Reduces transit time by 4 days.',
          steps: [
            'Divert Reefer cargo at Hamburg to cold-storage facility',
            'Express bonded refrigerated truck convoy to Frankfurt Hub',
            'Direct air cargo charter flight to Mumbai Chhatrapati Shivaji',
            'Immediate customs expedited release within 6 hours'
          ]
        }
      ]
    },
    {
      id: 'ROUTE-TRANS-PAC-01',
      name: 'Trans-Pacific Strategic Corridor',
      origin: 'Shanghai (CNSHA)',
      destination: 'Los Angeles (USLAX)',
      carrier: 'MaerskLine / COSCO',
      distanceNM: 5720,
      activeDisruption: 'Shanghai Port Congestion (DISR-001) & US Customs (DISR-005)',
      disruptionSeverity: 'HIGH',
      baseTransitDays: 14,
      currentRiskScore: 65,
      baseRouteDesc: 'Direct Great Circle via East China Sea → North Pacific → US West Coast',
      alternatives: [
        {
          id: 'ALT-PAC-01',
          name: 'Ningbo Deepwater Feeder Bypass',
          via: 'CNNGB (Port of Ningbo-Zhoushan)',
          vessel: 'MV Southern Cross (Container / V-006)',
          extraDays: 1,
          extraCost: 2200,
          riskMitigationPct: 68,
          projectedRiskScore: 24,
          fuelImpact: '+4% Fuel Reserve',
          co2Delta: '+18 MT',
          reason: 'Port of Ningbo is operating normally at 54% berth utilization. Bypasses 42-vessel Shanghai backlog with short coastal road transfer.',
          steps: [
            'Dispatch 40-foot container chassis via Hangzhou Bay bridge',
            'Direct load at Ningbo Beilun Container Terminal 4',
            'Full sea transit across North Pacific at 20 knots',
            'Arrival at Port of Los Angeles Pier 400'
          ]
        },
        {
          id: 'ALT-PAC-02',
          name: 'Tianjin Intermodal Rail Divergence',
          via: 'CNTXG (Tianjin Port)',
          vessel: 'MV Pacific Pioneer (Container / V-001)',
          extraDays: 3,
          extraCost: 5800,
          riskMitigationPct: 62,
          projectedRiskScore: 28,
          fuelImpact: '+9% Intermodal Energy',
          co2Delta: '+42 MT',
          reason: 'Rail transfer to northern gateway completely skirts Yangtze estuary vessel bunching.',
          steps: [
            'Inland rail manifest booking via Shanghai Baoshan Terminal',
            'High-speed container freight rail to Tianjin Port',
            'Fast-track vessel loading on MV Pacific Pioneer',
            'Arrival at USLAX Terminal'
          ]
        }
      ]
    },
    {
      id: 'ROUTE-ATLANTIC-01',
      name: 'South America → Northern Europe Food Lane',
      origin: 'Santos (BRSSO)',
      destination: 'Rotterdam (NLRTM)',
      carrier: 'Hapag-Lloyd',
      distanceNM: 5480,
      activeDisruption: "Rotterdam Port Workers' Strike (DISR-003)",
      disruptionSeverity: 'HIGH',
      baseTransitDays: 16,
      currentRiskScore: 87,
      baseRouteDesc: 'South Atlantic → Mid-Atlantic Ridge → English Channel → Rotterdam Maasvlakte',
      alternatives: [
        {
          id: 'ALT-ATL-01',
          name: 'Antwerp Gateway Divergence',
          via: 'BEANR (Port of Antwerp-Bruges)',
          vessel: 'MV Rhine Express (Container / V-007)',
          extraDays: 2,
          extraCost: 5200,
          riskMitigationPct: 78,
          projectedRiskScore: 19,
          fuelImpact: '+6% Bunker Fuel',
          co2Delta: '+28 MT',
          reason: 'Antwerp is fully operating with open crane shifts and only 35 miles road connection to Rotterdam consignees. Essential for fresh fruit perishables.',
          steps: [
            'Direct ocean crossing from Santos on Hapag-Lloyd schedule',
            'Divert course past Ushant entering Scheldt estuary',
            'Discharge at Antwerp MPET Deurganckdock Terminal',
            'Reefer cold-truck distribution across Netherlands & Rhine-Ruhr'
          ]
        }
      ]
    },
    {
      id: 'ROUTE-APAC-AUS-01',
      name: 'Southeast Asia → Eastern Australia Express',
      origin: 'Singapore (SGSIN)',
      destination: 'Sydney (AUSYD)',
      carrier: 'CMA CGM / ONE',
      distanceNM: 4420,
      activeDisruption: 'None (Nominal Corridor)',
      disruptionSeverity: 'LOW',
      baseTransitDays: 11,
      currentRiskScore: 14,
      baseRouteDesc: 'Singapore Strait → Java Sea → Torres Strait / Bass Strait → Sydney Botany',
      alternatives: [
        {
          id: 'ALT-AUS-01',
          name: 'Standard Nominal Schedule Optimization',
          via: 'Direct Open Ocean Route',
          vessel: 'MV Orient Express (Container / V-002)',
          extraDays: 0,
          extraCost: 0,
          riskMitigationPct: 0,
          projectedRiskScore: 14,
          fuelImpact: 'Nominal baseline',
          co2Delta: '0 MT',
          reason: 'Corridor operating under ideal navigational conditions with zero maritime advisories.',
          steps: [
            'Standard departure from Singapore PSA',
            'Transit via Lombok Strait avoiding shallow reef zones',
            'Direct approach into Port Botany Container Terminal'
          ]
        }
      ]
    }
  ]

  const currentCorridor = corridorCatalog.find(c => c.id === selectedCorridorId) || corridorCatalog[0]
  const currentAlt = currentCorridor.alternatives[selectedAltIndex] || currentCorridor.alternatives[0]

  const handleAuthorizeDispatch = () => {
    soundEngine.playSuccess()
    setDispatchStatus(`Authorized autonomous reroute order via ${currentAlt.name}. Dispatched to fleet vessel ${currentAlt.vessel}.`)
    setTimeout(() => setDispatchStatus(null), 8000)
  }

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* ── Top Header & Panoramic Hero Banner ────────────────────────────── */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-blue-500 text-base">✦</span>
            <h1 className="text-2xl font-black font-head tracking-tight text-slate-900">
              Routes & Corridor Optimization
            </h1>
          </div>
          <p className="text-xs text-slate-500 mt-1 font-sans">
            Autonomous dynamic rerouting engine powered by watsonx maritime reasoning and real-time chokepoint telemetry.
          </p>
        </div>

        {/* Hero Photo Banner Card */}
        <div className="relative rounded-2xl overflow-hidden shadow-xs border border-slate-200/80 w-full lg:w-[480px] h-[78px] flex-shrink-0 group">
          <img 
            src="/images/shipment_hero.jpg" 
            alt="Dynamic Maritime Corridors"
            className="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-700"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-sky-950/80 via-blue-900/40 to-transparent flex items-center px-6">
            <div>
              <p className="text-white font-serif italic text-base md:text-lg tracking-wide drop-shadow-md">
                “Intelligent Corridors. Zero Stagnation.”
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* ── Corridor Selection Bar ────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {corridorCatalog.map(corr => {
          const isSelected = corr.id === selectedCorridorId
          const isCrit = corr.disruptionSeverity === 'CRITICAL'
          const isHigh = corr.disruptionSeverity === 'HIGH'
          return (
            <button
              key={corr.id}
              onClick={() => {
                soundEngine.playClick()
                setSelectedCorridorId(corr.id)
                setSelectedAltIndex(0)
              }}
              className={`p-4 rounded-2xl text-left border transition-all flex flex-col justify-between ${
                isSelected 
                  ? 'bg-blue-50/70 border-blue-500 shadow-sm ring-2 ring-blue-500/20' 
                  : 'bg-white border-slate-200/80 hover:border-slate-300 shadow-xs'
              }`}
            >
              <div className="flex items-center justify-between w-full">
                <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded-md bg-slate-100 text-slate-700">
                  {corr.id}
                </span>
                <span className={`text-[9px] font-bold font-mono px-2 py-0.5 rounded-md border ${
                  isCrit ? 'bg-rose-50 text-rose-700 border-rose-200' :
                  isHigh ? 'bg-amber-50 text-amber-700 border-amber-200' :
                  'bg-emerald-50 text-emerald-700 border-emerald-200'
                }`}>
                  {corr.disruptionSeverity}
                </span>
              </div>

              <div className="mt-2.5">
                <div className="text-xs font-bold text-slate-900 leading-snug">
                  {corr.name}
                </div>
                <div className="text-[11px] text-slate-500 mt-1 flex items-center gap-1 font-mono">
                  <span>{corr.distanceNM.toLocaleString()} NM</span>
                  <span>•</span>
                  <span>{corr.baseTransitDays}d base</span>
                </div>
              </div>

              <div className="mt-3 pt-2 border-t border-slate-100 text-[10px] text-slate-500 truncate flex items-center justify-between">
                <span className="truncate max-w-[170px]">{corr.activeDisruption}</span>
                <ChevronRight size={13} className={isSelected ? 'text-blue-600' : 'text-slate-300'} />
              </div>
            </button>
          )
        })}
      </div>

      {/* Dispatch Success Banner */}
      {dispatchStatus && (
        <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs font-medium flex items-center gap-3 animate-fade-in shadow-xs">
          <CheckCircle2 size={18} className="text-emerald-600 flex-shrink-0" />
          <div className="flex-1">{dispatchStatus}</div>
        </div>
      )}

      {/* ── Main Corridor Analysis & Optimization Workbench ────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* Left: Interactive Corridor Schema & Waypoint Navigator (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200/80 shadow-xs p-5 flex flex-col justify-between space-y-4">
          
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <div className="flex items-center gap-2">
                <RouteIcon size={16} className="text-blue-600" />
                <h2 className="text-sm font-bold font-head text-slate-900">
                  {currentCorridor.name}
                </h2>
              </div>
              <p className="text-[11px] text-slate-400 font-mono mt-0.5">
                {currentCorridor.origin} → {currentCorridor.destination} ({currentCorridor.carrier})
              </p>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-[11px] text-slate-400">Baseline Risk:</span>
              <span className="font-mono font-bold text-xs px-2 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200">
                {currentCorridor.currentRiskScore} / 100
              </span>
            </div>
          </div>

          {/* Active Disruption Threat Alert Box */}
          <div className="p-3.5 rounded-xl bg-amber-50/70 border border-amber-200/80 flex items-start gap-3">
            <AlertTriangle size={16} className="text-amber-600 flex-shrink-0 mt-0.5" />
            <div className="text-xs">
              <div className="font-bold text-amber-900">Active Corridor Bottleneck Detected</div>
              <div className="text-amber-800/90 text-[11px] mt-0.5 leading-relaxed">
                {currentCorridor.activeDisruption}. Base voyage passage currently incurs unacceptable delay and thermal excursion risks.
              </div>
            </div>
          </div>

          {/* Strategic Corridor Comparison & Feasibility Matrix */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
            {/* Base Disrupted Corridor Card */}
            <div className="bg-rose-50/40 rounded-xl p-3.5 border border-rose-200/80 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-rose-700 bg-rose-100/80 px-2 py-0.5 rounded">
                    Baseline Track
                  </span>
                  <span className="text-[11px] font-mono text-rose-600 font-semibold">
                    Risk: {currentCorridor.currentRiskScore}/100
                  </span>
                </div>
                <div className="text-xs font-bold text-slate-900 mt-2">
                  Direct Corridor (Disrupted)
                </div>
                <div className="text-[11px] text-slate-500 mt-0.5">
                  Subject to active bottleneck: {currentCorridor.activeDisruption.split('—')[0]}
                </div>
              </div>

              <div className="mt-3 pt-2.5 border-t border-rose-200/60 space-y-1.5 text-xs font-mono">
                <div className="flex items-center justify-between text-slate-600">
                  <span>Projected Delay:</span>
                  <span className="font-bold text-rose-700">+{currentAlt.extraDays > 0 ? currentAlt.extraDays + 4 : 5} Days</span>
                </div>
                <div className="flex items-center justify-between text-slate-600">
                  <span>Vulnerability:</span>
                  <span className="font-bold text-rose-700">Critical (Impassable)</span>
                </div>
              </div>
            </div>

            {/* Watsonx Recommended Contingency Vector */}
            <div className="bg-sky-50/40 rounded-xl p-3.5 border border-sky-200/80 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-sky-700 bg-sky-100/80 px-2 py-0.5 rounded">
                    ✦ AI Contingency
                  </span>
                  <span className="text-[11px] font-mono text-emerald-600 font-semibold">
                    Mitigation: {currentAlt.riskMitigationPct}%
                  </span>
                </div>
                <div className="text-xs font-bold text-slate-900 mt-2">
                  {currentAlt.name}
                </div>
                <div className="text-[11px] text-slate-500 mt-0.5">
                  Via {currentAlt.via} • Mode: {currentAlt.type}
                </div>
              </div>

              <div className="mt-3 pt-2.5 border-t border-sky-200/60 space-y-1.5 text-xs font-mono">
                <div className="flex items-center justify-between text-slate-600">
                  <span>Added Transit:</span>
                  <span className="font-bold text-slate-800">+{currentAlt.extraDays} Days</span>
                </div>
                <div className="flex items-center justify-between text-slate-600">
                  <span>Budget Delta:</span>
                  <span className="font-bold text-slate-800">+${currentAlt.extraCost.toLocaleString()}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Stepped Operational Execution Plan */}
          <div>
            <div className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2">
              Autonomous Waypoint Execution Sequence
            </div>
            <div className="space-y-1.5">
              {currentAlt.steps.map((step, idx) => (
                <div key={idx} className="flex items-center gap-2.5 text-xs text-slate-700 bg-slate-50 p-2 rounded-lg border border-slate-200/60">
                  <span className="w-5 h-5 rounded-full bg-blue-100 text-blue-700 font-mono font-bold text-[10px] flex items-center justify-center flex-shrink-0">
                    {idx + 1}
                  </span>
                  <span className="font-sans">{step}</span>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* Right: Alternative Strategy Evaluation & Dispatch Control (5 cols) */}
        <div className="lg:col-span-5 bg-white rounded-2xl border border-slate-200/80 shadow-xs p-5 flex flex-col justify-between space-y-4">
          
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="text-sm font-bold font-head text-slate-900">
                Recommended Alternative Vectors
              </h3>
              <span className="text-[10px] font-mono font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                {currentCorridor.alternatives.length} OPTIONS
              </span>
            </div>

            {/* Alternative Tabs */}
            <div className="flex items-center gap-2 mt-3 overflow-x-auto pb-1">
              {currentCorridor.alternatives.map((alt, idx) => (
                <button
                  key={alt.id}
                  onClick={() => {
                    soundEngine.playClick()
                    setSelectedAltIndex(idx)
                  }}
                  className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 flex-shrink-0 ${
                    selectedAltIndex === idx 
                      ? 'bg-blue-600 text-white shadow-xs' 
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  <span>Option {idx + 1}</span>
                  <span className="text-[10px] font-mono opacity-80">({alt.via.split(' ')[0]})</span>
                </button>
              ))}
            </div>

            {/* Alternative Card Details */}
            <div className="mt-4 p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-3">
              <div>
                <div className="text-sm font-bold text-slate-900">
                  {currentAlt.name}
                </div>
                <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                  {currentAlt.reason}
                </p>
              </div>

              {/* Comparative Metrics Grid */}
              <div className="grid grid-cols-2 gap-2 text-xs pt-2 border-t border-slate-200/60 font-mono">
                <div className="bg-white p-2.5 rounded-lg border border-slate-200/60">
                  <span className="text-slate-400 text-[10px] block">TRANSIT DELTA</span>
                  <span className={`font-bold text-sm ${currentAlt.extraDays <= 0 ? 'text-emerald-600' : 'text-slate-800'}`}>
                    {currentAlt.extraDays > 0 ? `+${currentAlt.extraDays} Days` : `${currentAlt.extraDays} Days`}
                  </span>
                </div>

                <div className="bg-white p-2.5 rounded-lg border border-slate-200/60">
                  <span className="text-slate-400 text-[10px] block">COST VARIANCE</span>
                  <span className="font-bold text-sm text-slate-800">
                    +${currentAlt.extraCost.toLocaleString()}
                  </span>
                </div>

                <div className="bg-white p-2.5 rounded-lg border border-slate-200/60">
                  <span className="text-slate-400 text-[10px] block">RISK MITIGATION</span>
                  <span className="font-bold text-sm text-emerald-600">
                    -{currentAlt.riskMitigationPct}% Risk
                  </span>
                </div>

                <div className="bg-white p-2.5 rounded-lg border border-slate-200/60">
                  <span className="text-slate-400 text-[10px] block">POST-ALT SCORE</span>
                  <span className="font-bold text-sm text-blue-600">
                    {currentAlt.projectedRiskScore} / 100
                  </span>
                </div>
              </div>

              {/* Assigned Asset Allocation */}
              <div className="flex items-center justify-between p-2.5 rounded-lg bg-blue-50/60 border border-blue-200/60 text-xs">
                <div className="flex items-center gap-2">
                  <Ship size={15} className="text-blue-600" />
                  <span className="text-slate-700">Assigned Fleet Vessel:</span>
                </div>
                <span className="font-bold font-mono text-blue-700">{currentAlt.vessel}</span>
              </div>
            </div>

            {/* Simulation Parameters */}
            <div className="mt-4 space-y-2.5">
              <div className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center justify-between">
                <span>Simulation Constraints</span>
                <span className="text-slate-400 text-[10px] font-mono">{speedKnots} KNOTS</span>
              </div>

              {/* Speed Slider */}
              <div>
                <input 
                  type="range" 
                  min="12" 
                  max="24" 
                  value={speedKnots} 
                  onChange={e => setSpeedKnots(Number(e.target.value))}
                  className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
                <div className="flex justify-between text-[9px] font-mono text-slate-400 mt-1">
                  <span>Eco (12 kts)</span>
                  <span>Service (18 kts)</span>
                  <span>Max Sprint (24 kts)</span>
                </div>
              </div>

              {/* Constraint Toggles */}
              <div className="space-y-1.5 pt-1 text-xs">
                <label className="flex items-center gap-2 text-slate-700 cursor-pointer">
                  <input 
                    type="checkbox" 
                    checked={avoidCyclone} 
                    onChange={e => setAvoidCyclone(e.target.checked)} 
                    className="rounded text-blue-600 focus:ring-0" 
                  />
                  <span>Hard Avoid Meteorological Storm Cones (&gt;50 kts)</span>
                </label>
                <label className="flex items-center gap-2 text-slate-700 cursor-pointer">
                  <input 
                    type="checkbox" 
                    checked={avoidStrike} 
                    onChange={e => setAvoidStrike(e.target.checked)} 
                    className="rounded text-blue-600 focus:ring-0" 
                  />
                  <span>Divert from Ports with Active Industrial Strikes</span>
                </label>
                <label className="flex items-center gap-2 text-slate-700 cursor-pointer">
                  <input 
                    type="checkbox" 
                    checked={priorityReefer} 
                    onChange={e => setPriorityReefer(e.target.checked)} 
                    className="rounded text-blue-600 focus:ring-0" 
                  />
                  <span>Priority Reefer Thermal Excursion Safeguard</span>
                </label>
              </div>
            </div>
          </div>

          {/* Action Button */}
          <div className="pt-3 border-t border-slate-100">
            <button
              onClick={handleAuthorizeDispatch}
              className="w-full py-3 px-4 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 group"
            >
              <Zap size={14} className="group-hover:scale-110 transition-transform" />
              <span>Authorize & Dispatch Autonomous Corridors</span>
            </button>
            <p className="text-[10px] text-center text-slate-400 mt-1.5">
              Powered by IBM watsonx.ai Decision Matrix & AIS Real-time Feeds
            </p>
          </div>

        </div>

      </div>

    </div>
  )
}
