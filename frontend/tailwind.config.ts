import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
      colors: {
        ink: {
          950: '#07111f',
          900: '#0d1726',
          800: '#132238',
        },
        accent: {
          100: '#dff7ff',
          300: '#8fdcff',
          500: '#38bdf8',
          700: '#0284c7',
        },
        warm: {
          300: '#ffd19f',
          500: '#f59e0b',
        },
      },
      boxShadow: {
        glow: '0 24px 80px rgba(56, 189, 248, 0.22)',
      },
      backgroundImage: {
        'hero-radial': 'radial-gradient(circle at top left, rgba(56,189,248,0.28), transparent 30%), radial-gradient(circle at top right, rgba(245,158,11,0.2), transparent 24%), linear-gradient(180deg, #07111f 0%, #0d1726 48%, #f5f8ff 48%, #f5f8ff 100%)',
      },
    },
  },
  plugins: [],
} satisfies Config
