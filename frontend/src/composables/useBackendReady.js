// useBackendReady.js
import { ref, onMounted } from "vue";
import apiClient from "./apiClient";

const backendReady = ref(false);

export function useBackendReady() {
  onMounted(async () => {
    while (!backendReady.value) {
      try {
        const res = await apiClient.get("/administration/health/");

        if (res.status === 200) {
          backendReady.value = true;
        }
      } catch (err) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
  });

  return { backendReady };
}
