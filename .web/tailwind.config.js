/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#89b4fa',
        secondary: '#74c7ec',
        success: '#a6e3a1',
        warning: '#f9e2af',
        error: '#f38ba8',
        bg: {
          primary: '#1e1e2e',
          secondary: '#2a2a3e',
          tertiary: '#363650',
          accent: '#45475a',
          canvas: '#181825',
        },
        text: {
          primary: '#cdd6f4',
          secondary: '#a6adc8',
          muted: '#6c7086',
        },
        border: '#45475a',
        hover: '#585b70',
      },
      fontFamily: {
        sans: ['Segoe UI', 'system-ui', 'sans-serif'],
        mono: ['Consolas', 'monospace'],
      },
    },
  },
  plugins: [],
}