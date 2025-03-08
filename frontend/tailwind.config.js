/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        // Primary palette
        primary: {
          50: '#eaffd8',
          100: '#d5ffb1',
          200: '#bbff8a',
          300: '#a9ff68', // Main primary color
          400: '#96f247',
          500: '#7ed321',
          600: '#67b60c',
          700: '#4d8c04',
          800: '#376702',
          900: '#254a01',
        },
        // Secondary palette (red/pink)
        secondary: {
          50: '#ffede8',
          100: '#ffdbd1',
          200: '#ffbcac',
          300: '#ff9d87', 
          400: '#ff8989', // Main secondary color
          500: '#ff6f6f',
          600: '#f55252',
          700: '#e13a3a',
          800: '#c92828',
          900: '#a61c1c',
        },
        // Accent blue palette
        accent: {
          50: '#e8f0ff',
          100: '#d1e2ff',
          200: '#adc5ff',
          300: '#89a8ff', 
          400: '#68a9ff', // Main accent color
          500: '#4d95ff',
          600: '#2176ff',
          700: '#0e61e8',
          800: '#0a4cbf',
          900: '#063a91',
        },
        // Neutral palette
        neutral: {
          50: '#f8f8f8',
          100: '#f0f0f0',
          200: '#e4e4e4',
          300: '#d1d1d1',
          400: '#b4b4b4',
          500: '#949494',
          600: '#6e6e6e',
          700: '#555555',
          800: '#2A2A2A',
          900: '#181818',
        },
      },
      animation: {
        blob: 'blob 7s infinite',
        float: 'float 10s infinite ease-in-out',
        'bounce-slow': 'bounceSlow 2s infinite',
      },
      keyframes: {
        blob: {
          '0%': {
            transform: 'translate(0px, 0px) scale(1)',
          },
          '33%': {
            transform: 'translate(30px, -50px) scale(1.1)',
          },
          '66%': {
            transform: 'translate(-20px, 20px) scale(0.9)',
          },
          '100%': {
            transform: 'translate(0px, 0px) scale(1)',
          },
        },
        float: {
          '0%': { transform: 'translate(0, 0) scale(1)' },
          '33%': { transform: 'translate(30px, -30px) scale(1.05)' },
          '66%': { transform: 'translate(-20px, 20px) scale(0.95)' },
          '100%': { transform: 'translate(0, 0) scale(1)' },
        },
        bounceSlow: {
          '0%, 20%, 50%, 80%, 100%': { transform: 'translateY(0) translateX(-50%)' },
          '40%': { transform: 'translateY(-10px) translateX(-50%)' },
          '60%': { transform: 'translateY(-5px) translateX(-50%)' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/aspect-ratio'),
  ],
}