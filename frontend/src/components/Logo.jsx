export default function Logo({ size = 34, className = '' }) {
  return (
    <div className={`relative flex items-center justify-center ${className}`}>
      <svg 
        width={size} 
        height={size} 
        viewBox="0 0 48 48" 
        fill="none" 
        xmlns="http://www.w3.org/2000/svg"
        className="transform transition-transform duration-300 group-hover:scale-105"
      >
        <defs>
          <linearGradient id="logo-hex-grad" x1="4" y1="4" x2="44" y2="44" gradientUnits="userSpaceOnUse">
            <stop stopColor="#38BDF8" />
            <stop offset="0.5" stopColor="#6366F1" />
            <stop offset="1" stopColor="#0EA5E9" />
          </linearGradient>
          <linearGradient id="logo-chevron-grad" x1="24" y1="8" x2="24" y2="40" gradientUnits="userSpaceOnUse">
            <stop stopColor="#E0F2FE" />
            <stop offset="1" stopColor="#38BDF8" />
          </linearGradient>
          <filter id="logo-glow-filter" x="-20%" y="-20%" width="140%" height="140%" filterUnits="userSpaceOnUse">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* Outer Hexagonal Shield */}
        <polygon 
          points="24,4 42,14 42,34 24,44 6,34 6,14" 
          stroke="url(#logo-hex-grad)" 
          strokeWidth="2.5" 
          strokeLinejoin="round"
          fill="rgba(8, 15, 30, 0.75)"
          filter="url(#logo-glow-filter)"
        />

        {/* Inner Radar Rings & Compass Waypoint */}
        <circle cx="24" cy="24" r="10" stroke="rgba(56, 189, 248, 0.3)" strokeWidth="1.2" strokeDasharray="3 3" />
        
        {/* Dynamic Route Waypoint Arrow */}
        <path 
          d="M24 12 L34 29 L24 25 L14 29 Z" 
          fill="url(#logo-chevron-grad)" 
          filter="drop-shadow(0px 2px 6px rgba(56, 189, 248, 0.6))"
        />

        {/* Pulse Beacon Center */}
        <circle cx="24" cy="25" r="2.5" fill="#38BDF8">
          <animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite" />
        </circle>
      </svg>
    </div>
  )
}
