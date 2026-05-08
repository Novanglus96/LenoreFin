import { defineStore } from "pinia";
import { ref, computed } from "vue";
import axios from "axios";

const apiClient = axios.create({
  baseURL: "/api/v1",
  withCredentials: true,
  headers: { Accept: "application/json", "Content-Type": "application/json" },
});

export const useAuthStore = defineStore("auth", () => {
  const user = ref(null);

  const isAuthenticated = computed(() => user.value !== null);
  const isFullAccess = computed(() => user.value?.group === "full_access");
  const isReadonly = computed(() => user.value?.group === "readonly");

  async function fetchCurrentUser() {
    try {
      const response = await apiClient.get("/auth/me");
      user.value = response.data;
    } catch {
      user.value = null;
    }
  }

  async function login(username, password) {
    const response = await apiClient.post("/auth/login", { username, password });
    user.value = response.data;
  }

  async function logout() {
    try {
      await apiClient.post("/auth/logout");
    } catch {
      // session may already be expired; clear local state regardless
    } finally {
      user.value = null;
    }
  }

  return { user, isAuthenticated, isFullAccess, isReadonly, fetchCurrentUser, login, logout };
});
