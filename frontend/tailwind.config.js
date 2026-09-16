import animate from "tailwindcss-animate";

/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Paleta alinhada ao design de referência (NobreLOG_HTML_CSS)
        brand: { DEFAULT: "#ffc400", 100: "#fff4c8", 400: "#ffc400", 500: "#eab308" },
        ink: "#11141a",
        muted: "#667085",
        line: "#e4e7ec",
        surface: "#f3f5f7",
        ok: "#18b96b",
        danger: "#e5484d",
      },
      fontFamily: { sans: ["Inter", "system-ui", "sans-serif"] },
      maxWidth: { content: "1660px" },
      borderRadius: { xl: "14px", "2xl": "18px" },
      boxShadow: { card: "0 10px 28px rgba(18,24,33,.06)" },
      keyframes: {
        "fade-up": { from: { opacity: "0", transform: "translateY(8px)" }, to: { opacity: "1", transform: "translateY(0)" } },
        shimmer: { "100%": { transform: "translateX(100%)" } },
      },
      animation: { "fade-up": "fade-up .4s ease both" },
    },
  },
  plugins: [animate],
};
