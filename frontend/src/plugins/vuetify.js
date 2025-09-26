import "vuetify/styles";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import { aliases, mdi } from "vuetify/iconsets/mdi";
import "@mdi/font/css/materialdesignicons.css";
import { VDateInput } from "vuetify/labs/VDateInput"; // Import the lab component

const myCustomLightTheme = {
  dark: false,
  colors: {
    primary: "#ECFDF5",
    secondary: "#06966A",
    accent: "#FF5900",
    error: "#FF3407",
    warning: "#ffc107",
    info: "#795548",
    success: "#4caf50",
    selected: "#7fb17f",
    surface: "#ffffff",
  },
};

const myCustomDarkTheme = {
  dark: true,
  colors: {
    primary: "#0D1B1E", // very dark teal-gray (contrast with your light primary)
    secondary: "#4ADEB3", // brighter teal-green, keeps relation to light #06966A
    accent: "#FF784E", // warm accent, keeps energy of #FF5900 but better on dark
    error: "#FF6659", // softer red than #FF3407 for dark bg
    warning: "#FFD54F", // vivid amber for visibility
    info: "#BCAAA4", // muted brown-tan, complements dark surfaces
    success: "#81C784", // softer green for readability
    selected: "#A5D6A7", // lighter green tint for selected state
    surface: "#657383",
  },
};

export default createVuetify({
  theme: {
    defaultTheme: "myCustomLightTheme",
    variations: {
      colors: ["primary", "secondary", "accent"],
      lighten: 3,
      darken: 3,
    },
    themes: {
      myCustomLightTheme,
      myCustomDarkTheme,
    },
  },
  icons: {
    defaultSet: "mdi",
    aliases,
    sets: {
      mdi,
    },
  },
  components: {
    ...components, // Spread the default Vuetify components
    VDateInput, // Add the lab component
  },
  directives,
});
