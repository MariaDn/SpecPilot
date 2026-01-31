/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{ts,html}", "./index.html"],
  theme: {
    extend: {
      colors: {
        background: '#050505',
        card: '#111111',
        border: '#262626',
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
}