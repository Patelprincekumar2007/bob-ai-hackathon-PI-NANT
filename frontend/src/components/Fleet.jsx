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
  ChevronDown 
} from 'lucide-react'
import { soundEngine } from './effects'

export default function Fleet() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedId, setSelectedId] = useState('V-005')
  const [searchQuery, setSearchQuery] = useState('')
  const [activeTab, setActiveTab] = useState('Vessels')
  const [activeDossierTab, setActiveDossierTab] = useState('Overview')

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
      location: 'Detroit',
      portCode: 'USDET',
      flag: '🇺🇸',
      status: 'Available',
      capacity: '8,500',
      loadPct: 61,
      reeferSlots: 350,
      currentLoad: '5,185 TEU (61%)',
    },
    {
      id: 'V-002',
      name: 'MV Orient Express',
      type: 'Container',
      carrier: 'MaerskLine',
      location: 'Shanghai',
      portCode: 'CNSHA',
      flag: '🇨🇳',
      status: 'Available',
      capacity: '14,000',
      loadPct: 94,
      reeferSlots: 600,
      currentLoad: '13,160 TEU (94%)',
    },
    {
      id: 'V-003',
      name: 'MV Nordic Frost',
      type: 'Reefer',
      carrier: 'MSC',
      location: 'Hamburg',
      portCode: 'DEHAM',
      flag: '🇩🇪',
      status: 'Available',
      capacity: '3,200',
      loadPct: 91,
      reeferSlots: 550,
      currentLoad: '2,912 TEU (91%)',
    },
    {
      id: 'V-004',
      name: 'MV Amazon Star',
      type: 'Container',
      carrier: 'Hapag-Lloyd',
      location: 'Santos',
      portCode: 'BRSSO',
      flag: '🇧🇷',
      status: 'Available',
      capacity: '6,000',
      loadPct: 97,
      reeferSlots: 400,
      currentLoad: '5,820 TEU (97%)',
    },
    {
      id: 'V-005',
      name: 'MV Eastern Star',
      type: 'Container',
      carrier: 'ONE (Ocean Network Express)',
      location: 'Indian Ocean (adrift)',
      portCode: 'ADRIFT',
      flag: '🇯🇵',
      status: 'Unavailable',
      capacity: '7,500',
      loadPct: 100,
      reeferSlots: 200,
      currentLoad: '7,500 TEU (100%)',
      incident: 'Main engine failure. Vessel adrift awaiting salvage tug. Estimated resolution: 01 Aug 2025 (14 days delay)'
    },
    {
      id: 'V-006',
      name: 'MV Southern Cross',
      type: 'Container',
      carrier: 'Evergreen',
      location: 'Osaka',
      portCode: 'JPOSA',
      flag: '🇯🇵',
      status: 'Available',
      capacity: '5,500',
      loadPct: 22,
      reeferSlots: 250,
      currentLoad: '1,210 TEU (22%)',
    },
    {
      id: 'V-007',
      name: 'MV Rhine Express',
      type: 'Container',
      carrier: 'Hapag-Lloyd',
      location: 'Antwerp',
      portCode: 'BEANR',
      flag: '🇧🇪',
      status: 'Available',
      capacity: '9,000',
      loadPct: 50,
      reeferSlots: 450,
      currentLoad: '4,500 TEU (50%)',
    }
  ]

  const filtered = vesselList.filter(v => {
    if (statusFilter !== 'All' && v.status !== statusFilter) return false
    if (typeFilter !== 'All' && v.type !== typeFilter) return false
    if (carrierFilter !== 'All' && !v.carrier.includes(carrierFilter)) return false
    if (searchQuery) {
      const q = searchQuery.toLowerCase()
      if (!v.id.toLowerCase().includes(q) && !v.name.toLowerCase().includes(q) && !v.carrier.toLowerCase().includes(q)) return false
    }
    return true
  })

  const selectedVessel = vesselList.find(v => v.id === selectedId) || vesselList[4]

  return (
    <div className="space-y-6">
      
      {/* ── Title Banner with Hero Card matching reference ────────── */}
      <div className="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-2xl bg-[#0A1128] text-white flex items-center justify-center shadow-sm flex-shrink-0">
            <Ship size={22} className="text-cyan-400" />
          </div>
          <div>
            <h1 className="text-2xl sm:text-3xl font-head font-extrabold text-slate-900 tracking-tight">
              Fleet Management
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 font-medium">
              Track vessels, capacity, availability and utilization across your network.
            </p>
          </div>
        </div>

        {/* Right Hero Container Banner */}
        <div className="relative rounded-2xl overflow-hidden shadow-sm border border-slate-200/80 min-w-[340px] max-w-lg h-20 flex items-center px-5">
          <img 
            src="/images/fleet_hero.jpg" 
            alt="Fleet Hero" 
            className="absolute inset-0 w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-slate-900/85 via-slate-900/60 to-transparent" />
          <div className="relative z-10">
            <p className="text-sm font-head font-bold italic text-white tracking-wide">
              "Efficient Fleets. Stronger Supply Chains."
            </p>
            <span className="text-[10px] font-mono text-cyan-300 font-medium">
              Global AIS Vessel Telemetry
            </span>
          </div>
        </div>
      </div>

      {/* ── 6 KPI Metric Cards across matching screenshot ─────────── */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
        
        {/* Total Vessels */}
        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
              <Ship size={18} />
            </div>
            <span className="text-xs font-bold font-mono text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
              ↑ 17%
            </span>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold font-head text-slate-900">7</div>
            <div className="text-xs font-bold text-slate-700 mt-0.5">Total Vessels</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Active in network</div>
          </div>
        </div>

        {/* Available */}
        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <div className="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <CheckCircle2 size={18} />
            </div>
            <span className="text-xs font-bold font-mono text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
              ↑ 20%
            </span>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold font-head text-slate-900">6</div>
            <div className="text-xs font-bold text-slate-700 mt-0.5">Available</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Ready for deployment</div>
          </div>
        </div>

        {/* Unavailable */}
        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <div className="w-9 h-9 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center">
              <Wrench size={18} />
            </div>
            <span className="text-xs font-bold font-mono text-rose-600 bg-rose-50 px-2 py-0.5 rounded-full border border-rose-200">
              ↓ 50%
            </span>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold font-head text-slate-900">1</div>
            <div className="text-xs font-bold text-slate-700 mt-0.5">Unavailable</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Under maintenance / incident</div>
          </div>
        </div>

        {/* Total Capacity */}
        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
              <Box size={18} />
            </div>
            <span className="text-xs font-bold font-mono text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
              ↑ 12%
            </span>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold font-head text-slate-900">13,700</div>
            <div className="text-xs font-bold text-slate-700 mt-0.5">Total Capacity (TEU)</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Available capacity</div>
          </div>
        </div>

        {/* Reefer Slots */}
        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <div className="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <Thermometer size={18} />
            </div>
            <span className="text-xs font-bold font-mono text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
              ↑ 8%
            </span>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold font-head text-slate-900">550</div>
            <div className="text-xs font-bold text-slate-700 mt-0.5">Reefer Slots</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Available for cold chain</div>
          </div>
        </div>

        {/* Fleet Utilization */}
        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
              <BarChart2 size={18} />
            </div>
            <span className="text-xs font-bold font-mono text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
              ↑ 6%
            </span>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold font-head text-slate-900">57.1%</div>
            <div className="text-xs font-bold text-slate-700 mt-0.5">Fleet Utilization</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Current load across fleet</div>
          </div>
        </div>

      </div>

      {/* ── Subtabs Bar ────────────────────────────────────────────── */}
      <div className="flex items-center gap-6 border-b border-slate-200 text-xs font-semibold">
        {['Vessels', 'Utilization', 'Route Schedule', 'Maintenance', 'Capacity Planning'].map(tab => (
          <button
            key={tab}
            onClick={() => {
              soundEngine.playClick()
              setActiveTab(tab)
            }}
            className={`pb-2.5 transition-colors relative ${
              activeTab === tab
                ? 'text-blue-600 border-b-2 border-blue-600 font-bold'
                : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* ── Filter Bar ─────────────────────────────────────────────── */}
      <div className="bg-white p-3 rounded-2xl border border-slate-200 shadow-xs flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[220px]">
          <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            placeholder="Search by vessel ID, name, carrier..."
            className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
          />
        </div>

        {/* Status */}
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

        {/* Vessel Type */}
        <div className="relative">
          <select
            value={typeFilter}
            onChange={e => setTypeFilter(e.target.value)}
            className="appearance-none bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 pr-7 text-xs font-medium text-slate-700 focus:outline-none cursor-pointer"
          >
            <option value="All">Vessel Type: All</option>
            <option value="Container">Container</option>
            <option value="Reefer">Reefer</option>
          </select>
          <ChevronDown size={14} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
        </div>

        {/* Carrier */}
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

        {/* Current Location */}
        <div className="relative">
          <select
            value={locationFilter}
            onChange={e => setLocationFilter(e.target.value)}
            className="appearance-none bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 pr-7 text-xs font-medium text-slate-700 focus:outline-none cursor-pointer"
          >
            <option value="All">Current Location: All</option>
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

        <button
          onClick={() => {
            soundEngine.playClick()
            setStatusFilter('All')
            setTypeFilter('All')
            setCarrierFilter('All')
            setLocationFilter('All')
            setSearchQuery('')
          }}
          className="text-xs font-semibold text-slate-500 hover:text-slate-800 px-2"
        >
          Clear
        </button>

        <button
          onClick={() => soundEngine.playClick()}
          className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-xl text-xs font-semibold shadow-xs transition-colors"
        >
          <FilterIcon size={14} />
          <span>Filter</span>
        </button>
      </div>

      {/* ── Main Split Section: Table (Left) & Vessel Dossier (Right) ─ */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* Fleet List Table */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
          <div className="p-4 border-b border-slate-100 flex items-center justify-between">
            <h2 className="text-sm font-bold font-head text-slate-900">
              Fleet List ({filtered.length})
            </h2>
            <span className="text-xs font-medium text-slate-400">
              Showing 1–{filtered.length} of {filtered.length} vessels
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-50/70 border-b border-slate-200/80 text-slate-500 font-semibold uppercase tracking-wider text-[10px]">
                  <th className="p-3 pl-4 w-8"><input type="checkbox" className="rounded text-blue-600 focus:ring-0" /></th>
                  <th className="p-3">Vessel ID</th>
                  <th className="p-3">Vessel Name</th>
                  <th className="p-3">Type</th>
                  <th className="p-3">Carrier</th>
                  <th className="p-3">Current Location</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Capacity (TEU)</th>
                  <th className="p-3">Utilization</th>
                  <th className="p-3 pr-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filtered.map(v => {
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
                          ? isAdrift ? 'bg-rose-50/70 font-medium' : 'bg-blue-50/70 font-medium'
                          : 'hover:bg-slate-50'
                      }`}
                    >
                      <td className="p-3 pl-4" onClick={e => e.stopPropagation()}>
                        <input type="checkbox" checked={isSelected} onChange={() => {}} className="rounded text-blue-600 focus:ring-0" />
                      </td>
                      <td className="p-3 font-mono font-bold text-blue-600">
                        {v.id}
                      </td>
                      <td className="p-3 font-bold text-slate-800 truncate max-w-[130px]">
                        {v.name}
                      </td>
                      <td className="p-3 text-slate-600">
                        {v.type}
                      </td>
                      <td className="p-3 text-slate-600 truncate max-w-[100px]">
                        {v.carrier}
                      </td>
                      <td className="p-3">
                        <div className="flex items-center gap-1.5 font-medium text-slate-800">
                          <span>{v.flag}</span>
                          <span>{v.location}</span>
                        </div>
                        <div className="text-[10px] text-slate-400 font-mono">{v.portCode}</div>
                      </td>
                      <td className="p-3">
                        {v.status === 'Available' ? (
                          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                            Available
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-rose-700">
                            <span className="w-1.5 h-1.5 rounded-full bg-rose-500" />
                            Unavailable
                          </span>
                        )}
                      </td>
                      <td className="p-3 font-mono font-bold text-slate-800">
                        {v.capacity}
                      </td>
                      <td className="p-3">
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-bold text-[11px] w-8">{v.loadPct}%</span>
                          <div className="w-16 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                            <div
                              className={`h-full rounded-full ${v.loadPct >= 95 ? 'bg-rose-500' : v.loadPct >= 80 ? 'bg-blue-600' : 'bg-blue-400'}`}
                              style={{ width: `${v.loadPct}%` }}
                            />
                          </div>
                        </div>
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
                <button 
                  onClick={() => soundEngine.playClick()}
                  className="text-slate-400 hover:text-slate-600 p-1 rounded-lg hover:bg-slate-100"
                >
                  <X size={16} />
                </button>
              </div>

              <h3 className="text-lg font-head font-extrabold text-slate-900">
                {selectedVessel.name}
              </h3>

              {/* Subtabs: Overview, Route & Schedule, Cargo, Maintenance, History */}
              <div className="flex items-center gap-4 mt-3 border-b border-slate-100 text-xs font-semibold">
                {['Overview', 'Route & Schedule', 'Cargo', 'Maintenance', 'History'].map(tab => (
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

              {/* Vessel Image Component & Metadata Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-12 gap-3.5 mt-3.5">
                
                {/* Vessel Image Card */}
                <div className="sm:col-span-5 rounded-xl overflow-hidden border border-slate-200 shadow-xs relative aspect-[4/5] sm:aspect-auto">
                  <img
                    src="/images/vessel_eastern_star.jpg"
                    alt={selectedVessel.name}
                    className="w-full h-full object-cover"
                  />
                </div>

                {/* Vessel Specs List */}
                <div className="sm:col-span-7 space-y-1.5 text-xs">
                  <div className="flex justify-between py-0.5 border-b border-slate-100">
                    <span className="text-slate-400">Vessel ID</span>
                    <span className="font-mono font-bold text-slate-800">{selectedVessel.id}</span>
                  </div>
                  <div className="flex justify-between py-0.5 border-b border-slate-100">
                    <span className="text-slate-400">Name</span>
                    <span className="font-semibold text-slate-800">{selectedVessel.name}</span>
                  </div>
                  <div className="flex justify-between py-0.5 border-b border-slate-100">
                    <span className="text-slate-400">Type</span>
                    <span className="text-slate-800">{selectedVessel.type} Vessel</span>
                  </div>
                  <div className="flex justify-between py-0.5 border-b border-slate-100">
                    <span className="text-slate-400">Carrier</span>
                    <span className="text-slate-800 truncate max-w-[120px]">{selectedVessel.carrier}</span>
                  </div>
                  <div className="flex justify-between py-0.5 border-b border-slate-100">
                    <span className="text-slate-400">Flag</span>
                    <span className="text-slate-800">{selectedVessel.flag}</span>
                  </div>
                  <div className="flex justify-between py-0.5 border-b border-slate-100">
                    <span className="text-slate-400">Capacity</span>
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
                  <div className="flex justify-between py-0.5 border-b border-slate-100">
                    <span className="text-slate-400">Status</span>
                    <span className={`font-bold ${selectedVessel.status === 'Available' ? 'text-emerald-600' : 'text-rose-600'}`}>
                      {selectedVessel.status}
                    </span>
                  </div>
                </div>

              </div>

              {/* Vessel Incident Red Alert Card if unavailable */}
              {selectedVessel.incident && (
                <div className="mt-3.5 p-3.5 rounded-xl bg-rose-50 border border-rose-200/80 text-xs">
                  <div className="flex items-center justify-between text-rose-700 font-bold mb-1">
                    <div className="flex items-center gap-1.5">
                      <AlertTriangle size={15} />
                      <span>Vessel Incident</span>
                    </div>
                    <span className="text-rose-600 hover:underline cursor-pointer flex items-center gap-0.5">
                      View Details <ArrowRight size={12} />
                    </span>
                  </div>
                  <p className="text-rose-900/90 text-[11px] leading-relaxed">
                    {selectedVessel.incident}
                  </p>
                </div>
              )}

            </div>

            {/* Action Buttons */}
            <div className="pt-2 grid grid-cols-2 gap-2">
              <button
                onClick={() => {
                  soundEngine.playClick()
                  alert(`Displaying live satellite AIS telemetry vector for ${selectedVessel.name}`)
                }}
                className="py-2.5 px-3 rounded-xl text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50 border border-slate-200 shadow-xs flex items-center justify-center gap-1.5 transition-colors"
              >
                <MapPin size={14} className="text-blue-600" />
                <span>View Live Location</span>
              </button>

              <button
                onClick={() => {
                  soundEngine.playClick()
                  alert(`Opening emergency incident docket and dispatching salvage response for ${selectedVessel.name}`)
                }}
                className="py-2.5 px-3 rounded-xl text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 shadow-xs flex items-center justify-center gap-1.5 transition-colors"
              >
                <Wrench size={14} />
                <span>Maintenance & Incident</span>
              </button>
            </div>

          </div>
        )}

      </div>

      {/* ── Bottom Row: Fleet by Type, Fleet Status, Top Carriers ──── */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        
        {/* Fleet by Type */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <h4 className="text-xs font-bold text-slate-800 mb-3 font-head">Fleet by Type</h4>
          <div className="flex items-center justify-between gap-4">
            <div className="relative w-20 h-20 flex-shrink-0 flex items-center justify-center">
              <svg viewBox="0 0 36 36" className="w-full h-full -rotate-90">
                <circle cx="18" cy="18" r="14" fill="none" stroke="#f1f5f9" strokeWidth="4" />
                <circle cx="18" cy="18" r="14" fill="none" stroke="#3b82f6" strokeWidth="4" strokeDasharray="71.4 28.6" strokeDashoffset="0" />
                <circle cx="18" cy="18" r="14" fill="none" stroke="#a855f7" strokeWidth="4" strokeDasharray="14.3 85.7" strokeDashoffset="-71.4" />
                <circle cx="18" cy="18" r="14" fill="none" stroke="#06b6d4" strokeWidth="4" strokeDasharray="14.3 85.7" strokeDashoffset="-85.7" />
              </svg>
              <div className="absolute text-center">
                <span className="text-base font-bold font-head text-slate-900 leading-none">7</span>
                <span className="block text-[8px] text-slate-400 font-mono">Vessels</span>
              </div>
            </div>

            <div className="space-y-1 text-[11px] flex-1">
              {[
                { name: 'Container', count: '5 (71.4%)', color: 'bg-blue-500' },
                { name: 'Reefer', count: '1 (14.3%)', color: 'bg-purple-500' },
                { name: 'Bulk', count: '0 (0%)', color: 'bg-amber-500' },
                { name: 'Tanker', count: '0 (0%)', color: 'bg-orange-500' },
                { name: 'Other', count: '1 (14.3%)', color: 'bg-cyan-500' }
              ].map(t => (
                <div key={t.name} className="flex items-center justify-between text-slate-600">
                  <div className="flex items-center gap-1.5">
                    <span className={`w-2 h-2 rounded-full ${t.color}`} />
                    <span>{t.name}</span>
                  </div>
                  <span className="font-mono text-slate-800">{t.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Fleet Status */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <h4 className="text-xs font-bold text-slate-800 mb-3 font-head">Fleet Status</h4>
          <div className="flex items-center justify-between gap-4">
            <div className="relative w-20 h-20 flex-shrink-0 flex items-center justify-center">
              <svg viewBox="0 0 36 36" className="w-full h-full -rotate-90">
                <circle cx="18" cy="18" r="14" fill="none" stroke="#f1f5f9" strokeWidth="4" />
                <circle cx="18" cy="18" r="14" fill="none" stroke="#10b981" strokeWidth="4" strokeDasharray="85.7 14.3" strokeDashoffset="0" />
                <circle cx="18" cy="18" r="14" fill="none" stroke="#f43f5e" strokeWidth="4" strokeDasharray="14.3 85.7" strokeDashoffset="-85.7" />
              </svg>
              <div className="absolute text-center">
                <span className="text-base font-bold font-head text-slate-900 leading-none">7</span>
                <span className="block text-[8px] text-slate-400 font-mono">Vessels</span>
              </div>
            </div>

            <div className="space-y-1 text-[11px] flex-1">
              {[
                { name: 'Available', count: '6 (85.7%)', color: 'bg-emerald-500' },
                { name: 'Unavailable', count: '1 (14.3%)', color: 'bg-rose-500' },
                { name: 'Maintenance', count: '0 (0%)', color: 'bg-amber-500' },
                { name: 'In Transit', count: '0 (0%)', color: 'bg-blue-500' },
                { name: 'Idle', count: '0 (0%)', color: 'bg-slate-400' }
              ].map(t => (
                <div key={t.name} className="flex items-center justify-between text-slate-600">
                  <div className="flex items-center gap-1.5">
                    <span className={`w-2 h-2 rounded-full ${t.color}`} />
                    <span>{t.name}</span>
                  </div>
                  <span className="font-mono text-slate-800">{t.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Top Carriers by Fleet Size */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <h4 className="text-xs font-bold text-slate-800 mb-3 font-head">Top Carriers by Fleet Size</h4>
          <div className="space-y-2 text-xs">
            {[
              { carrier: 'Hapag-Lloyd', count: 2 },
              { carrier: 'CMA CGM', count: 1 },
              { carrier: 'MaerskLine', count: 1 },
              { carrier: 'MSC', count: 1 },
              { carrier: 'ONE', count: 1 },
              { carrier: 'Evergreen', count: 1 }
            ].map(c => (
              <div key={c.carrier} className="flex items-center justify-between gap-2">
                <span className="text-slate-600 w-24 text-[11px] truncate">{c.carrier}</span>
                <div className="flex-1 bg-slate-100 h-2 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500 rounded-full" style={{ width: `${(c.count / 2) * 100}%` }} />
                </div>
                <span className="font-mono font-bold text-slate-800 text-[11px] w-3 text-right">{c.count}</span>
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  )
}
