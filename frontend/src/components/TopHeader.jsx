import { Search, Bell } from 'lucide-react'
import { soundEngine } from './effects'

export default function TopHeader({ searchQuery, onSearchChange, currentTime }) {
  return (
    <header className="h-16 bg-white border-b border-slate-200/80 px-6 flex items-center justify-between gap-4 sticky top-0 z-30 shadow-[0_1px_3px_rgba(0,0,0,0.02)]">
      
      {/* ── Global Search Bar ────────────────────────────────────── */}
      <div className="flex-1 max-w-xl">
        <div className="relative flex items-center">
          <Search size={16} className="absolute left-3.5 text-slate-400 pointer-events-none" />
          <input 
            type="text"
            value={searchQuery || ''}
            onChange={(e) => onSearchChange && onSearchChange(e.target.value)}
            placeholder="Search disruptions, ports, routes or ask SmartRoute AI..."
            className="w-full pl-10 pr-12 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
          />
          <kbd className="absolute right-3 px-1.5 py-0.5 text-[10px] font-mono text-slate-400 bg-white border border-slate-200 rounded shadow-xs pointer-events-none">
            Ctrl K
          </kbd>
        </div>
      </div>

      {/* ── Right-Side Meta & Profile ────────────────────────────── */}
      <div className="flex items-center gap-5">
        
        {/* Live Date & Real-time Data Pill */}
        <div className="hidden lg:flex items-center gap-3 text-xs font-medium text-slate-600 border-r border-slate-200 pr-5">
          <span className="font-mono text-[11px] text-slate-500">
            {currentTime || 'Mon, 15 Sep 2026 23:20 (IST)'}
          </span>
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-[11px] font-semibold border border-emerald-200">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            Live Data
          </span>
        </div>

        {/* Notifications */}
        <button 
          onClick={() => soundEngine.playClick()}
          className="relative p-2 rounded-xl text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors"
          title="Notifications"
        >
          <Bell size={18} />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-rose-500 ring-2 ring-white" />
        </button>

        {/* Operational Status Badge */}
        <div className="flex items-center gap-2 pl-2 text-xs">
          <div className="w-8 h-8 rounded-xl bg-slate-100 text-slate-700 flex items-center justify-center font-mono font-bold text-[11px] border border-slate-200">
            HQ
          </div>
          <div className="hidden sm:block text-left">
            <div className="text-xs font-bold text-slate-800 leading-tight">
              Control Tower
            </div>
            <div className="text-[10px] font-mono text-slate-400 font-medium leading-tight">
              Maritime Ops
            </div>
          </div>
        </div>

      </div>

    </header>
  )
}
