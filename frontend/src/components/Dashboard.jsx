import { useState, useEffect } from 'react'
import { apiFetch } from '../api'
import { 
  Package, 
  AlertTriangle, 
  Flame, 
  Ship, 
  CloudRain, 
  BarChart3, 
  Maximize2, 
  Plus, 
  Minus, 
  MapPin, 
  Anchor, 
  ArrowUpRight, 
  ChevronDown,
  Navigation,
  ExternalLink
} from 'lucide-react'
import { soundEngine } from './effects'

export default function Dashboard({ onNavigateToShipments, onNavigateToDisruptions, onNavigateToColdChain }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [riskFilter, setRiskFilter] = useState('By Risk Level')
  const [statusFilter, setStatusFilter] = useState('All Shipments')

  useEffect(() => {
    apiFetch('/api/dashboard')
      .then(d => {
        setData(d)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  // 6 Executive KPI Telemetry metrics matching mockup
  const kpis = [
    {
      id: 'total-shipments',
      label: 'Total Shipments',
      value: '7',
      change: '+ 12%',
      changeType: 'up',
      subtitle: 'Active global shipments',
      icon: Ship,
      iconBg: 'bg-sky-50 text-sky-600 border border-sky-200/60',
      badgeBg: 'bg-emerald-50 text-emerald-600',
    },
    {
      id: 'at-risk',
      label: 'At-Risk Shipments',
      value: '5',
      change: '+ 25%',
      changeType: 'up',
      subtitle: 'Need attention',
      icon: AlertTriangle,
      iconBg: 'bg-amber-50 text-amber-600 border border-amber-200/60',
      badgeBg: 'bg-emerald-50 text-emerald-600',
    },
    {
      id: 'critical-risk',
      label: 'Critical Risk',
      value: '3',
      change: '+ 50%',
      changeType: 'up',
      subtitle: 'Immediate action required',
      icon: Flame,
      iconBg: 'bg-rose-50 text-rose-600 border border-rose-200/60',
      badgeBg: 'bg-rose-50 text-rose-600',
    },
    {
      id: 'active-disruptions',
      label: 'Active Disruptions',
      value: '5',
      change: '+ 17%',
      changeType: 'up',
      subtitle: 'Weather, strikes, port issues',
      icon: CloudRain,
      iconBg: 'bg-indigo-50 text-indigo-600 border border-indigo-200/60',
      badgeBg: 'bg-indigo-50 text-indigo-600',
    },
    {
      id: 'available-vessels',
      label: 'Available Vessels',
      value: '6',
      change: '+ 20%',
      changeType: 'up',
      subtitle: 'Ready for deployment',
      icon: Ship,
      iconBg: 'bg-teal-50 text-teal-600 border border-teal-200/60',
      badgeBg: 'bg-emerald-50 text-emerald-600',
    },
    {
      id: 'fleet-utilization',
      label: 'Fleet Utilization',
      value: '57.1%',
      change: '+ 8%',
      changeType: 'up',
      subtitle: 'Overall vessel capacity',
      icon: BarChart3,
      iconBg: 'bg-blue-50 text-blue-600 border border-blue-200/60',
      badgeBg: 'bg-emerald-50 text-emerald-600',
    },
  ]

  // Recent Disruptions data matching mockup
  const recentDisruptions = [
    {
      id: 'DISR-001',
      title: 'Shanghai Port Congestion',
      subtitle: 'CNSHA • 3 days delay',
      severity: 'HIGH',
      badgeClass: 'bg-amber-50 text-amber-700 border-amber-200',
      icon: Anchor,
      date: '08 Jul',
    },
    {
      id: 'DISR-002',
      title: 'Severe Cyclone – Arabian Sea',
      subtitle: 'INBOM, INPAV • 5 days delay',
      severity: 'CRITICAL',
      badgeClass: 'bg-rose-50 text-rose-700 border-rose-200',
      icon: CloudRain,
      date: '17 Jul',
    },
    {
      id: 'DISR-003',
      title: 'Rotterdam Port Strike',
      subtitle: 'NLRTM • 8 days delay',
      severity: 'HIGH',
      badgeClass: 'bg-amber-50 text-amber-700 border-amber-200',
      icon: AlertTriangle,
      date: '13 Jul',
    },
    {
      id: 'DISR-004',
      title: 'Vessel Engine Failure',
      subtitle: 'MV Eastern Star • 14 days delay',
      severity: 'CRITICAL',
      badgeClass: 'bg-rose-50 text-rose-700 border-rose-200',
      icon: Ship,
      date: '16 Jul',
    },
    {
      id: 'DISR-005',
      title: 'US Customs Inspection',
      subtitle: 'USLAX, USNYC • 2 days delay',
      severity: 'MEDIUM',
      badgeClass: 'bg-amber-50 text-amber-600 border-amber-200',
      icon: Package,
      date: '19 Jul',
    },
  ]

  // At-Risk Shipments data matching mockup
  const atRiskShipments = [
    { id: 'SHP-004', desc: 'Fresh produce - fruits', risk: 'CRITICAL', eta: '30 Jul' },
    { id: 'SHP-006', desc: 'Clothing and textiles', risk: 'CRITICAL', eta: '05 Aug' },
    { id: 'SHP-002', desc: 'Pharmaceuticals', risk: 'HIGH', eta: '26 Jul' },
    { id: 'SHP-001', desc: 'Electronics', risk: 'HIGH', eta: '31 Jul' },
    { id: 'SHP-003', desc: 'Automotive parts', risk: 'MEDIUM', eta: '27 Jul' },
  ]

  // Fleet Status data matching mockup
  const fleetStatus = [
    { id: 'V-001', type: 'Container', status: 'Available', util: 61, isAvailable: true },
    { id: 'V-002', type: 'Container', status: 'Available', util: 94, isAvailable: true },
    { id: 'V-003', type: 'Reefer', status: 'Available', util: 91, isAvailable: true },
    { id: 'V-004', type: 'Container', status: 'Available', util: 97, isAvailable: true },
    { id: 'V-005', type: 'Container', status: 'Unavailable', util: 100, isAvailable: false },
    { id: 'V-006', type: 'Container', status: 'Available', util: 22, isAvailable: true },
    { id: 'V-007', type: 'Container', status: 'Available', util: 50, isAvailable: true },
  ]

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* ── Top Header & Panoramic Hero Banner ────────────────────────────── */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-blue-500 text-base">✦</span>
            <h1 className="text-2xl font-black font-head tracking-tight text-slate-900">
              Executive Operations Overview
            </h1>
          </div>
          <p className="text-xs text-slate-500 mt-1 font-sans">
            Real-time maritime tracking, multi-factor risk scoring, and deterministic contingency optimization.
          </p>
        </div>

        {/* Hero Photo Banner Card ("Keep the World Moving") */}
        <div className="relative rounded-2xl overflow-hidden shadow-xs border border-slate-200/80 w-full lg:w-[480px] h-[78px] flex-shrink-0 group">
          <img 
            src="/images/dashboard_hero.jpg" 
            alt="Keep the World Moving - Commercial Container Vessel"
            className="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-700"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-sky-950/70 via-blue-900/40 to-transparent flex items-center px-6">
            <div>
              <p className="text-white font-serif italic text-base md:text-lg tracking-wide drop-shadow-md">
                “Keep the World Moving”
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* ── 6 KPI Cards Across ─────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {kpis.map(kpi => {
          const Icon = kpi.icon
          return (
            <div 
              key={kpi.id} 
              className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-xs hover:shadow-md transition-all group flex flex-col justify-between"
            >
              <div className="flex items-start justify-between">
                <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${kpi.iconBg}`}>
                  <Icon size={18} />
                </div>
                <span className={`text-[10px] font-mono font-bold px-1.5 py-0.5 rounded-md flex items-center gap-0.5 ${kpi.badgeBg}`}>
                  <span className="text-[9px]">↑</span> {kpi.change}
                </span>
              </div>
              <div className="mt-3">
                <div className="text-2xl font-black font-head text-slate-900 tracking-tight">
                  {kpi.value}
                </div>
                <div className="text-xs font-bold text-slate-700 mt-0.5">
                  {kpi.label}
                </div>
                <div className="text-[10px] text-slate-400 font-sans mt-0.5 truncate">
                  {kpi.subtitle}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* ── Middle Row: Global Map + Risk & Shipment Analytics ─────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* Left: Global Shipments Interactive Ocean Route Map (7 cols) */}
        <div className="lg:col-span-8 bg-white rounded-2xl border border-slate-200/80 shadow-xs p-5 flex flex-col justify-between">
          
          {/* Header with Title and Legend */}
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h2 className="text-sm font-bold font-head text-slate-900">
              Global Shipments Overview
            </h2>

            <div className="flex items-center gap-4 text-xs font-medium text-slate-600">
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-rose-500 inline-block" />
                <span>Critical</span>
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-amber-500 inline-block" />
                <span>At Risk</span>
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" />
                <span>On Track</span>
              </span>
              <button className="text-slate-400 hover:text-slate-600 p-1 rounded-md hover:bg-slate-50 transition-colors">
                <Maximize2 size={14} />
              </button>
            </div>
          </div>

          {/* Map Surface Viewport */}
          <div className="relative mt-3 rounded-xl overflow-hidden bg-[#0A1628] border border-slate-800 h-[280px] w-full flex items-center justify-center">
            
            {/* World Map SVG Vector Layer with Geodesic Routes */}
            <svg viewBox="0 0 900 450" className="w-full h-full object-cover">
              <defs>
                {/* Geodesic Corridor Glow Gradient */}
                <linearGradient id="routeGlowBlue" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.8" />
                  <stop offset="100%" stopColor="#2563eb" stopOpacity="0.3" />
                </linearGradient>
                <linearGradient id="routeGlowAmber" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#fbbf24" stopOpacity="0.9" />
                  <stop offset="100%" stopColor="#d97706" stopOpacity="0.4" />
                </linearGradient>
                <linearGradient id="routeGlowRose" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#f43f5e" stopOpacity="0.9" />
                  <stop offset="100%" stopColor="#be123c" stopOpacity="0.4" />
                </linearGradient>
              </defs>

              {/* Ocean Canvas Background */}
              <rect width="900" height="450" fill="#0A1628" />

              {/* ── Realistic World Continents Shorelines ──────────────────── */}
              <g fill="#14233D" stroke="#1E3A5F" strokeWidth="0.8" opacity="0.95">
                {/* North America */}
                <path d="M 75 75 C 95 60 130 50 165 55 C 190 60 210 45 240 50 C 275 55 310 70 315 95 C 295 105 280 115 285 130 C 265 140 250 165 240 185 C 215 195 200 170 180 165 C 160 160 145 140 130 135 C 110 130 90 105 75 75 Z" />
                <path d="M 140 135 C 175 135 220 130 260 135 C 285 140 295 160 290 185 C 285 205 270 215 255 225 C 240 235 220 240 210 255 C 195 260 185 245 175 225 C 160 200 145 170 140 135 Z" />
                <path d="M 210 255 C 220 265 235 275 245 285 C 240 290 230 285 225 280 C 215 270 205 260 210 255 Z" />

                {/* South America */}
                <path d="M 235 285 C 265 280 305 290 330 315 C 345 330 340 355 330 380 C 315 410 290 435 275 440 C 265 440 260 415 260 385 C 255 355 245 330 235 310 C 230 300 230 290 235 285 Z" />

                {/* Europe */}
                <path d="M 420 85 C 440 70 470 65 500 75 C 515 85 525 105 510 120 C 495 135 480 145 460 145 C 440 145 425 130 420 115 C 415 100 415 90 420 85 Z" />
                <path d="M 405 90 C 415 85 425 95 420 110 C 415 115 405 110 405 90 Z" />
                <path d="M 450 50 C 470 40 490 55 485 75 C 475 85 460 80 450 65 Z" />

                {/* Africa */}
                <path d="M 425 150 C 470 150 515 160 525 190 C 530 220 525 260 515 295 C 500 335 480 375 455 375 C 440 375 425 340 420 300 C 415 260 405 220 410 190 C 415 165 415 155 425 150 Z" />
                <path d="M 525 310 C 535 320 530 350 520 355 C 515 345 520 325 525 310 Z" />

                {/* Asia / Eurasia */}
                <path d="M 515 80 C 560 65 640 55 720 65 C 780 75 830 95 845 125 C 830 150 790 160 760 165 C 710 170 660 160 600 150 C 550 145 525 120 515 80 Z" />
                <path d="M 520 190 C 545 185 565 200 560 225 C 550 235 530 230 520 210 Z" />
                <path d="M 570 190 C 600 190 630 205 635 225 C 630 250 610 275 595 280 C 585 270 580 240 570 210 Z" />
                <path d="M 650 155 C 700 155 750 170 760 195 C 750 225 725 260 705 270 C 685 270 680 240 670 215 C 660 190 645 170 650 155 Z" />
                <path d="M 780 140 C 795 145 795 175 780 180 C 775 165 775 150 780 140 Z" />
                <path d="M 680 285 C 715 285 755 295 765 310 C 740 315 710 310 680 285 Z" />

                {/* Australia */}
                <path d="M 730 330 C 770 320 815 325 830 355 C 840 385 825 420 790 425 C 755 425 735 400 725 365 C 720 345 725 335 730 330 Z" />
                <path d="M 845 405 C 855 410 855 435 845 440 C 840 430 840 415 845 405 Z" />
              </g>

              {/* Latitude / Longitude Subtle Graticule */}
              <line x1="0" y1="120" x2="900" y2="120" stroke="#1e3a5f" strokeWidth="0.5" strokeDasharray="3 4" opacity="0.3" />
              <line x1="0" y1="225" x2="900" y2="225" stroke="#1e3a5f" strokeWidth="0.7" strokeDasharray="4 4" opacity="0.4" />
              <line x1="0" y1="330" x2="900" y2="330" stroke="#1e3a5f" strokeWidth="0.5" strokeDasharray="3 4" opacity="0.3" />
              <line x1="225" y1="0" x2="225" y2="450" stroke="#1e3a5f" strokeWidth="0.5" strokeDasharray="3 4" opacity="0.3" />
              <line x1="450" y1="0" x2="450" y2="450" stroke="#1e3a5f" strokeWidth="0.5" strokeDasharray="3 4" opacity="0.3" />
              <line x1="675" y1="0" x2="675" y2="450" stroke="#1e3a5f" strokeWidth="0.5" strokeDasharray="3 4" opacity="0.3" />

              {/* ── Realistic Maritime Geodesic Corridors ───────────── */}
              {/* Route 1: Trans-Pacific: Shanghai (725, 180) to Los Angeles (175, 175) */}
              <path 
                d="M 725 180 C 780 130 850 120 900 130" 
                fill="none" 
                stroke="#38bdf8" 
                strokeWidth="2" 
                strokeDasharray="5 3" 
                opacity="0.8" 
              />
              <path 
                d="M 0 130 C 50 140 120 150 175 175" 
                fill="none" 
                stroke="#38bdf8" 
                strokeWidth="2" 
                strokeDasharray="5 3" 
                opacity="0.8" 
              />

              {/* Route 2: Europe-India via Suez: Rotterdam (450, 105) -> Mumbai (585, 230) */}
              <path 
                d="M 450 105 C 425 140 460 140 500 160 C 525 180 545 205 585 230" 
                fill="none" 
                stroke="#f43f5e" 
                strokeWidth="2.5" 
                strokeDasharray="5 3" 
                opacity="0.9" 
              />

              {/* Route 3: South America to Europe: Santos (315, 345) to Rotterdam (450, 105) */}
              <path 
                d="M 315 345 C 360 270 410 180 450 105" 
                fill="none" 
                stroke="#fbbf24" 
                strokeWidth="2" 
                strokeDasharray="5 3" 
                opacity="0.85" 
              />

              {/* Route 4: Indian Ocean to Australia: Mumbai (585, 230) to Sydney (805, 385) */}
              <path 
                d="M 585 230 C 670 290 730 350 805 385" 
                fill="none" 
                stroke="#38bdf8" 
                strokeWidth="2" 
                strokeDasharray="5 3" 
                opacity="0.8" 
              />

              {/* Route 5: Shanghai to Mumbai via Malacca: (725, 180) -> (585, 230) */}
              <path 
                d="M 725 180 C 700 240 680 275 640 260 C 610 250 595 240 585 230" 
                fill="none" 
                stroke="#38bdf8" 
                strokeWidth="2" 
                strokeDasharray="5 3" 
                opacity="0.85" 
              />

              {/* ── Active Vessel Telemetry Nodes ────────────────────── */}
              {/* Critical Vessel near Arabian Sea */}
              <g transform="translate(565, 220)">
                <circle cx="0" cy="0" r="12" fill="#f43f5e" opacity="0.3" className="animate-ping" />
                <circle cx="0" cy="0" r="5" fill="#f43f5e" stroke="#ffffff" strokeWidth="1.5" />
              </g>

              {/* At-Risk Vessel in Mid-Atlantic */}
              <g transform="translate(365, 250)">
                <circle cx="0" cy="0" r="10" fill="#fbbf24" opacity="0.3" className="animate-ping" />
                <circle cx="0" cy="0" r="4.5" fill="#fbbf24" stroke="#ffffff" strokeWidth="1.5" />
              </g>

              {/* On-Track Vessel near Australia */}
              <g transform="translate(745, 340)">
                <circle cx="0" cy="0" r="10" fill="#10b981" opacity="0.3" className="animate-ping" />
                <circle cx="0" cy="0" r="4.5" fill="#10b981" stroke="#ffffff" strokeWidth="1.5" />
              </g>

              {/* ── Major Global Anchor Ports ───────────────────────── */}
              {/* Los Angeles (USLAX) */}
              <g transform="translate(175, 175)">
                <circle cx="0" cy="0" r="12" fill="#2563eb" opacity="0.3" />
                <circle cx="0" cy="0" r="5" fill="#2563eb" stroke="#ffffff" strokeWidth="1.5" />
                <rect x="8" y="-13" width="68" height="24" rx="4" fill="#0A1628" stroke="#3b82f6" strokeWidth="0.8" />
                <text x="14" y="-2" fill="#ffffff" fontSize="7" fontWeight="bold" fontFamily="sans-serif">Los Angeles</text>
                <text x="14" y="7" fill="#93c5fd" fontSize="6" fontFamily="sans-serif">USLAX</text>
              </g>

              {/* Rotterdam (NLRTM) */}
              <g transform="translate(450, 105)">
                <circle cx="0" cy="0" r="12" fill="#2563eb" opacity="0.3" />
                <circle cx="0" cy="0" r="5" fill="#2563eb" stroke="#ffffff" strokeWidth="1.5" />
                <rect x="8" y="-13" width="64" height="24" rx="4" fill="#0A1628" stroke="#3b82f6" strokeWidth="0.8" />
                <text x="14" y="-2" fill="#ffffff" fontSize="7" fontWeight="bold" fontFamily="sans-serif">Rotterdam</text>
                <text x="14" y="7" fill="#93c5fd" fontSize="6" fontFamily="sans-serif">NLRTM</text>
              </g>

              {/* Mumbai (INBOM) - Critical Alert */}
              <g transform="translate(585, 230)">
                <circle cx="0" cy="0" r="15" fill="#f43f5e" opacity="0.4" className="animate-pulse" />
                <circle cx="0" cy="0" r="5.5" fill="#f43f5e" stroke="#ffffff" strokeWidth="1.5" />
                <rect x="8" y="-13" width="58" height="24" rx="4" fill="#0A1628" stroke="#f43f5e" strokeWidth="1" />
                <text x="14" y="-2" fill="#ffffff" fontSize="7" fontWeight="bold" fontFamily="sans-serif">Mumbai</text>
                <text x="14" y="7" fill="#fca5a5" fontSize="6" fontFamily="sans-serif">INBOM</text>
              </g>

              {/* Shanghai (CNSHA) - High Alert */}
              <g transform="translate(725, 180)">
                <circle cx="0" cy="0" r="14" fill="#fbbf24" opacity="0.4" />
                <circle cx="0" cy="0" r="5" fill="#fbbf24" stroke="#ffffff" strokeWidth="1.5" />
                <rect x="8" y="-13" width="58" height="24" rx="4" fill="#0A1628" stroke="#fbbf24" strokeWidth="0.8" />
                <text x="14" y="-2" fill="#ffffff" fontSize="7" fontWeight="bold" fontFamily="sans-serif">Shanghai</text>
                <text x="14" y="7" fill="#fde68a" fontSize="6" fontFamily="sans-serif">CNSHA</text>
              </g>

              {/* Santos (BRSSO) */}
              <g transform="translate(315, 345)">
                <circle cx="0" cy="0" r="12" fill="#2563eb" opacity="0.3" />
                <circle cx="0" cy="0" r="5" fill="#2563eb" stroke="#ffffff" strokeWidth="1.5" />
                <rect x="8" y="-13" width="52" height="24" rx="4" fill="#0A1628" stroke="#3b82f6" strokeWidth="0.8" />
                <text x="14" y="-2" fill="#ffffff" fontSize="7" fontWeight="bold" fontFamily="sans-serif">Santos</text>
                <text x="14" y="7" fill="#93c5fd" fontSize="6" fontFamily="sans-serif">BRSSO</text>
              </g>

              {/* Sydney (AUSYD) */}
              <g transform="translate(805, 385)">
                <circle cx="0" cy="0" r="12" fill="#2563eb" opacity="0.3" />
                <circle cx="0" cy="0" r="5" fill="#2563eb" stroke="#ffffff" strokeWidth="1.5" />
                <rect x="8" y="-13" width="52" height="24" rx="4" fill="#0A1628" stroke="#3b82f6" strokeWidth="0.8" />
                <text x="14" y="-2" fill="#ffffff" fontSize="7" fontWeight="bold" fontFamily="sans-serif">Sydney</text>
                <text x="14" y="7" fill="#93c5fd" fontSize="6" fontFamily="sans-serif">AUSYD</text>
              </g>
            </svg>

            {/* Map Controls: Zoom buttons on bottom left */}
            <div className="absolute bottom-3 left-3 flex flex-col gap-1">
              <button 
                onClick={() => soundEngine.playClick()}
                className="w-7 h-7 bg-white text-slate-700 rounded-lg shadow-md border border-slate-200 flex items-center justify-center hover:bg-slate-50 transition-colors font-bold"
              >
                <Plus size={14} />
              </button>
              <button 
                onClick={() => soundEngine.playClick()}
                className="w-7 h-7 bg-white text-slate-700 rounded-lg shadow-md border border-slate-200 flex items-center justify-center hover:bg-slate-50 transition-colors font-bold"
              >
                <Minus size={14} />
              </button>
            </div>

            {/* Map Control: View Full Map on bottom right */}
            <div className="absolute bottom-3 right-3">
              <button 
                onClick={() => soundEngine.playClick()}
                className="px-3 py-1.5 bg-white text-slate-800 text-xs font-semibold rounded-lg shadow-md border border-slate-200 flex items-center gap-1.5 hover:bg-slate-50 transition-colors"
              >
                <Navigation size={13} className="text-blue-600" />
                <span>View Full Map</span>
              </button>
            </div>

          </div>

        </div>

        {/* Right: Risk Distribution + Shipment Status (4 cols) */}
        <div className="lg:col-span-4 flex flex-col gap-4">
          
          {/* Card 1: Risk Distribution with Donut Chart */}
          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-5 flex-1 flex flex-col justify-between">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="text-sm font-bold font-head text-slate-900">
                Risk Distribution
              </h3>
              <div className="flex items-center gap-1 text-xs text-slate-500 bg-slate-50 px-2 py-1 rounded-md border border-slate-200/60 cursor-pointer">
                <span>{riskFilter}</span>
                <ChevronDown size={12} />
              </div>
            </div>

            <div className="flex items-center justify-between gap-4 my-2">
              {/* Donut Chart SVG */}
              <div className="relative w-28 h-28 flex-shrink-0 flex items-center justify-center">
                <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                  {/* Background Track */}
                  <circle cx="50" cy="50" r="38" fill="none" stroke="#F1F5F9" strokeWidth="14" />
                  
                  {/* Segment: Critical (3/7 = 42.9%) -> circumference ~ 238.76 -> dash = 102 */}
                  <circle 
                    cx="50" cy="50" r="38" 
                    fill="none" 
                    stroke="#F43F5E" 
                    strokeWidth="14" 
                    strokeDasharray="102.4 238.76" 
                    strokeDashoffset="0" 
                  />
                  {/* Segment: High (2/7 = 28.6%) -> dash = 68.3 */}
                  <circle 
                    cx="50" cy="50" r="38" 
                    fill="none" 
                    stroke="#F97316" 
                    strokeWidth="14" 
                    strokeDasharray="68.3 238.76" 
                    strokeDashoffset="-102.4" 
                  />
                  {/* Segment: Medium (1/7 = 14.3%) -> dash = 34.1 */}
                  <circle 
                    cx="50" cy="50" r="38" 
                    fill="none" 
                    stroke="#FBBF24" 
                    strokeWidth="14" 
                    strokeDasharray="34.1 238.76" 
                    strokeDashoffset="-170.7" 
                  />
                  {/* Segment: Low (1/7 = 14.3%) -> dash = 34.1 */}
                  <circle 
                    cx="50" cy="50" r="38" 
                    fill="none" 
                    stroke="#10B981" 
                    strokeWidth="14" 
                    strokeDasharray="34.1 238.76" 
                    strokeDashoffset="-204.8" 
                  />
                </svg>
                {/* Center Donut Text */}
                <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                  <span className="text-xl font-black font-head text-slate-900 leading-none">7</span>
                  <span className="text-[9px] text-slate-400 font-sans mt-0.5">Shipments</span>
                </div>
              </div>

              {/* Legend with percentages */}
              <div className="space-y-1.5 text-xs flex-1">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
                    <span className="text-slate-700 font-medium">Critical</span>
                  </div>
                  <div className="font-mono text-slate-500">
                    <span className="font-bold text-slate-800">3</span> (42.9%)
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-orange-500" />
                    <span className="text-slate-700 font-medium">High</span>
                  </div>
                  <div className="font-mono text-slate-500">
                    <span className="font-bold text-slate-800">2</span> (28.6%)
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-amber-400" />
                    <span className="text-slate-700 font-medium">Medium</span>
                  </div>
                  <div className="font-mono text-slate-500">
                    <span className="font-bold text-slate-800">1</span> (14.3%)
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                    <span className="text-slate-700 font-medium">Low</span>
                  </div>
                  <div className="font-mono text-slate-500">
                    <span className="font-bold text-slate-800">1</span> (14.3%)
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Card 2: Shipment Status Segmented Bar */}
          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-5 flex flex-col justify-between">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <h3 className="text-sm font-bold font-head text-slate-900">
                Shipment Status
              </h3>
              <div className="flex items-center gap-1 text-xs text-slate-500 bg-slate-50 px-2 py-1 rounded-md border border-slate-200/60 cursor-pointer">
                <span>{statusFilter}</span>
                <ChevronDown size={12} />
              </div>
            </div>

            {/* Segmented Progress Bar */}
            <div className="my-3">
              <div className="h-3 w-full rounded-full overflow-hidden flex bg-slate-100 p-0.5 gap-0.5">
                {/* In Transit: 71.4% */}
                <div className="h-full bg-blue-500 rounded-l-full" style={{ width: '71.4%' }} />
                {/* Delayed: 14.3% */}
                <div className="h-full bg-orange-400" style={{ width: '14.3%' }} />
                {/* Delivered: 0% */}
                {/* Pending: 14.3% */}
                <div className="h-full bg-slate-400 rounded-r-full" style={{ width: '14.3%' }} />
              </div>

              {/* Legend for Status */}
              <div className="grid grid-cols-2 gap-y-1.5 gap-x-2 text-[11px] mt-2.5">
                <div className="flex items-center gap-1.5 text-slate-600">
                  <span className="w-2 h-2 rounded-full bg-blue-500" />
                  <span>In Transit: <b className="text-slate-800 font-mono">5 (71.4%)</b></span>
                </div>
                <div className="flex items-center gap-1.5 text-slate-600">
                  <span className="w-2 h-2 rounded-full bg-orange-400" />
                  <span>Delayed: <b className="text-slate-800 font-mono">1 (14.3%)</b></span>
                </div>
                <div className="flex items-center gap-1.5 text-slate-600">
                  <span className="w-2 h-2 rounded-full bg-emerald-500" />
                  <span>Delivered: <b className="text-slate-800 font-mono">0 (0%)</b></span>
                </div>
                <div className="flex items-center gap-1.5 text-slate-600">
                  <span className="w-2 h-2 rounded-full bg-slate-400" />
                  <span>Pending: <b className="text-slate-800 font-mono">1 (14.3%)</b></span>
                </div>
              </div>
            </div>
          </div>

        </div>

      </div>

      {/* ── Bottom Row: 3 Parallel Quick Registers ─────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        
        {/* Register 1: Recent Disruptions */}
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h3 className="text-sm font-bold font-head text-slate-900">
              Recent Disruptions
            </h3>
            <button 
              onClick={() => {
                soundEngine.playClick()
                onNavigateToDisruptions()
              }}
              className="text-xs font-semibold text-blue-600 hover:text-blue-700 transition-colors"
            >
              View All
            </button>
          </div>

          <div className="divide-y divide-slate-100 mt-1">
            {recentDisruptions.map(item => {
              const Icon = item.icon
              return (
                <div key={item.id} className="py-2.5 flex items-center justify-between hover:bg-slate-50/60 px-1 rounded-lg transition-colors">
                  <div className="flex items-center gap-2.5">
                    <div className="w-7 h-7 rounded-lg bg-slate-100 flex items-center justify-center text-slate-600 flex-shrink-0">
                      <Icon size={14} />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-slate-800 truncate max-w-[150px]">
                        {item.title}
                      </div>
                      <div className="text-[10px] text-slate-400 font-sans">
                        {item.subtitle}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 text-right">
                    <span className={`text-[10px] font-mono font-bold px-1.5 py-0.5 rounded border ${item.badgeClass}`}>
                      {item.severity}
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">
                      {item.date}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Register 2: At-Risk Shipments */}
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h3 className="text-sm font-bold font-head text-slate-900">
              At-Risk Shipments
            </h3>
            <button 
              onClick={() => {
                soundEngine.playClick()
                onNavigateToShipments()
              }}
              className="text-xs font-semibold text-blue-600 hover:text-blue-700 transition-colors"
            >
              View All
            </button>
          </div>

          <div className="mt-1">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="text-[10px] font-semibold text-slate-400 uppercase border-b border-slate-100">
                  <th className="pb-2">ID</th>
                  <th className="pb-2">Description</th>
                  <th className="pb-2">Risk</th>
                  <th className="pb-2 text-right">ETA</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {atRiskShipments.map(s => (
                  <tr key={s.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-2.5 font-mono text-blue-600 font-semibold">{s.id}</td>
                    <td className="py-2.5 text-slate-800 font-medium truncate max-w-[110px]">{s.desc}</td>
                    <td className="py-2.5">
                      <span className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded border ${
                        s.risk === 'CRITICAL' ? 'bg-rose-50 text-rose-700 border-rose-200' :
                        s.risk === 'HIGH' ? 'bg-amber-50 text-amber-700 border-amber-200' :
                        'bg-amber-50 text-amber-600 border-amber-200'
                      }`}>
                        {s.risk}
                      </span>
                    </td>
                    <td className="py-2.5 text-right font-mono text-slate-500 text-[11px]">{s.eta}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Register 3: Fleet Status with Utilization Bar */}
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h3 className="text-sm font-bold font-head text-slate-900">
              Fleet Status
            </h3>
            <button 
              onClick={() => {
                soundEngine.playClick()
                onNavigateToShipments()
              }}
              className="text-xs font-semibold text-blue-600 hover:text-blue-700 transition-colors"
            >
              View All
            </button>
          </div>

          <div className="mt-1">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="text-[10px] font-semibold text-slate-400 uppercase border-b border-slate-100">
                  <th className="pb-2">Vessel</th>
                  <th className="pb-2">Type</th>
                  <th className="pb-2">Status</th>
                  <th className="pb-2 text-right">Utilization</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {fleetStatus.map(v => (
                  <tr key={v.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-2 font-mono text-slate-900 font-semibold">{v.id}</td>
                    <td className="py-2 text-slate-600 text-[11px]">{v.type}</td>
                    <td className="py-2">
                      <span className="flex items-center gap-1 text-[11px]">
                        <span className={`w-1.5 h-1.5 rounded-full ${v.isAvailable ? 'bg-emerald-500' : 'bg-rose-500'}`} />
                        <span className={v.isAvailable ? 'text-slate-700' : 'text-rose-600 font-semibold'}>{v.status}</span>
                      </span>
                    </td>
                    <td className="py-2 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <span className="font-mono text-[10px] text-slate-600 w-6">{v.util}%</span>
                        <div className="w-12 h-1.5 rounded-full bg-slate-100 overflow-hidden">
                          <div 
                            className={`h-full rounded-full ${v.isAvailable ? 'bg-blue-600' : 'bg-rose-500'}`} 
                            style={{ width: `${v.util}%` }} 
                          />
                        </div>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

      </div>

    </div>
  )
}
