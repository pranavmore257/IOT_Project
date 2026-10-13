/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        traffic: {
          red: '#EF4444',
          yellow: '#F59E0B',
          green: '#10B981',
          dark: '#0F172A',
          card: '#1E293B',
          border: '#334155'
        }
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow-red': 'glowRed 1.5s ease-in-out infinite alternate',
        'glow-green': 'glowGreen 1.5s ease-in-out infinite alternate',
      },
      keyframes: {
        glowRed: {
          '0%': { boxShadow: '0 0 10px rgba(239, 68, 68, 0.5)' },
          '100%': { boxShadow: '0 0 25px rgba(239, 68, 68, 1)' },
        },
        glowGreen: {
          '0%': { boxShadow: '0 0 10px rgba(16, 185, 129, 0.5)' },
          '100%': { boxShadow: '0 0 25px rgba(16, 185, 129, 1)' },
        }
      }
    },
  },
  plugins: [],
}
