import { 
  LayoutDashboard, 
  Package, 
  AlertTriangle, 
  Ship, 
  Thermometer, 
  Route, 
  Sparkles, 
  FileText, 
  Settings, 
  HelpCircle,
  Anchor
} from 'lucide-react'
import { soundEngine } from './effects'

const NAV_ITEMS = [
  { id: 'dashboard',   label: 'Dashboard',         icon: LayoutDashboard },
  { id: 'shipments',   label: 'Shipments',         icon: Package },
  { id: 'disruptions', label: 'Disruptions',       icon: AlertTriangle },
  { id: 'fleet',       label: 'Fleet',             icon: Ship },
  { id: 'cold-chain',  label: 'Cold Chain',        icon: Thermometer },
  { id: 'routes',      label: 'Routes & Planning', icon: Route },
  { id: 'ai',          label: 'AI Assistant',      icon: Sparkles, badge: 'New' },
  { id: 'reports',     label: 'Reports',           icon: FileText },
]

export default function Sidebar({ activeTab, onSelectTab }) {
  const getPromoText = () => {
    switch (activeTab) {
      case 'dashboard':
        return 'Smarter Routes. Safer Shipments. A More Resilient Tomorrow.'
      case 'fleet':
        return 'Optimized Fleets for a Sustainable Tomorrow.'
      case 'disruptions':
      default:
        return 'Stronger Supply Chains for a Brighter Tomorrow.'
    }
  }

  return (
    <aside className="w-64 flex-shrink-0 bg-[#0A1128] text-slate-300 flex flex-col justify-between border-r border-slate-800/60 min-h-screen select-none sticky top-0 h-screen">
      
      {/* ── Brand Logo Header ────────────────────────────────────── */}
      <div>
        <div 
          onClick={() => {
            soundEngine.playClick()
            onSelectTab('dashboard')
          }}
          className="px-6 py-6 flex items-center gap-3 cursor-pointer group border-b border-slate-800/40"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/25 group-hover:scale-105 transition-transform flex-shrink-0">
            <Anchor size={22} className="text-white" />
          </div>
          <div>
            <div className="font-head font-extrabold text-white text-lg tracking-tight flex items-center gap-1.5">
              SmartRoute<span className="text-cyan-400">AI</span>
            </div>
            <div className="text-[10px] font-mono text-slate-400 tracking-wider uppercase">
              Supply Chain Control Tower
            </div>
          </div>
        </div>

        {/* ── Navigation Links ─────────────────────────────────────── */}
        <nav className="px-3 py-4 space-y-1">
          {NAV_ITEMS.map((item) => {
            const isActive = activeTab === item.id
            const Icon = item.icon
            return (
              <button
                key={item.id}
                onClick={() => {
                  soundEngine.playClick()
                  onSelectTab(item.id)
                }}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30 font-semibold'
                    : 'text-slate-400 hover:text-white hover:bg-white/[0.05]'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon size={18} className={isActive ? 'text-white' : 'text-slate-400'} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-500 text-white shadow-sm">
                    {item.badge}
                  </span>
                )}
              </button>
            )
          })}
        </nav>
      </div>

      {/* ── Bottom Promotional Card & Secondary Links ────────────── */}
      <div className="p-4 space-y-3">
        {/* Inspirational Maritime Card matching reference */}
        <div className="relative rounded-2xl overflow-hidden p-4 border border-white/10 shadow-lg group">
          <img 
            src="/images/smartroute_hero_bg.jpg" 
            alt="Supply Chain Vessel" 
            className="absolute inset-0 w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[#0A1128] via-[#0A1128]/70 to-transparent" />
          <div className="relative z-10 pt-12">
            <p className="text-xs font-bold text-white leading-snug">
              {getPromoText()}
            </p>
          </div>
        </div>

        {/* Settings & Help */}
        <div className="pt-2 border-t border-slate-800/60 space-y-0.5">
          <button 
            onClick={() => soundEngine.playClick()}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium text-slate-400 hover:text-white hover:bg-white/[0.04] transition-colors"
          >
            <Settings size={16} />
            <span>Settings</span>
          </button>
          <button 
            onClick={() => soundEngine.playClick()}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium text-slate-400 hover:text-white hover:bg-white/[0.04] transition-colors"
          >
            <HelpCircle size={16} />
            <span>Help & Support</span>
          </button>
        </div>
      </div>

    </aside>
  )
}
