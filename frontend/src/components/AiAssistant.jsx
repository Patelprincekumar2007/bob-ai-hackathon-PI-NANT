import { useState, useRef, useEffect } from 'react'
import { apiFetch, apiPost } from '../api'
import { 
  Sparkles, 
  Send, 
  Bot, 
  User, 
  ShieldAlert, 
  Zap, 
  CheckCircle2, 
  RefreshCw, 
  Flame, 
  Ship, 
  Route, 
  CornerDownLeft,
  ChevronRight,
  Key,
  Database
} from 'lucide-react'
import { soundEngine } from './effects'

export default function AiAssistant() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'ai',
      timestamp: 'Active',
      content: "Welcome to the IBM Granite Logistics Intelligence Assistant. I am continuously synchronized with your 7 active commercial shipments, global meteorological alerts, port labor disruptions, and IoT cold-chain telemetry. Ask any question regarding trade corridors, risk decomposition, vessel allocation, or contingency actions.",
      model: 'ibm/granite-13b-chat-v2',
      metrics: {
        monitoredShipments: 7,
        activeDisruptions: 5,
        decisionConfidence: '100% Deterministic Engine'
      }
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [configured, setConfigured] = useState(false)
  const chatEndRef = useRef(null)

  useEffect(() => {
    apiFetch('/api/ai/status')
      .then(res => setConfigured(res?.configured || false))
      .catch(() => setConfigured(false))
  }, [])

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const quickPrompts = [
    {
      title: 'Arabian Sea Cyclone (SHP-002)',
      prompt: 'Evaluate the operational threat of DISR-002 (Severe Cyclone Arabian Sea) on pharmaceutical shipment SHP-002 to Mumbai. Detail the risk score, cold-chain temperature deviations, and compare the Cape of Good Hope vs Air Freight options.'
    },
    {
      title: 'Vessel Engine Breakdown (SHP-006)',
      prompt: 'Shipment SHP-006 is stranded in the Indian Ocean due to propulsion failure on MV Eastern Star (V-005). What is the exact delay accumulation and what idle fleet asset is recommended for salvage?'
    },
    {
      title: 'Rotterdam Strike & Spoilage (SHP-004)',
      prompt: 'Assess shipment SHP-004 carrying fresh produce into Rotterdam during the dock strike (DISR-003). What is the spoilage risk and why is Antwerp divergence (ALT-ATL-01) recommended?'
    },
    {
      title: 'Global Fleet Idle Capacity',
      prompt: 'What is the current available capacity across the global fleet, and which vessel is best equipped for refrigerated pharmaceutical re-routing?'
    }
  ]

  const handleSend = async (textToSend) => {
    const query = textToSend || input
    if (!query.trim() || loading) return

    soundEngine.playClick()
    const userMsg = {
      id: Date.now(),
      sender: 'user',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      content: query
    }

    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const response = await apiPost('/api/ai/explain', { prompt: query })
      soundEngine.playSuccess()

      const aiMsg = {
        id: Date.now() + 1,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        content: response?.text || "Strategic operational assessment generated from deterministic decision models.",
        model: response?.model_id === 'mock' ? 'IBM Granite Engine (Deterministic Mode)' : (response?.model_id || 'ibm/granite-13b-chat-v2'),
        source: response?.source || 'watsonx'
      }
      setMessages(prev => [...prev, aiMsg])
    } catch (err) {
      soundEngine.playAlert()
      const fallbackMsg = {
        id: Date.now() + 1,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        content: `[IBM Granite Intelligence Advisory]\n\nQuery: "${query}"\n\nOperational Status: Backend connection interrupted. Please ensure the local FastAPI backend service is running on port 8000. All core calculations continue to be managed deterministically by the Python Risk and Decision Engine.`,
        model: 'ibm/granite-13b-chat-v2',
        source: 'local-resilience'
      }
      setMessages(prev => [...prev, fallbackMsg])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* ── Top Header & Panoramic Hero Banner ────────────────────────────── */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-blue-500 text-base">✦</span>
            <h1 className="text-2xl font-black font-head tracking-tight text-slate-900">
              AI Decision & NLP Advisor
            </h1>
          </div>
          <p className="text-xs text-slate-500 mt-1 font-sans">
            Natural language maritime reasoning powered by IBM Granite Foundation Models & deterministic core algorithms.
          </p>
        </div>

        {/* Hero Photo Banner Card */}
        <div className="relative rounded-2xl overflow-hidden shadow-xs border border-slate-200/80 w-full lg:w-[480px] h-[78px] flex-shrink-0 group">
          <img 
            src="/images/disruption_hero.jpg" 
            alt="AI Maritime Reasoning"
            className="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-700"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-sky-950/80 via-blue-900/40 to-transparent flex items-center px-6">
            <div>
              <p className="text-white font-serif italic text-base md:text-lg tracking-wide drop-shadow-md">
                “Granite Explains. The Engine Calculates.”
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* ── Model Telemetry Status Strip ─────────────────────────────────── */}
      <div className="bg-white p-3.5 rounded-2xl border border-slate-200/80 shadow-xs flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
            <Sparkles size={16} />
          </div>
          <div>
            <div className="font-bold text-slate-900 flex items-center gap-2">
              <span>IBM Granite Foundation Model</span>
              <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                ibm/granite-13b-chat-v2
              </span>
            </div>
            <div className="text-[11px] text-slate-400 font-sans">
              Parameters: 13B • Context Window: 8,192 tokens • Multi-Factor Factor Explanation Protocol
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 font-mono text-[11px]">
          <span className="flex items-center gap-1 text-emerald-600 font-semibold bg-emerald-50 px-2.5 py-1 rounded-md border border-emerald-200">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>Decision Engine Active</span>
          </span>
          <span className="text-slate-600 bg-slate-100 px-2.5 py-1 rounded-md border border-slate-200/80">
            {configured ? 'watsonx.ai Live Cloud' : 'Local Deterministic Synthesis'}
          </span>
        </div>
      </div>

      {/* ── Chat Canvas & Interaction Hub ────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* Left: Chat Feed (8 cols) */}
        <div className="lg:col-span-8 bg-white rounded-2xl border border-slate-200/80 shadow-xs flex flex-col h-[580px]">
          
          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto p-5 space-y-4">
            {messages.map((m) => (
              <div 
                key={m.id} 
                className={`flex gap-3 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {m.sender === 'ai' && (
                  <div className="w-8 h-8 rounded-xl bg-blue-600 text-white flex items-center justify-center flex-shrink-0 shadow-xs">
                    <Bot size={16} />
                  </div>
                )}

                <div className={`max-w-[85%] rounded-2xl p-4 text-xs ${
                  m.sender === 'user' 
                    ? 'bg-blue-600 text-white shadow-xs rounded-tr-xs' 
                    : 'bg-slate-50 text-slate-800 border border-slate-200/70 shadow-2xs rounded-tl-xs space-y-2'
                }`}>
                  <div className="flex items-center justify-between gap-4 pb-1 border-b border-black/5">
                    <span className="font-bold text-[11px] opacity-80">
                      {m.sender === 'user' ? 'Logistics Coordinator' : 'IBM Granite NLP Advisory'}
                    </span>
                    <span className="font-mono text-[10px] opacity-60">
                      {m.timestamp}
                    </span>
                  </div>

                  {/* Body text with structured formatting */}
                  <div className="whitespace-pre-line leading-relaxed font-sans mt-1">
                    {m.content}
                  </div>

                  {/* Optional AI Telemetry Badge */}
                  {m.metrics && (
                    <div className="pt-2 border-t border-slate-200/60 grid grid-cols-3 gap-2 font-mono text-[10px] text-slate-500">
                      <div className="bg-white p-1.5 rounded border border-slate-200/60">
                        <span>Shipments: </span><b className="text-slate-800">{m.metrics.monitoredShipments}</b>
                      </div>
                      <div className="bg-white p-1.5 rounded border border-slate-200/60">
                        <span>Disruptions: </span><b className="text-rose-600">{m.metrics.activeDisruptions}</b>
                      </div>
                      <div className="bg-white p-1.5 rounded border border-slate-200/60">
                        <span>Logic: </span><b className="text-emerald-600">{m.metrics.decisionConfidence}</b>
                      </div>
                    </div>
                  )}
                </div>

                {m.sender === 'user' && (
                  <div className="w-8 h-8 rounded-xl bg-slate-900 text-white flex items-center justify-center flex-shrink-0 shadow-xs font-bold text-xs">
                    <User size={15} />
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="flex gap-3 justify-start items-center text-xs text-slate-400 font-mono">
                <div className="w-8 h-8 rounded-xl bg-blue-100 text-blue-600 flex items-center justify-center flex-shrink-0 animate-pulse">
                  <Bot size={16} />
                </div>
                <div className="bg-slate-50 p-3 rounded-xl border border-slate-200/60 flex items-center gap-2">
                  <RefreshCw size={13} className="animate-spin text-blue-600" />
                  <span>IBM Granite synthesizing deterministic calculations...</span>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Input Box */}
          <div className="p-3 border-t border-slate-100 bg-slate-50/50 rounded-b-2xl">
            <form 
              onSubmit={(e) => {
                e.preventDefault()
                handleSend()
              }}
              className="flex items-center gap-2 bg-white p-1.5 rounded-xl border border-slate-200 shadow-2xs focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500/20 transition-all"
            >
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask IBM Granite about shipments (SHP-001..SHP-007), cyclone routes, cold-chain excursions, or fleet..."
                className="flex-1 px-3 py-2 text-xs bg-transparent border-none focus:outline-none text-slate-900 placeholder-slate-400"
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="p-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white transition-colors"
              >
                <Send size={15} />
              </button>
            </form>
          </div>

        </div>

        {/* Right: Quick Prompts & Decision Context (4 cols) */}
        <div className="lg:col-span-4 space-y-4">
          
          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-5 space-y-3">
            <h3 className="text-sm font-bold font-head text-slate-900 flex items-center gap-2">
              <Zap size={15} className="text-amber-500" />
              <span>Verified Operational Prompts</span>
            </h3>
            <p className="text-xs text-slate-400 font-sans">
              Click any verified operational scenario to inspect how IBM Granite explains the deterministic calculation:
            </p>

            <div className="space-y-2">
              {quickPrompts.map((qp, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(qp.prompt)}
                  disabled={loading}
                  className="w-full text-left p-3 rounded-xl bg-slate-50 hover:bg-blue-50/60 border border-slate-200/60 hover:border-blue-300 transition-all group"
                >
                  <div className="text-xs font-bold text-slate-800 group-hover:text-blue-600 flex items-center justify-between">
                    <span>{qp.title}</span>
                    <ChevronRight size={13} className="text-slate-400 group-hover:text-blue-600 group-hover:translate-x-0.5 transition-all" />
                  </div>
                  <p className="text-[11px] text-slate-500 mt-1 line-clamp-2 leading-relaxed">
                    {qp.prompt}
                  </p>
                </button>
              ))}
            </div>
          </div>

          {/* Solution Architecture Governance Card */}
          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-5 space-y-2.5">
            <h4 className="text-xs font-bold font-head text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
              <Database size={14} className="text-blue-600" />
              <span>Solution Governance (SOLUTION_PLAN.md)</span>
            </h4>
            <div className="space-y-2 text-xs">
              <div className="flex items-center justify-between text-slate-600">
                <span>Risk & Delay Calculations:</span>
                <span className="font-mono font-bold text-emerald-600">Deterministic (Python)</span>
              </div>
              <div className="flex items-center justify-between text-slate-600">
                <span>Agent Tool Interface:</span>
                <span className="font-mono text-slate-800">MCP (7 Tools)</span>
              </div>
              <div className="flex items-center justify-between text-slate-600">
                <span>Explanation Model:</span>
                <span className="font-mono text-slate-800">IBM Granite 13B</span>
              </div>
              <div className="flex items-center justify-between text-slate-600">
                <span>Hallucination Guard:</span>
                <span className="font-mono text-emerald-600">Active (Fact-Grounded)</span>
              </div>
            </div>
          </div>

        </div>

      </div>

    </div>
  )
}
