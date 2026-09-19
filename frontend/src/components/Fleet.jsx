import { useEffect, useState } from 'react'
import { apiFetch } from '../api'
import { 
  Ship, 
  CheckCircle2, 
  Wrench, 
  Box, 
  Thermometer, 
  BarChart2, 
  Search, 
  Filter as FilterIcon, 
  MoreHorizontal, 
  X, 
  AlertTriangle, 
  ArrowRight, 
  MapPin, 
  ChevronDown,
  Navigation,
  FileCheck2,
  Zap,
  Calendar,
  Layers,
  Gauge
} from 'lucide-react'
import { soundEngine } from './effects'

export default function Fleet() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedId, setSelectedId] = useState('V-005')
  const [searchQuery, setSearchQuery] = useState('')
  const [activeDossierTab, setActiveDossierTab] = useState('Overview')
  const [actionNotice, setActionNotice] = useState(null)

  // Filter dropdown states
  const [statusFilter, setStatusFilter] = useState('All')
  const [typeFilter, setTypeFilter] = useState('All')
  const [carrierFilter, setCarrierFilter] = useState('All')
  const [locationFilter, setLocationFilter] = useState('All')

  useEffect(() => {
    apiFetch('/api/fleet')
      .then(d => { setData(d); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  const vesselList = [
    {
      id: 'V-001',
      name: 'MV Pacific Pioneer',
      type: 'Container',
      carrier: 'CMA CGM',
      location: 'Detroit (USDET)',
      portCode: 'USDET',
      flag: '🇺🇸',
      status: 'Available',
      capacity: '8,500',
      loadPct: 61,
      reeferSlots: 350,
      currentLoad: '5,185 TEU (61%)',
      route: 'ROUTE-US-EU-01 (Trans-Atlantic Direct)',
      speed: '19.4 knots',
      eta: '28 Jul 2025 14:00',
      engineStatus: 'Nominal — 100% Power Output',
      nextSurvey: '14 Nov 2026',
      supportedCargo: ['General Cargo', 'Automotive Parts', 'Machinery'],
      image: '/images/vessel_eastern_star.jpg'
    },
    {
      id: 'V-002',
      name: 'MV Orient Express',
      type: 'Container',
      carrier: 'MaerskLine',
      location: 'Shanghai (CNSHA)',
      portCode: 'CNSHA',
      flag: '🇨🇳',
      status: 'Available',
      capacity: '14,000',
      loadPct: 94,
      reeferSlots: 600,
      currentLoad: '13,160 TEU (94%)',
      route: 'ROUTE-TRANS-PAC-01 (Trans-Pacific Strategic)',
      speed: '20.2 knots',
      eta: '31 Jul 2025 08:30',
      engineStatus: 'Nominal — 98% Power Output',
      nextSurvey: '02 Feb 2027',
      supportedCargo: ['Electronics', 'Consumer Goods', 'General Cargo'],
      image: '/images/vessel_eastern_star.jpg'
    },
    {
      id: 'V-003',
      name: 'MV Nordic Frost',
      type: 'Reefer',
      carrier: 'MSC',
      location: 'Hamburg (DEHAM)',
      portCode: 'DEHAM',
      flag: '🇩🇪',
      status: 'Available',
      capacity: '3,200',
      loadPct: 91,
      reeferSlots: 550,
      currentLoad: '2,912 TEU (91%)',
      route: 'ROUTE-EU-INDIA-01 (Cape of Good Hope Divergence)',
      speed: '18.8 knots',
      eta: '26 Jul 2025 18:00',
      engineStatus: 'Nominal — Ultra-Deep Freeze Active (-25°C)',
      nextSurvey: '19 Sep 2026',
      supportedCargo: ['Pharmaceuticals', 'Vaccines', 'Perishable Food'],
      image: '/images/vessel_eastern_star.jpg'
    },
    {
      id: 'V-004',
      name: 'MV Amazon Star',
      type: 'Container',
      carrier: 'Hapag-Lloyd',
      location: 'Santos (BRSSO)',
      portCode: 'BRSSO',
      flag: '🇧🇷',
      status: 'Available',
      capacity: '6,000',
      loadPct: 97,
      reeferSlots: 400,
      currentLoad: '5,820 TEU (97%)',
      route: 'ROUTE-LATAM-EU-01 (South Atlantic Corridor)',
      speed: '17.5 knots',
      eta: '30 Jul 2025 10:00',
      engineStatus: 'Nominal — Active Reefer Telemetry',
      nextSurvey: '08 Dec 2026',
      supportedCargo: ['Fresh Produce', 'Coffee', 'Agricultural Goods'],
      image: '/images/vessel_eastern_star.jpg'
    },
    {
      id: 'V-005',
      name: 'MV Eastern Star',
      type: 'Container',
      carrier: 'ONE (Ocean Network Express)',
      location: 'Indian Ocean (Adrift)',
      portCode: 'ADRIFT',
      flag: '🇯🇵',
      status: 'Unavailable',
      capacity: '7,500',
      loadPct: 100,
      reeferSlots: 200,
      currentLoad: '7,500 TEU (100%)',
      route: 'ROUTE-SOUTH-ASIA-US-01 (Stranded / Transshipment Req.)',
      speed: '0.0 knots (Drifting at 1.2 kts)',
      eta: 'Delayed (+14 Days)',
      engineStatus: 'CRITICAL — Main propulsion piston fracture. Salvage tug en route.',
      nextSurvey: 'Immediate Emergency Drydock Required',
      supportedCargo: ['Textiles', 'Garments', 'Raw Materials'],
      incident: 'Main engine failure in open water. Vessel adrift awaiting commercial salvage tug. Estimated resolution: 01 Aug 2025 (14 days delay)',
      image: '/images/vessel_eastern_star.jpg'
    },
    {
      id: 'V-006',
      name: 'MV Southern Cross',
      type: 'Container',
      carrier: 'Evergreen',
      location: 'Osaka (JPOSA)',
      portCode: 'JPOSA',
      flag: '🇯🇵',
      status: 'Available',
      capacity: '5,500',
      loadPct: 22,
      reeferSlots: 250,
      currentLoad: '1,210 TEU (22%)',
      route: 'Standby / Trans-Pacific Feeder Corridor',
      speed: '21.0 knots',
      eta: 'Immediate Ready for Deployment (4,290 TEU Free)',
      engineStatus: 'Excellent — Dual-Fuel LNG Engine Ready',
      nextSurvey: '05 May 2027',
      supportedCargo: ['High-Priority Electronics', 'General Cargo', 'Automotive'],
      image: '/images/vessel_eastern_star.jpg'
    },
    {
      id: 'V-007',
      name: 'MV Rhine Express',
      type: 'Container',
      carrier: 'Hapag-Lloyd',
      location: 'Antwerp (BEANR)',
      portCode: 'BEANR',
      flag: '🇧🇪',
      status: 'Available',
      capacity: '9,000',
      loadPct: 50,
      reeferSlots: 450,
      currentLoad: '4,500 TEU (50%)',
      route: 'Contingency Backup (Antwerp-Rotterdam Shuttle)',
      speed: '19.2 knots',
      eta: 'Available (4,500 TEU Free, 225 Reefer Free)',
      engineStatus: 'Nominal — Fully Certified for Dangerous & Reefer Goods',
      nextSurvey: '12 Jan 2027',
      supportedCargo: ['Chemicals', 'Cold-Chain Foods', 'Pharmaceuticals'],
      image: '/images/vessel_eastern_star.jpg'
    }
  ]

  // Fully calibrated multi-factor filter logic
  const filtered = vesselList.filter(v => {
    if (statusFilter !== 'All' && v.status !== statusFilter) return false
    if (typeFilter !== 'All' && v.type !== typeFilter) return false
    if (carrierFilter !== 'All' && !v.carrier.toLowerCase().includes(carrierFilter.toLowerCase())) return false
    if (locationFilter !== 'All' && !v.location.toLowerCase().includes(locationFilter.toLowerCase())) return false
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim()
      const match = v.id.toLowerCase().includes(q) ||
                    v.name.toLowerCase().includes(q) ||
                    v.carrier.toLowerCase().includes(q) ||
                    v.location.toLowerCase().includes(q)
      if (!match) return false
    }
    return true
  })

  const selectedVessel = vesselList.find(v => v.id === selectedId) || vesselList[4]

  const handleAssignContingency = (vessel) => {
    soundEngine.playSuccess()
    setActionNotice(`Vessel ${vessel.name} (${vessel.id}) successfully assigned as active contingency asset for trade lane redirection.`)
    setTimeout(() => setActionNotice(null), 7000)
  }

  const handleExportDossier = (vessel) => {
    soundEngine.playClick()
    setActionNotice(`Generated SOLAS Chapter V technical compliance dossier for ${vessel.name}. Ready for download.`)
    setTimeout(() => setActionNotice(null), 6000)
  }

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* ── Title Banner ───────────────────────────────────────────── */}
      <div className="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-blue-500 text-base">✦</span>
            <h1 className="text-2xl font-black font-head tracking-tight text-slate-900">
              Fleet Capacity & Asset Allocation
            </h1>
          </div>
          <p className="text-xs text-slate-500 mt-1 font-sans">
            Real-time vessel telematics, load distribution, and deterministic contingency redeployment.
          </p>
        </div>

        {/* Hero Photo Banner Card */}
        <div className="relative rounded-2xl overflow-hidden shadow-xs border border-slate-200/80 w-full lg:w-[480px] h-[78px] flex-shrink-0 group">
          <img 
            src="/images/fleet_hero.jpg" 
            alt="Commercial Fleet"
            className="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-700"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-sky-950/80 via-blue-900/40 to-transparent flex items-center px-6">
            <div>
              <p className="text-white font-serif italic text-base md:text-lg tracking-wide drop-shadow-md">
                “Optimized Fleets. Zero Idling.”
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Action Notification Toast */}
      {actionNotice && (
        <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs font-medium flex items-center gap-3 animate-fade-in shadow-xs">
          <CheckCircle2 size={16} className="text-emerald-600 flex-shrink-0" />
          <span className="flex-1">{actionNotice}</span>
        </div>
      )}

      {/* ── 4 Top KPI Cards ────────────────────────────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block font-head">Total Vessels</span>
            <div className="text-2xl font-black font-head text-slate-900 mt-0.5">7</div>
            <span className="text-[11px] font-bold text-emerald-600 font-mono">100% Monitored</span>
          </div>
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
            <Ship size={20} />
          </div>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block font-head">Available for Reroute</span>
            <div className="text-2xl font-black font-head text-slate-900 mt-0.5">6</div>
            <span className="text-[11px] font-bold text-emerald-600 font-mono">13,700 TEU Idle Space</span>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
            <CheckCircle2 size={20} />
          </div>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block font-head">Disabled / Adrift</span>
            <div className="text-2xl font-black font-head text-slate-900 mt-0.5">1</div>
            <span className="text-[11px] font-bold text-rose-600 font-mono">V-005 Engine Failure</span>
          </div>
          <div className="w-10 h-10 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center font-bold">
            <Wrench size={20} />
          </div>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block font-head">Fleet Utilisation</span>
            <div className="text-2xl font-black font-head text-slate-900 mt-0.5">57.1%</div>
            <span className="text-[11px] font-bold text-blue-600 font-mono">2,800 Reefer Slots</span>
          </div>
          <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold">
            <BarChart2 size={20} />
          </div>
        </div>
      </div>

      {/* ── Filter Bar ─────────────────────────────────────────────── */}
      <div className="bg-white p-3.5 rounded-2xl border border-slate-200 shadow-xs flex flex-wrap items-center gap-3">
        {/* Search */}
        <div className="relative flex-1 min-w-[200px]">
          <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            placeholder="Search by vessel ID, name, carrier, port..."
            className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
          />
        </div>

        {/* Status Dropdown */}
        <div className="relative">
          <select
            value={statusFilter}
            onChange={e => setStatusFilter(e.target.value)}
            className="appearance-none bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 pr-7 text-xs font-medium text-slate-700 focus:outline-none cursor-pointer"
          >
            <option value="All">Status: All</option>
            <option value="Available">Available</option>
            <option value="Unavailable">Unavailable</option>
          </select>
          <ChevronDown size={14} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
        </div>

        {/* Vessel Type Dropdown */}
        <div className="relative">
          <select
            value={typeFilter}
            onChange={e => setTypeFilter(e.target.value)}
            className="appearance-none bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 pr-7 text-xs font-medium text-slate-700 focus:outline-none cursor-pointer"
          >
            <option value="All">Type: All</option>
            <option value="Container">Container</option>
            <option value="Reefer">Reefer</option>
          </select>
          <ChevronDown size={14} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
        </div>

        {/* Carrier Dropdown */}
        <div className="relative">
          <select
            value={carrierFilter}
            onChange={e => setCarrierFilter(e.target.value)}
            className="appearance-none bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 pr-7 text-xs font-medium text-slate-700 focus:outline-none cursor-pointer"
          >
            <option value="All">Carrier: All</option>
            <option value="MaerskLine">MaerskLine</option>
            <option value="CMA CGM">CMA CGM</option>
            <option value="Hapag-Lloyd">Hapag-Lloyd</option>
            <option value="MSC">MSC</option>
            <option value="ONE">ONE</option>
            <option value="Evergreen">Evergreen</option>
          </select>
          <ChevronDown size={14} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
        </div>

        {/* Location Dropdown */}
        <div className="relative">
          <select
            value={locationFilter}
            onChange={e => setLocationFilter(e.target.value)}
            className="appearance-none bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 pr-7 text-xs font-medium text-slate-700 focus:outline-none cursor-pointer"
          >
            <option value="All">Location: All</option>
            <option value="Detroit">Detroit</option>
            <option value="Shanghai">Shanghai</option>
            <option value="Hamburg">Hamburg</option>
            <option value="Santos">Santos</option>
            <option value="Indian Ocean">Indian Ocean</option>
            <option value="Osaka">Osaka</option>
            <option value="Antwerp">Antwerp</option>
          </select>
          <ChevronDown size={14} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
        </div>

        {/* Clear Filters */}
        <button
          onClick={() => {
            soundEngine.playClick()
            setStatusFilter('All')
            setTypeFilter('All')
            setCarrierFilter('All')
            setLocationFilter('All')
            setSearchQuery('')
          }}
          className="text-xs font-semibold text-slate-500 hover:text-slate-800 px-2 transition-colors"
        >
          Clear
        </button>
      </div>

      {/* ── Main Split Section: Table (Left) & Vessel Dossier (Right) ─ */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* Fleet List Table */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden flex flex-col justify-between">
          <div>
            <div className="p-4 border-b border-slate-100 flex items-center justify-between">
              <h2 className="text-sm font-bold font-head text-slate-900">
                Fleet Registry ({filtered.length})
              </h2>
              <span className="text-xs font-medium text-slate-400 font-mono">
                Matching {filtered.length} of {vesselList.length} vessels
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-50/70 border-b border-slate-200/80 text-slate-500 font-semibold uppercase tracking-wider text-[10px]">
                    <th className="p-3 pl-4">Vessel ID</th>
                    <th className="p-3">Vessel Name</th>
                    <th className="p-3">Type</th>
                    <th className="p-3">Carrier</th>
                    <th className="p-3">Current Location</th>
                    <th className="p-3">Status</th>
                    <th className="p-3">Capacity</th>
                    <th className="p-3 pr-4">Utilization</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filtered.length === 0 ? (
                    <tr>
                      <td colSpan={8} className="p-8 text-center text-slate-400 text-xs">
                        No vessels match the selected filter criteria.
                      </td>
                    </tr>
                  ) : (
                    filtered.map(v => {
                      const isSelected = selectedId === v.id
                      const isAdrift = v.id === 'V-005'
                      return (
                        <tr
                          key={v.id}
                          onClick={() => {
                            soundEngine.playClick()
                            setSelectedId(v.id)
                          }}
                          className={`cursor-pointer transition-colors ${
                            isSelected 
                              ? 'bg-blue-50/70 font-medium text-blue-900' 
                              : 'hover:bg-slate-50 text-slate-700'
                          }`}
                        >
                          <td className="p-3 pl-4 font-mono font-bold text-blue-600">
                            {v.id}
                          </td>
                          <td className="p-3 font-semibold text-slate-900">
                            {v.name}
                          </td>
                          <td className="p-3">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              v.type === 'Reefer' ? 'bg-purple-50 text-purple-700 border border-purple-200' : 'bg-slate-100 text-slate-700'
                            }`}>
                              {v.type}
                            </span>
                          </td>
                          <td className="p-3 text-slate-600 truncate max-w-[110px]">
                            {v.carrier}
                          </td>
                          <td className="p-3">
                            <span className="flex items-center gap-1">
                              <span>{v.flag}</span>
                              <span className="truncate max-w-[120px]">{v.location}</span>
                            </span>
                          </td>
                          <td className="p-3">
                            {v.status === 'Available' ? (
                              <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                                Available
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-200">
                                <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse" />
                                Unavailable
                              </span>
                            )}
                          </td>
                          <td className="p-3 font-mono font-bold text-slate-800">
                            {v.capacity} TEU
                          </td>
                          <td className="p-3 pr-4">
                            <div className="flex items-center gap-2">
                              <span className="font-mono font-bold text-[11px] w-8">{v.loadPct}%</span>
                              <div className="w-14 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                                <div
                                  className={`h-full rounded-full ${v.loadPct >= 95 ? 'bg-rose-500' : v.loadPct >= 80 ? 'bg-blue-600' : 'bg-blue-400'}`}
                                  style={{ width: `${v.loadPct}%` }}
                                />
                              </div>
                            </div>
                          </td>
                        </tr>
                      )
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right Side: Deep Vessel Dossier */}
        {selectedVessel && (
          <div className="lg:col-span-5 bg-white rounded-2xl border border-slate-200 shadow-xs p-5 flex flex-col justify-between space-y-4">
            
            {/* Header */}
            <div>
              <div className="flex items-center justify-between pb-2">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-slate-900">{selectedVessel.id}</span>
                  {selectedVessel.status === 'Available' ? (
                    <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">Available</span>
                  ) : (
                    <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-rose-50 text-rose-700 border border-rose-200">Unavailable</span>
                  )}
                </div>
                <span className="font-mono text-xs text-slate-400">{selectedVessel.flag} {selectedVessel.portCode}</span>
              </div>

              <h3 className="text-lg font-head font-extrabold text-slate-900">
                {selectedVessel.name}
              </h3>

              {/* Subtabs: Overview, Route & Schedule, Cargo, Maintenance, History */}
              <div className="flex items-center gap-3 mt-3 border-b border-slate-100 text-xs font-semibold overflow-x-auto pb-1">
                {['Overview', 'Route & Schedule', 'Cargo', 'Maintenance', 'History'].map(tab => (
                  <button
                    key={tab}
                    onClick={() => {
                      soundEngine.playClick()
                      setActiveDossierTab(tab)
                    }}
                    className={`pb-2 transition-colors relative flex-shrink-0 ${
                      activeDossierTab === tab 
                        ? 'text-blue-600 border-b-2 border-blue-600' 
                        : 'text-slate-400 hover:text-slate-600'
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              {/* Dynamic Dossier Content by Active Tab */}
              <div className="mt-3.5">
                
                {/* 1. Overview Tab */}
                {activeDossierTab === 'Overview' && (
                  <div className="space-y-3 animate-fade-in">
                    <div className="grid grid-cols-1 sm:grid-cols-12 gap-3.5">
                      <div className="sm:col-span-5 rounded-xl overflow-hidden border border-slate-200 shadow-xs relative aspect-[4/5] sm:aspect-auto">
                        <img
                          src={selectedVessel.image}
                          alt={selectedVessel.name}
                          className="w-full h-full object-cover"
                        />
                      </div>

                      <div className="sm:col-span-7 space-y-1.5 text-xs">
                        <div className="flex justify-between py-0.5 border-b border-slate-100">
                          <span className="text-slate-400">Carrier</span>
                          <span className="font-semibold text-slate-800">{selectedVessel.carrier}</span>
                        </div>
                        <div className="flex justify-between py-0.5 border-b border-slate-100">
                          <span className="text-slate-400">Vessel Type</span>
                          <span className="text-slate-800">{selectedVessel.type} Vessel</span>
                        </div>
                        <div className="flex justify-between py-0.5 border-b border-slate-100">
                          <span className="text-slate-400">Total Capacity</span>
                          <span className="font-mono font-bold text-slate-800">{selectedVessel.capacity} TEU</span>
                        </div>
                        <div className="flex justify-between py-0.5 border-b border-slate-100">
                          <span className="text-slate-400">Current Load</span>
                          <span className="font-mono font-bold text-slate-800">{selectedVessel.currentLoad}</span>
                        </div>
                        <div className="flex justify-between py-0.5 border-b border-slate-100">
                          <span className="text-slate-400">Reefer Slots</span>
                          <span className="font-mono text-slate-800">{selectedVessel.reeferSlots} slots</span>
                        </div>
                        <div className="flex justify-between py-0.5 border-b border-slate-100">
                          <span className="text-slate-400">Current Location</span>
                          <span className="text-slate-800 font-semibold">{selectedVessel.location}</span>
                        </div>
                      </div>
                    </div>

                    {selectedVessel.incident && (
                      <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-xs">
                        <div className="flex items-center gap-1.5 text-rose-700 font-bold mb-1">
                          <AlertTriangle size={15} />
                          <span>Incident Alert: Propulsion Breakdown</span>
                        </div>
                        <p className="text-rose-900 text-[11px] leading-relaxed">
                          {selectedVessel.incident}
                        </p>
                      </div>
                    )}
                  </div>
                )}

                {/* 2. Route & Schedule Tab */}
                {activeDossierTab === 'Route & Schedule' && (
                  <div className="space-y-2.5 text-xs animate-fade-in">
                    <div className="bg-slate-50 p-3 rounded-xl border border-slate-200/80 space-y-1.5">
                      <span className="text-slate-400 text-[10px] font-mono block">ASSIGNED TRADE CORRIDOR</span>
                      <div className="font-bold text-slate-900">{selectedVessel.route}</div>
                    </div>

                    <div className="grid grid-cols-2 gap-2">
                      <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200/60">
                        <span className="text-slate-400 text-[10px] block">CRUISING SPEED</span>
                        <span className="font-mono font-bold text-slate-800">{selectedVessel.speed}</span>
                      </div>
                      <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200/60">
                        <span className="text-slate-400 text-[10px] block">ESTIMATED ARRIVAL</span>
                        <span className="font-mono font-bold text-slate-800">{selectedVessel.eta}</span>
                      </div>
                    </div>

                    <div className="p-3 bg-white rounded-xl border border-slate-200 space-y-1.5">
                      <span className="text-[11px] font-bold text-slate-800 block">Voyage Waypoint Telemetry:</span>
                      <div className="flex items-center justify-between text-[11px] text-slate-600">
                        <span>• Departure: <b>{selectedVessel.location}</b></span>
                        <span className="text-emerald-600 font-mono">On Schedule</span>
                      </div>
                      <div className="flex items-center justify-between text-[11px] text-slate-600">
                        <span>• Next Chokepoint: <b>Clearance Zone Alpha</b></span>
                        <span className="text-blue-600 font-mono">Monitored</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* 3. Cargo Tab */}
                {activeDossierTab === 'Cargo' && (
                  <div className="space-y-2.5 text-xs animate-fade-in">
                    <div className="grid grid-cols-2 gap-2">
                      <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200/60">
                        <span className="text-slate-400 text-[10px] block">LOADED TEU</span>
                        <span className="font-mono font-bold text-slate-900">{selectedVessel.currentLoad}</span>
                      </div>
                      <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200/60">
                        <span className="text-slate-400 text-[10px] block">REEFER ACTIVE SLOTS</span>
                        <span className="font-mono font-bold text-purple-700">{selectedVessel.reeferSlots} Units</span>
                      </div>
                    </div>

                    <div className="p-3 bg-white rounded-xl border border-slate-200 space-y-2">
                      <span className="text-[11px] font-bold text-slate-800 block">Certified Cargo Specifications:</span>
                      <div className="flex flex-wrap gap-1.5">
                        {selectedVessel.supportedCargo.map((c, i) => (
                          <span key={i} className="px-2 py-0.5 rounded-md bg-blue-50 text-blue-700 text-[11px] font-medium border border-blue-200">
                            {c}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* 4. Maintenance Tab */}
                {activeDossierTab === 'Maintenance' && (
                  <div className="space-y-2.5 text-xs animate-fade-in">
                    <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 space-y-1.5">
                      <span className="text-slate-400 text-[10px] font-mono block">PROPULSION & MACHINERY STATE</span>
                      <div className={`font-bold ${selectedVessel.id === 'V-005' ? 'text-rose-600' : 'text-slate-900'}`}>
                        {selectedVessel.engineStatus}
                      </div>
                    </div>

                    <div className="bg-white p-3 rounded-xl border border-slate-200 space-y-1">
                      <div className="flex justify-between">
                        <span className="text-slate-500">Next Class Survey:</span>
                        <span className="font-mono font-bold text-slate-800">{selectedVessel.nextSurvey}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-500">Hull Integrity Index:</span>
                        <span className="font-mono font-bold text-emerald-600">{selectedVessel.id === 'V-005' ? '91%' : '98.5%'}</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* 5. History Tab */}
                {activeDossierTab === 'History' && (
                  <div className="space-y-2 text-xs animate-fade-in">
                    <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200/60 flex justify-between">
                      <span>Total Completed Voyages:</span>
                      <b className="font-mono text-slate-900">42 Voyages</b>
                    </div>
                    <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200/60 flex justify-between">
                      <span>Historical On-Time Reliability:</span>
                      <b className="font-mono text-emerald-600">97.8%</b>
                    </div>
                    <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200/60 flex justify-between">
                      <span>Safety Excursion Incident Count:</span>
                      <b className="font-mono text-slate-800">{selectedVessel.id === 'V-005' ? '1 (Active)' : '0'}</b>
                    </div>
                  </div>
                )}

              </div>

            </div>

            {/* Practical Operational Action Buttons */}
            <div className="pt-2 grid grid-cols-2 gap-2">
              <button
                onClick={() => handleAssignContingency(selectedVessel)}
                disabled={selectedVessel.status !== 'Available'}
                className="py-2.5 px-3 rounded-xl text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 shadow-xs flex items-center justify-center gap-1.5 transition-colors"
              >
                <Zap size={14} />
                <span>Assign as Contingency</span>
              </button>

              <button
                onClick={() => handleExportDossier(selectedVessel)}
                className="py-2.5 px-3 rounded-xl text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50 border border-slate-200 shadow-xs flex items-center justify-center gap-1.5 transition-colors"
              >
                <FileCheck2 size={14} className="text-blue-600" />
                <span>Export Vessel Dossier</span>
              </button>
            </div>

          </div>
        )}

      </div>

    </div>
  )
}
