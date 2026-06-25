/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f2f8f6',
          100: '#e1efe9',
          200: '#c5dfd4',
          300: '#9cc7b8',
          400: '#6fa895',
          500: '#508b77',
          600: '#3e6f5e',
          700: '#345a4d',
          800: '#2b493f',
          900: '#0C2B24', // Card Backgrounds
          950: '#04110E', // Main App Background
          960: '#081C17', // Sidebar / Surface Background
        },
        accent: {
          DEFAULT: '#F2C960', // Primary Action / Highlight
          hover: '#EAB308',
          subtle: '#3D301B', // Amber risk background
        },
        danger: {
          DEFAULT: '#C1432D',
          subtle: '#3A1916',
        },
        success: {
          DEFAULT: '#5E846A',
          subtle: '#1F3125',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        serif: ['Lora', 'serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      }
    },
  },
  plugins: [],
}
