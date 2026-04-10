/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        void: '#020408',
        panel: '#080f1a',
        surface: '#0d1829',
        border: '#1a2d4a',
        accent: '#00d4ff',
        accent2: '#7b2fff',
        success: '#00ff88',
        warning: '#ffaa00',
        danger: '#ff3366',
        muted: '#4a6280',
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        display: ['Orbitron', 'sans-serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'scan': 'scan 2s linear infinite',
        'flicker': 'flicker 4s linear infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        scan: { '0%': { top: '0%' }, '100%': { top: '100%' } },
        flicker: {
          '0%, 96%, 100%': { opacity: 1 },
          '97%': { opacity: 0.4 },
          '98%': { opacity: 1 },
          '99%': { opacity: 0.6 },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px #00d4ff33' },
          '100%': { boxShadow: '0 0 20px #00d4ff88, 0 0 40px #00d4ff22' },
        }
      }
    }
  },
  plugins: []
}
