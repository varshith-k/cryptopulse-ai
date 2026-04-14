import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#09111f",
        panel: "#10213b",
        "panel-deep": "#0c182d",
        accent: "#2dd4bf",
        signal: "#f97316",
      },
      boxShadow: {
        glow: "0 18px 60px rgba(45, 212, 191, 0.18)",
        "glow-soft": "0 10px 40px rgba(45, 212, 191, 0.12)",
        panel: "0 24px 60px rgba(3, 7, 18, 0.35)",
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        body: ["'Manrope'", "sans-serif"],
      },
    },
  },
  plugins: [],
} satisfies Config;
