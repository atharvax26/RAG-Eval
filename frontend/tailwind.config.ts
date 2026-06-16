import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg:      '#0C0C0C',
        card:    '#161616',
        card2:   '#1E1E1E',
        teal:    '#00E5C4',
        teal2:   '#00B8A0',
        border:  '#2E2E2E',
        lgray:   '#D0D0D0',
        mgray:   '#808080',
        amber:   '#F5A623',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
} satisfies Config
