/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        bg:      "#070B14",
        card:    "#0D1424",
        elev:    "#111827",
        border:  "rgba(255,255,255,0.07)",
        accent:  "#38BDF8",
        accent2: "#818CF8",
        accent3: "#34D399",
        danger:  "#F87171",
        warn:    "#FB923C",
        caution: "#FBBF24",
        success: "#34D399",
      },
      fontFamily: {
        sans:  ["Inter", "system-ui", "sans-serif"],
        head:  ["'Space Grotesk'", "system-ui", "sans-serif"],
        mono:  ["'JetBrains Mono'", "monospace"],
      },
    },
  },
  plugins: [],
}
