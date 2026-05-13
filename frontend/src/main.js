import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import piniaPluginPersistedState from "pinia-plugin-persistedstate";
import vuetify from "./plugins/vuetify";
import { loadFonts } from "./plugins/webfontloader";
import { VueQueryPlugin, QueryClient } from "@tanstack/vue-query";

loadFonts();

const pinia = createPinia();
pinia.use(piniaPluginPersistedState);
const app = createApp(App);

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
    },
  },
});

app.use(router);
app.use(pinia);
app.use(vuetify);
app.use(VueQueryPlugin, { queryClient });
app.mount("#app");

// If the browser restores a page from bfcache (back/forward navigation),
// re-validate the session so a logged-out user never sees stale content.
window.addEventListener("pageshow", async event => {
  if (event.persisted) {
    const { useAuthStore } = await import("@/stores/auth");
    const authStore = useAuthStore();
    await authStore.fetchCurrentUser();
    if (!authStore.isAuthenticated) {
      window.location.href = "/login";
    }
  }
});
