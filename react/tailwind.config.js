/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./public/index.html",
    "./src/**/*.{js,jsx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: "#111111",
          light: "#222222",
          dim: "#6b7280"
        }
      },
      boxShadow: {
        subtle: "0 1px 2px rgb(0 0 0 / 0.06)"
      }
    },
    fontFamily: {
      sans: [
        "ui-sans-serif",
        "system-ui",
        "-apple-system",
        "BlinkMacSystemFont",
        "Segoe UI",
        "Roboto",
        "Ubuntu",
        "Cantarell",
        "Noto Sans",
        "Helvetica Neue",
        "Arial",
        "sans-serif",
        "Apple Color Emoji",
        "Segoe UI Emoji"
      ]
    }
  },
  plugins: []
};
