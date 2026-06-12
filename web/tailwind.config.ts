import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#1B1B3D",
          ink: "#0E0E26",
          accent: "#3F3F8C",
          mist: "#F4F4FB",
        },
      },
      fontFamily: {
        sans: [
          "var(--font-lato)",
          "Lato",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Helvetica",
          "Arial",
          "sans-serif",
        ],
      },
    },
  },
  plugins: [],
};

export default config;
