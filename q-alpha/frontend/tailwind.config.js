/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Q-Alpha Brand Colors
        'q-bg':        '#030712',
        'q-surface':   '#0a0f1e',
        'q-card':      '#0d1526',
        'q-border':    '#1a2a4a',
        'q-blue':      '#00d4ff',
        'q-green':     '#00ff88',
        'q-red':       '#ff3366',
        'q-amber':     '#f59e0b',
        'q-purple':    '#a855f7',
        'q-muted':     '#8892a4',
        'q-text':      '#e2e8f0',
        'q-dim':       '#c4ccdc',
      },
      fontFamily: {
        'display': ['"Space Grotesk"', '"IBM Plex Mono"', 'monospace'],
        'mono':    ['"IBM Plex Mono"', '"Fira Code"', 'monospace'],
        'sans':    ['"Inter"', 'system-ui', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic':  'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'grid-pattern':    "url(\"data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%231a2a4a' fill-opacity='0.4'%3E%3Cpath d='M0 40L40 0H20L0 20M40 40V20L20 40'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")",
      },
      animation: {
        'pulse-slow':    'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow':          'glow 2s ease-in-out infinite alternate',
        'ticker-slide':  'ticker-slide 30s linear infinite',
        'number-spin':   'number-spin 0.4s ease-out',
        'fade-in':       'fade-in 0.5s ease-out',
        'slide-up':      'slide-up 0.4s ease-out',
        'slide-right':   'slide-right 0.3s ease-out',
      },
      keyframes: {
        glow: {
          '0%':   { boxShadow: '0 0 5px #00d4ff44, 0 0 20px #00d4ff22' },
          '100%': { boxShadow: '0 0 20px #00d4ff88, 0 0 40px #00d4ff44' },
        },
        'ticker-slide': {
          '0%':   { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(-50%)' },
        },
        'fade-in': {
          '0%':   { opacity: 0 },
          '100%': { opacity: 1 },
        },
        'slide-up': {
          '0%':   { opacity: 0, transform: 'translateY(16px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
        'slide-right': {
          '0%':   { opacity: 0, transform: 'translateX(-16px)' },
          '100%': { opacity: 1, transform: 'translateX(0)' },
        },
      },
      boxShadow: {
        'glow-blue':   '0 0 20px rgba(0, 212, 255, 0.3)',
        'glow-green':  '0 0 20px rgba(0, 255, 136, 0.3)',
        'glow-red':    '0 0 20px rgba(255, 51, 102, 0.3)',
        'card':        '0 4px 24px rgba(0, 0, 0, 0.4)',
        'modal':       '0 20px 80px rgba(0, 0, 0, 0.8)',
      },
    },
  },
  plugins: [],
};
