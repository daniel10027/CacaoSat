import type { Config } from 'tailwindcss';

/**
 * Design system CacaoSat — palette drapeau de Côte d'Ivoire.
 * orange (Sassandra) · blanc · vert (canopée) + accents nuit / or cacao / sable.
 */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        ci: {
          orange: '#FF7A00',
          'orange-600': '#E06A00',
          white: '#FFFFFF',
          green: '#00A651',
          'green-600': '#008C45',
          'green-700': '#006C36',
        },
        night: '#08130E',
        'night-2': '#0E211A',
        cacao: '#7B3F00',
        sand: '#F4EAD5',
        canopy: '#04160F',
        risk: {
          low: '#00A651',
          medium: '#E8A33D',
          high: '#C0392B',
          none: '#9AA0A6',
        },
      },
      fontFamily: {
        display: ['Poppins', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        glow: '0 0 40px -8px rgba(255, 122, 0, 0.45)',
        'glow-green': '0 0 48px -6px rgba(0, 166, 81, 0.4)',
        card: '0 1px 2px rgba(8,19,14,0.06), 0 12px 32px -12px rgba(8,19,14,0.18)',
      },
      borderRadius: { xl2: '1.25rem' },
      backgroundImage: {
        'orbit-grid':
          'radial-gradient(circle at 50% 50%, rgba(255,255,255,0.06) 1px, transparent 1px)',
        'flag-sheen':
          'linear-gradient(100deg, #FF7A00 0%, #FF7A00 33%, #FFFFFF 33%, #FFFFFF 66%, #00A651 66%, #00A651 100%)',
      },
      keyframes: {
        orbit: { to: { transform: 'rotate(360deg)' } },
        'float-y': {
          '0%,100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        shimmer: { '100%': { transform: 'translateX(100%)' } },
        'fade-up': {
          from: { opacity: '0', transform: 'translateY(16px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        'fade-in': { from: { opacity: '0' }, to: { opacity: '1' } },
      },
      animation: {
        orbit: 'orbit 24s linear infinite',
        'orbit-fast': 'orbit 9s linear infinite',
        'float-y': 'float-y 6s ease-in-out infinite',
        shimmer: 'shimmer 2.2s infinite',
        'fade-up': 'fade-up 0.6s cubic-bezier(0.16,1,0.3,1) both',
        'fade-in': 'fade-in 0.4s ease-out both',
      },
    },
  },
  plugins: [],
} satisfies Config;
