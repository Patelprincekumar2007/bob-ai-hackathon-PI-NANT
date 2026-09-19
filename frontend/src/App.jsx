import { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import TopHeader from './components/TopHeader'
import Dashboard from './components/Dashboard'
import Shipments from './components/Shipments'
import Disruptions from './components/Disruptions'
import Fleet from './components/Fleet'
import ColdChain from './components/ColdChain'
import RoutesPlanning from './components/RoutesPlanning'
import AiAssistant from './components/AiAssistant'
import { apiFetch } from './api'

export default function App() {
  const [page, setPage] = useState('dashboard')
  const [searchQuery, setSearchQuery] = useState('')
  const [currentTime, setCurrentTime] = useState('Mon, 15 Sep 2026 23:20 (IST)')

  useEffect(() => {
    // Format live time string: "Mon, 15 Sep 2026 23:20:15 (IST)"
    const updateClock = () => {
      const d = new Date()
      const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
      const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      const day = days[d.getDay()]
      const date = d.getDate()
      const month = months[d.getMonth()]
      const year = d.getFullYear()
      const hrs = String(d.getHours()).padStart(2, '0')
      const mins = String(d.getMinutes()).padStart(2, '0')
      const secs = String(d.getSeconds()).padStart(2, '0')
      setCurrentTime(`${day}, ${date} ${month} ${year} ${hrs}:${mins}:${secs} (IST)`)
    }
    updateClock()
    const timer = setInterval(updateClock, 1000)
    return () => clearInterval(timer)
  }, [])

  const renderPage = () => {
    switch (page) {
      case 'dashboard':
        return (
          <Dashboard 
            onNavigateToShipments={() => setPage('shipments')}
            onNavigateToDisruptions={() => setPage('disruptions')}
            onNavigateToColdChain={() => setPage('cold-chain')}
          />
        )
      case 'shipments':
        return <Shipments />
      case 'disruptions':
        return <Disruptions onNavigateToShipments={() => setPage('shipments')} />
      case 'fleet':
        return <Fleet />
      case 'cold-chain':
        return <ColdChain />
      case 'routes':
        return <RoutesPlanning />
      case 'ai':
        return <AiAssistant />
      case 'reports':
        return (
          <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-xs space-y-4">
            <h2 className="text-xl font-bold font-head text-slate-900">Executive Logistics & Compliance Reports</h2>
            <p className="text-sm text-slate-500">Generate auditable PDF & CSV manifests for international customs and maritime regulators.</p>
          </div>
        )
      default:
        return <Disruptions onNavigateToShipments={() => setPage('shipments')} />
    }
  }

  return (
    <div className="flex min-h-screen bg-[#F0F4F8] font-sans antialiased text-slate-900">
      
      {/* ── Left Dark Navy Sidebar ─────────────────────────────────── */}
      <Sidebar activeTab={page} onSelectTab={setPage} />

      {/* ── Main Application Workspace ─────────────────────────────── */}
      <div className="flex-1 flex flex-col min-w-0 relative overflow-hidden">
        
        {/* Dynamic Minimal Maritime Background Layer */}
        <div className="fixed inset-0 left-64 pointer-events-none z-0 overflow-hidden">
          {/* Faint high-res vessel photography watermark */}
          <div 
            className="absolute -right-16 -bottom-16 w-[1000px] h-[650px] bg-no-repeat bg-contain bg-right-bottom opacity-[0.035] transition-all duration-1000 blur-[0.5px]"
            style={{ 
              backgroundImage: `url('${
                page === 'disruptions' ? '/images/disruption_hero.jpg' :
                page === 'fleet' ? '/images/fleet_hero.jpg' :
                page === 'cold-chain' ? '/images/coldchain_hero.jpg' :
                page === 'shipments' ? '/images/shipment_hero.jpg' :
                '/images/dashboard_hero.jpg'
              }')` 
            }}
          />
          {/* Subtle atmospheric radial glow */}
          <div className="absolute top-0 right-1/4 w-[500px] h-[500px] bg-blue-500/[0.025] rounded-full blur-3xl pointer-events-none" />
          <div className="absolute bottom-20 left-20 w-[450px] h-[450px] bg-sky-500/[0.02] rounded-full blur-3xl pointer-events-none" />
          
          {/* Subtle Nautical Coordinate Grid Overlay */}
          <svg className="absolute inset-0 w-full h-full opacity-[0.025]" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern id="nautical-grid" width="60" height="60" patternUnits="userSpaceOnUse">
                <path d="M 60 0 L 0 0 0 60" fill="none" stroke="#0f172a" strokeWidth="0.75" />
                <circle cx="60" cy="60" r="1.2" fill="#0f172a" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#nautical-grid)" />
          </svg>
        </div>

        {/* Top Sticky Header */}
        <TopHeader 
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          currentTime={currentTime}
        />

        {/* Dynamic Page Content */}
        <main className="flex-1 p-6 max-w-7xl w-full mx-auto space-y-6 relative z-10">
          {renderPage()}
        </main>

      </div>

    </div>
  )
}
