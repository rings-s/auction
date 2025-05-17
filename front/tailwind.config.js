// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ['./src/**/*.{html,js,svelte,ts}'],
    darkMode: 'class',
    theme: {
      extend: {
        
        fontFamily: {
          sans: ['Inter var', 'sans-serif'],
          arabic: ['Tajawal', 'sans-serif'],
        },
      },
    },
    plugins: [
      require('@tailwindcss/forms'),
      require('@tailwindcss/typography'),
      require('@tailwindcss/line-clamp'),
    ],
  };