/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        void: "#05080F",
        surface: "#0A1220",
        "surface-2": "#101C30",
        line: "#1C2C46",
        text: "#E9F1FB",
        muted: "#8BA2BD",
        brand: "#22D3EE",
        "brand-2": "#3B82F6",
        violet: "#A78BFA",
        success: "#34D399",
        warning: "#FBBF24",
        danger: "#F87171",
        critical: "#FB7185",
      },
      fontFamily: {
        sans: [
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "Helvetica Neue",
          "Arial",
          "sans-serif",
        ],
        mono: [
          "JetBrains Mono",
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "Consolas",
          "Liberation Mono",
          "monospace",
        ],
      },
      boxShadow: {
        panel: "0 24px 80px -24px rgba(0, 0, 0, 0.85)",
        glow: "0 0 0 1px rgba(34, 211, 238, 0.14), 0 18px 60px -24px rgba(34, 211, 238, 0.32)",
      },
      backgroundImage: {
        "brand-line":
          "linear-gradient(90deg, transparent, rgba(34,211,238,0.55), rgba(167,139,250,0.35), transparent)",
      },
      keyframes: {
        rise: {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        breathe: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.45" },
        },
      },
      animation: {
        rise: "rise 520ms cubic-bezier(0.22, 1, 0.36, 1) both",
        breathe: "breathe 2.8s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
