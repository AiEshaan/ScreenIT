/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: {
          light: '#FAFAFA',
          dark: '#09090B',
        },
        surface: {
          light: '#FFFFFF',
          dark: '#0C0C0F',
        },
        border: {
          light: '#E8E8E8',
          dark: '#1E1E24',
        },
        text: {
          light: '#111111',
          dark: '#FAFAFA',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['Geist Mono', 'IBM Plex Mono', 'monospace'],
      },
      borderRadius: {
        'lg': '16px',
      },
      transitionDuration: {
        'default': '180ms',
      },
    },
  },
  plugins: [],
}
