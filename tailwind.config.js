/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './node_modules/preline/dist/*.js',
    "./node_modules/flowbite/**/*.js"
  ],
  theme: {
    colors: {
      darkbg: '#070F2B',
      purplish: '#9290C3'
    },
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('preline/plugin'),
    require('flowbite/plugin')({
      charts: true,
    }),
  ],
}
