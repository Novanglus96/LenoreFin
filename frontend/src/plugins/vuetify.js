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
    primary: "#06966A",
    secondary: "#ECFDF5",
    accent: "#FF5900",
    error: "#FF3407",
    warning: "#ffc107",
    info: "#795548",
    success: "#4caf50",
    selected: "#7fb17f",
    surface: "#FFFFFF",
    background: "#F5F5F5",
    "on-background": "#212121",
    "on-surface": "#212121",
  },
};

const myCustomDarkTheme = {
  dark: true,
  colors: {
    primary: "#0D1B1E",
    secondary: "#4ADEB3",
    accent: "#FF784E",
    error: "#CF6679",
    warning: "#FB8C00",
    info: "#2196F3",
    success: "#4CAF50",
    selected: "#A5D6A7",
    surface: "#212121",
    background: "#121212",
    "on-background": "#ffffff",
    "on-surface": "#ffffff",
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
