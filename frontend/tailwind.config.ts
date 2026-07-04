import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        card: "var(--card)",
        ink: "var(--foreground)",
        "ink-soft": "var(--ink-soft)",
        muted: "var(--muted)",
        faint: "var(--faint)",
        line: "var(--line)",
        "line-strong": "var(--line-strong)",
        // Semantic status — the only colour in the system, chips only.
        status: {
          new: "#4b5563",
          newbg: "#eeeef0",
          prog: "#a65a0b",
          progbg: "#fbeed4",
          done: "#067a54",
          donebg: "#e0f4eb",
          over: "#c7362b",
          overbg: "#fbe6e3",
        },
      },
      borderRadius: {
        card: "14px",
        ctrl: "9px",
      },
      boxShadow: {
        soft: "0 1px 2px rgba(20,21,26,.05), 0 14px 36px -14px rgba(20,21,26,.13)",
        "soft-sm":
          "0 1px 2px rgba(20,21,26,.06), 0 6px 16px -10px rgba(20,21,26,.12)",
      },
      fontFamily: {
        sans: [
          "ui-sans-serif",
          "-apple-system",
          "BlinkMacSystemFont",
          '"SF Pro Text"',
          '"Helvetica Neue"',
          "system-ui",
          "sans-serif",
        ],
      },
    },
  },
  plugins: [],
};
export default config;
