import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { soundEngine } from './effects'
import Logo from './Logo'
import { 
  IconLayoutDashboard, 
  IconPackage, 
  IconAlertTriangle, 
  IconShip, 
  IconTemperature,
  IconVolume, 
  IconVolumeOff
} from '@tabler/icons-react'

const NAV_TABS = [
  { id: 'dashboard',   label: 'Dashboard',   icon: IconLayoutDashboard },
  { id: 'shipments',   label: 'Shipments',   icon: IconPackage },
  { id: 'disruptions', label: 'Disruptions', icon: IconAlertTriangle },
  { id: 'fleet',       label: 'Fleet Matrix',icon: IconShip },
  { id: 'cold-chain',  label: 'Cold Chain',  icon: IconTemperature },
]

export default function Navbar({ activeTab, onSelectTab, aiConfigured, currentTime }) {
  const [isAudioActive, setIsAudioActive] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 10)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const toggleSound = () => {
    const active = soundEngine.toggle()
    setIsAudioActive(active)
  }

  return (
    <header className={`sticky top-0 left-0 right-0 z-50 transition-all duration-300 ${
      scrolled 
        ? 'py-2.5 bg-[#07090e]/85 backdrop-blur-2xl border-b border-white/[0.07] shadow-lg shadow-black/40' 
        : 'py-3.5 bg-transparent border-b border-white/[0.04]'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 flex items-center justify-between gap-4">
        
        {/* Brand Logo with Custom Bespoke SVG */}
        <div 
          onClick={() => onSelectTab('dashboard')}
          className="flex items-center gap-3 cursor-pointer group select-none flex-shrink-0"
        >
          <div className="relative">
            <Logo size={32} />
            <span className="absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full bg-emerald-400 border border-[#07090e]">
              <span className="absolute inset-0 rounded-full bg-emerald-400 animate-ping opacity-60" />
            </span>
          </div>

          <div>
            <div className="flex items-center gap-2">
              <span className="font-head font-bold text-sm sm:text-base text-slate-100 tracking-tight group-hover:text-cyan-300 transition-colors">
                SmartRoute<span className="text-cyan-400 font-bold">.ai</span>
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-white/[0.04] text-slate-400 border border-white/[0.06] font-medium">
                CONTROL TOWER
              </span>
            </div>
            <div className="text-[10px] font-mono tracking-wider text-slate-500 uppercase">
              IBM watsonx.ai Enterprise
            </div>
          </div>
        </div>

        {/* Center Minimal Nav Pill */}
        <nav className="hidden md:flex items-center gap-1 p-1 rounded-full bg-[#0D111A]/80 backdrop-blur-xl border border-white/[0.06] shadow-sm">
          {NAV_TABS.map(tab => {
            const isActive = activeTab === tab.id
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => {
                  soundEngine.playClick()
                  onSelectTab(tab.id)
                }}
                className={`relative flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200 ${
                  isActive 
                    ? 'text-cyan-300 font-semibold' 
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.03]'
                }`}
              >
                {isActive && (
                  <motion.div
                    layoutId="active-nav-pill"
                    className="absolute inset-0 rounded-full bg-cyan-500/15 border border-cyan-500/30"
                    transition={{ type: 'spring', stiffness: 400, damping: 35 }}
                  />
                )}
                <Icon size={14} className={isActive ? 'text-cyan-400' : 'text-slate-500'} />
                <span className="relative z-10">{tab.label}</span>
              </button>
            )
          })}
        </nav>

        {/* Right Side Status & Audio Controls */}
        <div className="flex items-center gap-3">
          {/* Live UTC Clock */}
          {currentTime && (
            <div className="hidden lg:flex items-center gap-1.5 font-mono text-[11px] text-slate-400 bg-white/[0.03] px-2.5 py-1 rounded-full border border-white/[0.05]">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400/80" />
              <span>{currentTime.split(' ').slice(4, 5)[0] || currentTime} UTC</span>
            </div>
          )}

          {/* Watsonx AI Status Pill */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/[0.03] border border-white/[0.06] text-xs font-mono">
            <span className={`w-1.5 h-1.5 rounded-full ${aiConfigured ? 'bg-emerald-400 animate-pulse' : 'bg-cyan-400'}`} />
            <span className="text-slate-300 text-[11px]">watsonx.ai</span>
          </div>

          {/* Sound Toggle */}
          <button
            onClick={toggleSound}
            title={isAudioActive ? 'Mute Sound Feedback' : 'Enable Sound Feedback'}
            className="p-1.5 rounded-full bg-white/[0.03] border border-white/[0.06] text-slate-400 hover:text-white hover:border-white/[0.15] transition-colors"
          >
            {isAudioActive ? <IconVolume size={14} className="text-cyan-400" /> : <IconVolumeOff size={14} />}
          </button>
        </div>

      </div>

      {/* Mobile Horizontal Tabs */}
      <div className="md:hidden flex items-center gap-1 px-4 mt-2 overflow-x-auto pb-1">
        {NAV_TABS.map(tab => {
          const isActive = activeTab === tab.id
          return (
            <button
              key={tab.id}
              onClick={() => {
                soundEngine.playClick()
                onSelectTab(tab.id)
              }}
              className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${
                isActive 
                  ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30' 
                  : 'text-slate-400 bg-white/[0.03] border border-white/[0.05]'
              }`}
            >
              {tab.label}
            </button>
          )
        })}
      </div>
    </header>
  )
}
