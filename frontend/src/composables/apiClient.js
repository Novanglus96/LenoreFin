import axios from "axios";
import router from "@/router";

const apiClient = axios.create({
  baseURL: "/api/v1",
  withCredentials: true,
  headers: { Accept: "application/json", "Content-Type": "application/json" },
});

apiClient.interceptors.response.use(
  response => response,
  error => {
    const is401 = error.response?.status === 401;
    const isAuthCheck = error.config?.url?.includes("/auth/me");
    const alreadyOnLogin = router.currentRoute.value.name === "login";

    if (is401 && !isAuthCheck && !alreadyOnLogin) {
      const currentPath = router.currentRoute.value.fullPath;
      router.push({ name: "login", query: { redirect: currentPath } });
    }
    return Promise.reject(error);
  },
);

export default apiClient;
