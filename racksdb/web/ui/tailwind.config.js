/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      backgroundImage: {
        'racks_black': "url('/assets/racks_black.jpg')"
      }
    },
  },
  plugins: [],
}

