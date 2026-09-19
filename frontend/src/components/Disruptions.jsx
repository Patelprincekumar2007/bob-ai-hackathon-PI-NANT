import { useState, useEffect } from 'react'
import { apiFetch } from '../api'
import { 
  AlertTriangle, 
  CloudRain, 
  Flame, 
  Info, 
  CheckCircle2, 
  Search, 
  Filter as FilterIcon, 
  Calendar, 
  Anchor, 
  Wrench, 
  Users, 
  FileText, 
  MoreHorizontal, 
  X, 
  Clock, 
  DollarSign, 
  ArrowRight, 
  Route, 
  Sparkles,
  ChevronDown
} from 'lucide-react'
import { soundEngine } from './effects'

export default function Disruptions({ onNavigateToShipments }) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedId, setSelectedId] = useState('DISR-002')
  const [searchQuery, setSearchQuery] = useState('')
  const [activeDossierTab, setActiveDossierTab] = useState('Overview')
  const [aiInsightOpen, setAiInsightOpen] = useState(false)

  // Filters state
  const [statusFilter, setStatusFilter] = useState('All')
  const [severityFilter, setSeverityFilter] = useState('All')
  const [typeFilter, setTypeFilter] = useState('All')
  const [regionFilter, setRegionFilter] = useState('All')

  useEffect(() => {
    apiFetch('/api/disruptions')
      .then(res => {
        setData(res)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  // Comprehensive static dataset if API yields partial
  const allDisruptions = [
    {
      id: 'DISR-001',
      title: 'Shanghai Port Congestion',
      type: 'Port Congestion',
      icon: Anchor,
      severity: 'HIGH',
      affectedPorts: 'CNSHA',
      affectedRoutes: '2 routes',
      impactDays: '3 days',
      impactCost: '$4,500',
      startDate: '08 Jul 2025',
      estResolution: '02 Aug 2025',
      status: 'Active',
      description: 'Severe vessel backlog at Port of Shanghai (CNSHA) due to typhoon recovery and berth equipment maintenance.',
      carriers: 'COSCO, Evergreen',
      region: 'Asia',
    },
    {
      id: 'DISR-002',
      title: 'Severe Cyclone - Arabian Sea',
      type: 'Weather',
      icon: CloudRain,
      severity: 'CRITICAL',
      affectedPorts: 'INBOM, INPAV',
      affectedRoutes: '1 route',
      impactDays: '5 days',
      impactCost: '$12,000',
      startDate: '17 Jul 2025',
      estResolution: '24 Jul 2025',
      status: 'Active',
      description: 'Tropical cyclone causing route diversions and delays across EU-India trade lane.',
      carriers: 'MSC, Hapag-Lloyd',
      region: 'Indian Ocean',
      impactSummary: 'Wind speeds exceeding 90 knots. All vessels on EU-India routes advised to divert south. Significant delays expected for shipments to Mumbai and nearby ports.'
    },
    {
      id: 'DISR-003',
      title: "Rotterdam Port Workers' Strike",
      type: 'Strike',
      icon: Users,
      severity: 'HIGH',
      affectedPorts: 'NLRTM',
      affectedRoutes: '2 routes',
      impactDays: '8 days',
      impactCost: '$9,800',
      startDate: '13 Jul 2025',
      estResolution: '05 Aug 2025',
      status: 'Active',
      description: 'Unionised dock workers at Port of Rotterdam (NLRTM) strike over wage agreements, freezing container crane operations.',
      carriers: 'Maersk, CMA CGM',
      region: 'Europe',
    },
    {
      id: 'DISR-004',
      title: 'Vessel Engine Failure - MV Eastern Star',
      type: 'Vessel Failure',
      icon: Wrench,
      severity: 'CRITICAL',
      affectedPorts: 'V-005',
      affectedRoutes: '1 route',
      impactDays: '14 days',
      impactCost: '$35,000',
      startDate: '16 Jul 2025',
      estResolution: '01 Aug 2025',
      status: 'Active',
      description: 'Container vessel MV Eastern Star (V-005) suffered catastrophic propulsion failure en route to Santos.',
      carriers: 'ONE (Ocean Network Express)',
      region: 'Asia',
    },
    {
      id: 'DISR-005',
      title: 'US Customs Enhanced Inspection',
      type: 'Customs Delay',
      icon: FileText,
      severity: 'MEDIUM',
      affectedPorts: 'USLAX, USNYC',
      affectedRoutes: '2 routes',
      impactDays: '2 days',
      impactCost: '$1,200',
      startDate: '19 Jul 2025',
      estResolution: '26 Jul 2025',
      status: 'Monitoring',
      description: 'US Customs and Border Protection issued an enhanced security directive triggering mandatory x-ray scans for electronics.',
      carriers: 'Hapag-Lloyd, Maersk',
      region: 'North America',
    },
  ]

  const displayList = allDisruptions.filter(d => {
    if (statusFilter !== 'All' && d.status !== statusFilter) return false
    if (severityFilter !== 'All' && d.severity !== severityFilter) return false
    if (typeFilter !== 'All' && d.type !== typeFilter) return false
    if (regionFilter !== 'All' && d.region !== regionFilter) return false
    if (searchQuery) {
      const q = searchQuery.toLowerCase()
      if (!d.id.toLowerCase().includes(q) && !d.title.toLowerCase().includes(q) && !d.type.toLowerCase().includes(q)) return false
    }
    return true
  })

  const selectedDisruption = allDisruptions.find(d => d.id === selectedId) || allDisruptions[1]

  const severityBadge = (sev) => {
    switch (sev) {
      case 'CRITICAL':
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-50 text-rose-600 border border-rose-200">CRITICAL</span>
      case 'HIGH':
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-50 text-amber-600 border border-amber-200">HIGH</span>
      case 'MEDIUM':
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-50/80 text-amber-500 border border-amber-200/80">MEDIUM</span>
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-600 border border-emerald-200">LOW</span>
    }
  }

  const statusBadge = (st) => {
    if (st === 'Active') {
      return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">Active</span>
    }
    return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200">Monitoring</span>
  }

  return (
    <div className="space-y-6">
      
      {/* ── Header Title Banner with Hero Card ────────────────────── */}
      <div className="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-4">
        
        {/* Left Title */}
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-2xl bg-slate-900 text-white flex items-center justify-center shadow-sm flex-shrink-0">
            <AlertTriangle size={22} className="text-amber-400" />
          </div>
          <div>
            <h1 className="text-2xl sm:text-3xl font-head font-extrabold text-slate-900 tracking-tight">
              Disruptions
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 font-medium">
              Monitor global events that impact your shipments and plan ahead.
            </p>
          </div>
        </div>

        {/* Right Hero Container Banner */}
        <div className="relative rounded-2xl overflow-hidden shadow-sm border border-slate-200/80 min-w-[320px] max-w-md h-20 flex items-center px-5">
          <img 
            src="/images/smartroute_hero_bg.jpg" 
            alt="Maritime Hero" 
            className="absolute inset-0 w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-slate-900/90 via-slate-900/70 to-slate-900/40" />
          <div className="relative z-10">
            <p className="text-sm font-head font-bold italic text-white tracking-wide">
              "From Uncertainty to Preparedness"
            </p>
            <span className="text-[10px] font-mono text-cyan-300 font-medium">
              Real-time Global Satellite Radar
            </span>
          </div>
        </div>

      </div>

      {/* ── 5 KPI Metric Cards Row ─────────────────────────────────── */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
        
        {/* Active Disruptions */}
        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
              <CloudRain size={20} />
            </div>
            <span className="text-xs font-bold font-mono text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
              ↑ 25%
            </span>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold font-head text-slate-900">5</div>
            <div className="text-xs font-bold text-slate-700 mt-0.5">Active Disruptions</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Currently impacting operations</div>
          </div>
        </div>

        {/* Critical */}
        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <div className="w-9 h-9 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center">
              <Flame size={20} />
            </div>
            <span className="text-xs font-bold font-mono text-rose-600 bg-rose-50 px-2 py-0.5 rounded-full border border-rose-200">
              ↑ 50%
            </span>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold font-head text-slate-900">3</div>
            <div className="text-xs font-bold text-slate-700 mt-0.5">Critical</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Immediate action required</div>
          </div>
        </div>

        {/* High */}
        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <div className="w-9 h-9 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
              <AlertTriangle size={20} />
            </div>
            <span className="text-xs font-bold font-mono text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">
              → 0%
            </span>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold font-head text-slate-900">1</div>
            <div className="text-xs font-bold text-slate-700 mt-0.5">High</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Monitor closely</div>
          </div>
        </div>

        {/* Medium */}
        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
              <Info size={20} />
            </div>
            <span className="text-xs font-bold font-mono text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full border border-blue-200">
              ↓ 33%
            </span>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold font-head text-slate-900">1</div>
            <div className="text-xs font-bold text-slate-700 mt-0.5">Medium</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Keep under review</div>
          </div>
        </div>

        {/* Low */}
        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <div className="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <CheckCircle2 size={20} />
            </div>
            <span className="text-xs font-bold font-mono text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
              ↓ 100%
            </span>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold font-head text-slate-900">0</div>
            <div className="text-xs font-bold text-slate-700 mt-0.5">Low</div>
            <div className="text-[11px] text-slate-400 mt-0.5">No major issues</div>
          </div>
        </div>

      </div>

      {/* ── Search & Filter Bar ────────────────────────────────────── */}
      <div className="bg-white p-3.5 rounded-2xl border border-slate-200 shadow-xs flex flex-wrap items-center gap-3">
        
        {/* Search input */}
        <div className="relative flex-1 min-w-[220px]">
          <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by ID, title, port, route, or keyword..."
            className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
          />
        </div>

        {/* Status dropdown */}
        <div className="relative">
          <select 
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="appearance-none bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 pr-7 text-xs font-medium text-slate-700 focus:outline-none focus:border-blue-500 cursor-pointer"
          >
            <option value="All">Status: All</option>
            <option value="Active">Active</option>
            <option value="Monitoring">Monitoring</option>
          </select>
          <ChevronDown size={14} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
        </div>

        {/* Severity dropdown */}
        <div className="relative">
          <select 
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="appearance-none bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 pr-7 text-xs font-medium text-slate-700 focus:outline-none focus:border-blue-500 cursor-pointer"
          >
            <option value="All">Severity: All</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
          </select>
          <ChevronDown size={14} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
        </div>

        {/* Type dropdown */}
        <div className="relative">
          <select 
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="appearance-none bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 pr-7 text-xs font-medium text-slate-700 focus:outline-none focus:border-blue-500 cursor-pointer"
          >
            <option value="All">Type: All</option>
            <option value="Port Congestion">Port Congestion</option>
            <option value="Weather">Weather</option>
            <option value="Strike">Strike</option>
            <option value="Vessel Failure">Vessel Failure</option>
            <option value="Customs Delay">Customs Delay</option>
          </select>
          <ChevronDown size={14} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
        </div>

        {/* Region dropdown */}
        <div className="relative">
          <select 
            value={regionFilter}
            onChange={(e) => setRegionFilter(e.target.value)}
            className="appearance-none bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 pr-7 text-xs font-medium text-slate-700 focus:outline-none focus:border-blue-500 cursor-pointer"
          >
            <option value="All">Region: All</option>
            <option value="Asia">Asia</option>
            <option value="Europe">Europe</option>
            <option value="North America">North America</option>
            <option value="Indian Ocean">Indian Ocean</option>
          </select>
          <ChevronDown size={14} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
        </div>

        {/* Date Range Picker Placeholder */}
        <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-medium text-slate-600">
          <span>Select dates</span>
          <Calendar size={14} className="text-slate-400" />
        </div>

        {/* Filter Button */}
        <button 
          onClick={() => soundEngine.playClick()}
          className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-xl text-xs font-semibold shadow-xs transition-colors"
        >
          <FilterIcon size={14} />
          <span>Filter</span>
        </button>

        {/* Clear Button */}
        <button 
          onClick={() => {
            soundEngine.playClick()
            setStatusFilter('All')
            setSeverityFilter('All')
            setTypeFilter('All')
            setRegionFilter('All')
            setSearchQuery('')
          }}
          className="text-xs font-semibold text-slate-500 hover:text-slate-800 px-2 py-2 transition-colors"
        >
          Clear
        </button>

      </div>

      {/* ── Main Split View: Table (Left) & Deep Dossier (Right) ───── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* Left Side: Active Disruptions Table */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
          <div className="p-4 border-b border-slate-100 flex items-center justify-between">
            <h2 className="text-sm font-bold font-head text-slate-900">
              Active Disruptions ({displayList.length})
            </h2>
            <span className="text-xs font-medium text-slate-400">
              Showing 1–{displayList.length} of {displayList.length} disruptions
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-50/70 border-b border-slate-200/80 text-slate-500 font-semibold uppercase tracking-wider text-[10px]">
                  <th className="p-3 pl-4 w-8"><input type="checkbox" className="rounded text-blue-600 focus:ring-0" /></th>
                  <th className="p-3">ID</th>
                  <th className="p-3">Title</th>
                  <th className="p-3">Type</th>
                  <th className="p-3">Severity</th>
                  <th className="p-3">Affected Ports / Routes</th>
                  <th className="p-3">Impact</th>
                  <th className="p-3">Start Date</th>
                  <th className="p-3">Est. Resolution</th>
                  <th className="p-3">Status</th>
                  <th className="p-3 pr-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {displayList.map(item => {
                  const isSelected = selectedId === item.id
                  const Icon = item.icon
                  return (
                    <tr 
                      key={item.id}
                      onClick={() => {
                        soundEngine.playClick()
                        setSelectedId(item.id)
                      }}
                      className={`cursor-pointer transition-colors ${
                        isSelected 
                          ? 'bg-blue-50/60 font-medium' 
                          : 'hover:bg-slate-50/80'
                      }`}
                    >
                      <td className="p-3 pl-4" onClick={(e) => e.stopPropagation()}>
                        <input type="checkbox" checked={isSelected} onChange={() => {}} className="rounded text-blue-600 focus:ring-0" />
                      </td>
                      <td className="p-3 font-mono font-bold text-blue-600">
                        {item.id}
                      </td>
                      <td className="p-3">
                        <div className="flex items-center gap-2">
                          <span className="p-1 rounded bg-slate-100 text-slate-600">
                            <Icon size={13} />
                          </span>
                          <span className="font-semibold text-slate-800 truncate max-w-[140px]">
                            {item.title}
                          </span>
                        </div>
                      </td>
                      <td className="p-3 text-slate-600">
                        {item.type}
                      </td>
                      <td className="p-3">
                        {severityBadge(item.severity)}
                      </td>
                      <td className="p-3">
                        <div className="font-semibold text-slate-700">{item.affectedPorts}</div>
                        <div className="text-[10px] text-slate-400">{item.affectedRoutes}</div>
                      </td>
                      <td className="p-3">
                        <div className="font-semibold text-slate-800">{item.impactDays}</div>
                        <div className="text-[10px] text-slate-400">{item.impactCost}</div>
                      </td>
                      <td className="p-3 text-slate-600 font-mono text-[11px]">
                        {item.startDate}
                      </td>
                      <td className="p-3 text-slate-600 font-mono text-[11px]">
                        {item.estResolution}
                      </td>
                      <td className="p-3">
                        {statusBadge(item.status)}
                      </td>
                      <td className="p-3 pr-4 text-right">
                        <button className="text-slate-400 hover:text-slate-600 p-1">
                          <MoreHorizontal size={14} />
                        </button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right Side: Deep Disruption Dossier */}
        {selectedDisruption && (
          <div className="lg:col-span-5 bg-white rounded-2xl border border-slate-200 shadow-xs p-5 flex flex-col justify-between space-y-4">
            
            {/* Header with Title and Close */}
            <div>
              <div className="flex items-center justify-between pb-2">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-slate-900">{selectedDisruption.id}</span>
                  {severityBadge(selectedDisruption.severity)}
                </div>
                <button 
                  onClick={() => soundEngine.playClick()}
                  className="text-slate-400 hover:text-slate-600 p-1 rounded-lg hover:bg-slate-100"
                >
                  <X size={16} />
                </button>
              </div>

              <h3 className="text-lg font-head font-extrabold text-slate-900">
                {selectedDisruption.title}
              </h3>
              <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">
                {selectedDisruption.description}
              </p>

              {/* Sub-tabs: Overview, Affected Shipments, Alternative Routes, Updates */}
              <div className="flex items-center gap-4 mt-3 border-b border-slate-100 text-xs font-semibold">
                {['Overview', 'Affected Shipments (2)', 'Alternative Routes', 'Updates'].map(tab => (
                  <button
                    key={tab}
                    onClick={() => {
                      soundEngine.playClick()
                      setActiveDossierTab(tab)
                    }}
                    className={`pb-2 transition-colors relative ${
                      activeDossierTab === tab 
                        ? 'text-blue-600 border-b-2 border-blue-600' 
                        : 'text-slate-400 hover:text-slate-600'
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              {/* Metadata Grid */}
              <div className="grid grid-cols-2 gap-y-2 gap-x-4 text-xs mt-3.5 py-2 border-b border-slate-100">
                <div className="flex justify-between">
                  <span className="text-slate-400">Type</span>
                  <span className="font-medium text-slate-800">{selectedDisruption.type} Event</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Severity</span>
                  <span>{severityBadge(selectedDisruption.severity)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Status</span>
                  <span>{statusBadge(selectedDisruption.status)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Start Date</span>
                  <span className="font-mono text-slate-700">{selectedDisruption.startDate}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Est. Resolution</span>
                  <span className="font-mono text-slate-700">{selectedDisruption.estResolution}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Est. Delay</span>
                  <span className="font-bold text-rose-600">{selectedDisruption.impactDays}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Additional Cost</span>
                  <span className="font-bold text-slate-800">{selectedDisruption.impactCost}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Affected Ports</span>
                  <span className="font-mono text-slate-800 font-semibold">{selectedDisruption.affectedPorts}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Affected Routes</span>
                  <span className="font-mono text-slate-800">ROUTE-EU-INDIA-01</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Carriers</span>
                  <span className="text-slate-800 font-medium">{selectedDisruption.carriers}</span>
                </div>
              </div>

              {/* ── Dynamic Disruption Visual Graphic & Telemetry Overlay ─────────── */}
              {(() => {
                const visualsMap = {
                  'DISR-001': {
                    image: '/images/disr_shanghai.jpg',
                    alt: 'Port of Shanghai AIS Anchorage Congestion',
                    badgeText: 'ANCHORAGE QUEUE: 58 VESSELS (CNSHA)',
                    badgeBorder: 'border-amber-500/80',
                    pulseColor: 'bg-amber-500',
                    legend: [
                      { label: 'AIS Queue 58', color: 'bg-amber-500' },
                      { label: 'Yangtze Estuary', color: 'bg-sky-400' },
                      { label: 'Berth 98.4%', color: 'bg-rose-500' }
                    ],
                    impactBoxClass: 'bg-amber-50 border-amber-200/80',
                    impactTitleClass: 'text-amber-800',
                    impactTextClass: 'text-amber-900/90',
                    impactTitle: 'Anchorage Congestion & Berth Delay Summary',
                    impactSummary: 'Severe vessel bunching outside Shanghai. 42 container vessels waiting at anchor with average delay of 3.2 days. Rerouting via Port of Ningbo (CNNGB) recommended to save 48+ hours.'
                  },
                  'DISR-002': {
                    image: '/images/cyclone_radar.jpg',
                    alt: 'Satellite Weather Radar - Arabian Sea Tropical Cyclone',
                    badgeText: 'CURRENT POSITION: ARABIAN SEA',
                    badgeBorder: 'border-red-500/80',
                    pulseColor: 'bg-red-500',
                    legend: [
                      { label: 'Storm Track', color: 'bg-red-500' },
                      { label: 'Forecast Path', color: 'bg-sky-400' },
                      { label: 'Affected Ports', color: 'bg-blue-500' }
                    ],
                    impactBoxClass: 'bg-rose-50 border-rose-200/80',
                    impactTitleClass: 'text-rose-700',
                    impactTextClass: 'text-rose-900/90',
                    impactTitle: 'Meteorological Cyclone Impact Summary',
                    impactSummary: 'Wind speeds exceeding 90 knots. All vessels on EU-India routes advised to divert south. Significant delays expected for shipments to Mumbai and nearby ports.'
                  },
                  'DISR-003': {
                    image: '/images/disr_rotterdam.jpg',
                    alt: 'Port of Rotterdam Terminal Gate Lockdown',
                    badgeText: 'TERMINAL LOCKDOWN: ROTTERDAM ECT',
                    badgeBorder: 'border-amber-500/80',
                    pulseColor: 'bg-amber-500',
                    legend: [
                      { label: 'Gantry Halted', color: 'bg-rose-500' },
                      { label: 'Gate Blocked', color: 'bg-amber-500' },
                      { label: 'Divert Antwerp', color: 'bg-emerald-400' }
                    ],
                    impactBoxClass: 'bg-amber-50 border-amber-200/80',
                    impactTitleClass: 'text-amber-800',
                    impactTextClass: 'text-amber-900/90',
                    impactTitle: 'Dock Workers Strike Operational Assessment',
                    impactSummary: 'Dock workers union strike halted container crane operations at ECT Delta Terminal. 8 days estimated delay. Immediate diversion of perishables to Antwerp-Bruges (BEANR) recommended.'
                  },
                  'DISR-004': {
                    image: '/images/disr_vessel_failure.jpg',
                    alt: 'MV Eastern Star Dead-in-Water AIS Distress Telemetry',
                    badgeText: 'SOS DISTRESS: DRIFTING IN INDIAN OCEAN',
                    badgeBorder: 'border-rose-600/80',
                    pulseColor: 'bg-rose-600',
                    legend: [
                      { label: 'Drift 0.8 kts', color: 'bg-rose-500' },
                      { label: 'Salvage Radius', color: 'bg-amber-400' },
                      { label: 'Colombo Tug', color: 'bg-sky-400' }
                    ],
                    impactBoxClass: 'bg-rose-50 border-rose-200/80',
                    impactTitleClass: 'text-rose-700',
                    impactTextClass: 'text-rose-900/90',
                    impactTitle: 'Propulsion Breakdown & Salvage Protocol',
                    impactSummary: 'MV Eastern Star (V-005) main engine failure. Vessel dead-in-water drifting east at 0.8 knots. Salvage tug dispatched from Colombo. 14 days delay; transshipment at Singapore mandatory.'
                  },
                  'DISR-005': {
                    image: '/images/disr_customs.jpg',
                    alt: 'Port Security Customs X-Ray Container Scanner',
                    badgeText: 'BORDER SECURITY SCANNING: USLAX',
                    badgeBorder: 'border-blue-500/80',
                    pulseColor: 'bg-blue-500',
                    legend: [
                      { label: 'Portal Scanner', color: 'bg-blue-500' },
                      { label: 'Secondary Hold', color: 'bg-amber-400' },
                      { label: 'Queue 48 hrs', color: 'bg-emerald-400' }
                    ],
                    impactBoxClass: 'bg-blue-50 border-blue-200/80',
                    impactTitleClass: 'text-blue-800',
                    impactTextClass: 'text-blue-900/90',
                    impactTitle: 'Customs Regulatory Examination Hold',
                    impactSummary: 'US Customs & Border Protection enhanced 100% portal x-ray examinations on incoming semiconductor cargo. Average 48h clearance hold. Expedited ACE pre-filing initiated.'
                  }
                }

                const currentVisual = visualsMap[selectedDisruption.id] || visualsMap['DISR-002']

                return (
                  <>
                    <div className="mt-3.5 relative rounded-xl overflow-hidden bg-slate-950 border border-slate-700/60 h-44 flex items-center justify-center group shadow-inner">
                      <img 
                        src={currentVisual.image} 
                        alt={currentVisual.alt} 
                        className="w-full h-full object-cover object-center opacity-85 group-hover:scale-105 transition-transform duration-700"
                      />
                      
                      {/* Visual Radar Overlay Gradients */}
                      <div className="absolute inset-0 bg-gradient-to-t from-slate-950/90 via-slate-950/20 to-slate-950/50 pointer-events-none" />

                      {/* Vector Overlay based on disruption type */}
                      {selectedDisruption.id === 'DISR-002' && (
                        <svg className="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 400 176">
                          <path d="M 195 90 Q 250 65 330 45" fill="none" stroke="#38bdf8" strokeWidth="2.5" strokeDasharray="5 3" />
                          <circle cx="330" cy="45" r="4" fill="#38bdf8" />
                          <circle cx="260" cy="63" r="3" fill="#38bdf8" />
                          <path d="M 90 145 Q 140 120 195 90" fill="none" stroke="#ef4444" strokeWidth="2.5" strokeDasharray="4 2" />
                          <circle cx="90" cy="145" r="3.5" fill="#ef4444" />
                          <circle cx="140" cy="120" r="3.5" fill="#ef4444" />
                          <circle cx="195" cy="90" r="14" fill="#ef4444" opacity="0.3" className="animate-ping" />
                          <circle cx="195" cy="90" r="6" fill="#ef4444" stroke="#ffffff" strokeWidth="1.5" />
                        </svg>
                      )}

                      {selectedDisruption.id === 'DISR-004' && (
                        <svg className="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 400 176">
                          <circle cx="170" cy="85" r="28" fill="none" stroke="#f43f5e" strokeWidth="1.5" strokeDasharray="3 3" className="animate-spin" />
                          <circle cx="170" cy="85" r="18" fill="#f43f5e" opacity="0.25" className="animate-ping" />
                          <circle cx="170" cy="85" r="5" fill="#f43f5e" stroke="#ffffff" strokeWidth="1.5" />
                          {/* Drift Vector Arrow */}
                          <line x1="170" y1="85" x2="230" y2="105" stroke="#fbbf24" strokeWidth="2" strokeDasharray="4 2" />
                          <polygon points="235,107 225,100 227,110" fill="#fbbf24" />
                        </svg>
                      )}

                      {/* Current Disruption Status Badge */}
                      <div className={`absolute bottom-3 left-3 bg-[#0A1128]/95 border ${currentVisual.badgeBorder} px-2.5 py-1 rounded-md text-[10px] font-bold text-white shadow-lg flex items-center gap-1.5 backdrop-blur-xs`}>
                        <span className={`w-2 h-2 rounded-full ${currentVisual.pulseColor} animate-pulse inline-block`} />
                        <span>{currentVisual.badgeText}</span>
                      </div>

                      {/* Radar Legend in Top Right */}
                      <div className="absolute top-2 right-2 flex items-center gap-2 text-[9px] font-mono text-slate-200 bg-slate-950/85 px-2.5 py-1 rounded-md border border-white/15 backdrop-blur-xs shadow-md">
                        {currentVisual.legend.map((leg, i) => (
                          <span key={i} className="flex items-center gap-1">
                            <span className={`w-1.5 h-1.5 rounded-full ${leg.color} inline-block`} />
                            <span>{leg.label}</span>
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Dynamic Impact Summary Alert Box */}
                    <div className={`mt-3.5 p-3.5 rounded-xl border text-xs ${currentVisual.impactBoxClass}`}>
                      <div className={`flex items-center gap-2 font-bold mb-1 ${currentVisual.impactTitleClass}`}>
                        <AlertTriangle size={15} />
                        <span>{currentVisual.impactTitle}</span>
                      </div>
                      <p className={`leading-relaxed text-[11px] ${currentVisual.impactTextClass}`}>
                        {currentVisual.impactSummary}
                      </p>
                    </div>
                  </>
                )
              })()}

            </div>

            {/* Bottom 3 Action Buttons */}
            <div className="pt-2 space-y-2">
              <div className="grid grid-cols-2 gap-2">
                <button 
                  onClick={() => {
                    soundEngine.playClick()
                    onNavigateToShipments && onNavigateToShipments()
                  }}
                  className="w-full py-2 px-3 rounded-xl text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 shadow-xs flex items-center justify-center gap-1.5 transition-colors"
                >
                  <span>View Affected Shipments</span>
                  <ArrowRight size={14} />
                </button>

                <button 
                  onClick={() => {
                    soundEngine.playClick()
                    alert('Showing alternative routes calculated by watsonx.ai routing engine.')
                  }}
                  className="w-full py-2 px-3 rounded-xl text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50 border border-slate-200 shadow-xs flex items-center justify-center gap-1.5 transition-colors"
                >
                  <Route size={14} className="text-blue-600" />
                  <span>Show Alternative Routes</span>
                </button>
              </div>

              <button 
                onClick={() => {
                  soundEngine.playChime()
                  setAiInsightOpen(!aiInsightOpen)
                }}
                className="w-full py-2 px-3 rounded-xl text-xs font-semibold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 flex items-center justify-center gap-1.5 transition-colors"
              >
                <Sparkles size={14} className="text-indigo-600" />
                <span>Get AI Insights (watsonx.ai)</span>
              </button>

              {aiInsightOpen && (
                <div className="p-3 bg-indigo-900 text-white rounded-xl text-xs space-y-1.5 animate-fadeIn">
                  <div className="font-bold text-cyan-300 flex items-center gap-1.5">
                    <Sparkles size={13} />
                    <span>watsonx Autonomous Advisory</span>
                  </div>
                  <p className="text-slate-200 text-[11px] leading-relaxed">
                    Vessels approaching Arabian Sea should adjust headings southward via Colombo (+1.5d, +$3,200 fuel) to bypass cyclone gale radius and safeguard reefer integrity.
                  </p>
                </div>
              )}
            </div>

          </div>
        )}

      </div>

      {/* ── Bottom Analytics Row (Regions, Types, Estimated Impact) ── */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        
        {/* Most Affected Regions */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <h4 className="text-xs font-bold text-slate-800 mb-3 font-head">Most Affected Regions</h4>
          <div className="space-y-2.5 text-xs">
            {[
              { region: 'Asia', count: 2, color: 'bg-rose-500' },
              { region: 'Europe', count: 1, color: 'bg-orange-500' },
              { region: 'North America', count: 1, color: 'bg-amber-400' },
              { region: 'Indian Ocean', count: 1, color: 'bg-blue-500' }
            ].map(r => (
              <div key={r.region} className="flex items-center justify-between gap-3">
                <span className="text-slate-500 w-24 text-[11px] font-medium">{r.region}</span>
                <div className="flex-1 bg-slate-100 h-2 rounded-full overflow-hidden">
                  <div className={`h-full ${r.color} rounded-full`} style={{ width: `${(r.count / 2) * 100}%` }} />
                </div>
                <span className="font-mono font-bold text-slate-800 text-[11px]">{r.count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Disruption Types Donut Breakdown */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <h4 className="text-xs font-bold text-slate-800 mb-3 font-head">Disruption Types</h4>
          <div className="flex items-center justify-between gap-4">
            <div className="relative w-20 h-20 flex-shrink-0 flex items-center justify-center">
              {/* Circular SVG Donut */}
              <svg viewBox="0 0 36 36" className="w-full h-full -rotate-90">
                <circle cx="18" cy="18" r="14" fill="none" stroke="#f1f5f9" strokeWidth="4" />
                <circle cx="18" cy="18" r="14" fill="none" stroke="#f43f5e" strokeWidth="4" strokeDasharray="20 80" strokeDashoffset="0" />
                <circle cx="18" cy="18" r="14" fill="none" stroke="#3b82f6" strokeWidth="4" strokeDasharray="20 80" strokeDashoffset="-20" />
                <circle cx="18" cy="18" r="14" fill="none" stroke="#f97316" strokeWidth="4" strokeDasharray="20 80" strokeDashoffset="-40" />
                <circle cx="18" cy="18" r="14" fill="none" stroke="#a855f7" strokeWidth="4" strokeDasharray="20 80" strokeDashoffset="-60" />
                <circle cx="18" cy="18" r="14" fill="none" stroke="#10b981" strokeWidth="4" strokeDasharray="20 80" strokeDashoffset="-80" />
              </svg>
              <div className="absolute text-center">
                <span className="text-base font-bold font-head text-slate-900 leading-none">5</span>
                <span className="block text-[8px] text-slate-400 font-mono">Total</span>
              </div>
            </div>

            <div className="space-y-1 text-[11px] flex-1">
              {[
                { name: 'Port Congestion', count: 1, color: 'bg-rose-500' },
                { name: 'Weather', count: 1, color: 'bg-blue-500' },
                { name: 'Strike', count: 1, color: 'bg-orange-500' },
                { name: 'Vessel Failure', count: 1, color: 'bg-purple-500' },
                { name: 'Customs Delay', count: 1, color: 'bg-emerald-500' }
              ].map(t => (
                <div key={t.name} className="flex items-center justify-between text-slate-600">
                  <div className="flex items-center gap-1.5">
                    <span className={`w-2 h-2 rounded-full ${t.color}`} />
                    <span className="truncate max-w-[100px]">{t.name}</span>
                  </div>
                  <span className="font-mono font-bold text-slate-800">{t.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Estimated Impact */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <h4 className="text-xs font-bold text-slate-800 mb-2 font-head">Estimated Impact</h4>
          <div className="grid grid-cols-2 gap-3 py-1">
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
              <div className="flex items-center gap-1.5 text-slate-500 mb-1">
                <Clock size={14} />
                <span className="text-lg font-bold font-head text-slate-900">32</span>
              </div>
              <div className="text-[10px] font-bold text-slate-700 uppercase">Total Delay Days</div>
              <div className="text-[10px] font-bold text-rose-600 mt-0.5">↑ 68%</div>
              <div className="text-[9px] text-slate-400 leading-tight mt-0.5">Across all affected shipments</div>
            </div>

            <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
              <div className="flex items-center gap-1.5 text-slate-500 mb-1">
                <DollarSign size={14} className="text-emerald-600" />
                <span className="text-lg font-bold font-head text-slate-900">$57,500</span>
              </div>
              <div className="text-[10px] font-bold text-slate-700 uppercase">Add. Cost (USD)</div>
              <div className="text-[10px] font-bold text-emerald-600 mt-0.5">↑ 42%</div>
              <div className="text-[9px] text-slate-400 leading-tight mt-0.5">Estimated total impact</div>
            </div>
          </div>
        </div>

      </div>

    </div>
  )
}
