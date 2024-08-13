import { nextui } from "@nextui-org/theme";

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./node_modules/@nextui-org/theme/dist/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        pageColor: {
          light: "#006FEE",
          DEFAULT: "#006FEE",
          dark: "#99C7FB",
        },
        interactionColor: {
          light: "#7828C8",
          DEFAULT: "#7828C8",
          dark: "#C9A9E9",
        },
        apiColor: {
          light: "#F31260",
          DEFAULT: "#F31260",
          dark: "#FAA0BF",
        },
      },
    },
  },
  darkMode: "class",
  plugins: [nextui()],
};
