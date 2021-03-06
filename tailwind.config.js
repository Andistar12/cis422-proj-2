//console.log(process.env.NODE_ENV);
//const purge = process.env.NODE_ENV === 'production' ? true : false;
module.exports = {
  purge: {
    enabled: true,
    content: ['./templates/**/*.html']
  },
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {
      colors: {
        jade: '#01A66F',
        medium_aquamarine: "#75CE9F",
        madang: "#BDD99E",
        chardonnay: "#FFC06E",
        nav_grey: "#F6F6F6"
      }
    }
  },
  variants: {
    extend: {},
  },
  plugins: [],
}
