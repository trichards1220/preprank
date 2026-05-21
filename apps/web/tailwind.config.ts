import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        crimson: '#C22032',
        charcoal: '#1A1A1E',
        'steel-gray': '#6B7280',
        silver: '#C0C0C0',
      },
    },
  },
  plugins: [],
};
export default config;
