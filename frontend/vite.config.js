import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { createHtmlPlugin } from "vite-plugin-html";
import vueDevTools from "vite-plugin-vue-devtools";
import { fileURLToPath, URL } from "node:url";
import eslint from "vite-plugin-eslint";
import pkg from "./package.json";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
    VitePWA({
      strategies: "injectManifest",
      srcDir: "src",
      filename: "sw.js",
      registerType: "autoUpdate",
      includeAssets: ["favicon.ico", "logov2.png", "apple-touch-icon.png"],
      manifest: {
        name: "LenoreFin",
        short_name: "LenoreFin",
        description: "Personal finance tracking",
        theme_color: "#06966a",
        background_color: "#121212",
        display: "standalone",
        start_url: "/",
        icons: [
          { src: "android-chrome-192x192.png", sizes: "192x192", type: "image/png" },
          { src: "android-chrome-512x512.png", sizes: "512x512", type: "image/png" },
          { src: "android-chrome-512x512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
        ],
      },
      injectManifest: {
        maximumFileSizeToCacheInBytes: 3 * 1024 * 1024,
      },
    }),
    createHtmlPlugin({
      inject: {
        data: {
          title: "LenoreFin",
        },
      },
    }),
    eslint(),
  ],
  server: {
    proxy: {
      "/api": {
        target: "https://back-dev.danielleandjohn.love/api", // Backend API server
        changeOrigin: true,
        rewrite: path => path.replace(/^\/api/, ""),
      },
      "/media": {
        target: "https://back-dev.danielleandjohn.love", // Serve media files from backend in dev
        changeOrigin: true,
      },
      "/ws": {
        target: "wss://back-dev.danielleandjohn.love",
        changeOrigin: true,
        ws: true,
      },
    },
  },
  define: {
    __VUE_OPTIONS_API__: true,
    __VUE_PROD_DEVTOOLS__: false,
    __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false,
    "import.meta.env.VITE_APP_VERSION": JSON.stringify(pkg.version),
    __OPT_FEATURES__: process.env.VITE_OPT_FEATURES === "true",
  },
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
});
