import type { Config } from "tailwindcss"

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        mkc: {
          rust:        "#C1440E",
          terracotta:  "#D4622A",
          clay:        "#E8854A",
          sand:        "#F5C98A",
          cream:       "#FDF4E7",
          warm:        "#FAE8D0",
          ochre:       "#B8860B",
          saffron:     "#E8A020",
          rose:        "#C17B6A",
          dark:        "#2C1A0E",
          mid:         "#5C3320",
          muted:       "#9A6B55",
          border:      "#E8C4A8",
          surface:     "#FDF8F2",
        },
      },
    },
  },
  plugins: [],
}

export default config