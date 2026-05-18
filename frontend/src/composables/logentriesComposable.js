import { useQuery, useQueryClient } from "@tanstack/vue-query";
import apiClient from "./apiClient";
import { useMainStore } from "@/stores/main";

function handleApiError(error, message) {
  if (error.response?.status === 401) throw error;
  const mainstore = useMainStore();
  mainstore.showSnackbar(message + " : " + (error.response?.data?.detail ?? error.message), "error");
  throw error;
}

async function getLogsFunction({ logType = "error", page = 1, pageSize = 100, level = null, search = null } = {}) {
  try {
    const params = { log_type: logType, page, page_size: pageSize };
    if (level) params.level = level;
    if (search) params.search = search;
    const response = await apiClient.get("/administration/logs", { params });
    return response.data;
  } catch (error) {
    return handleApiError(error, "Failed to load logs");
  }
}

export function useLogs({ logType, page, pageSize, level, search } = {}) {
  const queryClient = useQueryClient();
  const { data: logPage, isLoading, refetch } = useQuery({
    queryKey: ["logs", logType, page, pageSize, level, search],
    queryFn: () =>
      getLogsFunction({
        logType: logType?.value ?? logType ?? "error",
        page: page?.value ?? page ?? 1,
        pageSize: pageSize?.value ?? pageSize ?? 100,
        level: level?.value ?? level ?? null,
        search: search?.value ?? search ?? null,
      }),
    client: queryClient,
  });

  return { logPage, isLoading, refetch };
}

export async function downloadLogBundle() {
  try {
    const response = await apiClient.get("/administration/logs/bundle", {
      responseType: "blob",
    });
    const url = URL.createObjectURL(response.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = "lenore_logs.zip";
    a.click();
    URL.revokeObjectURL(url);
  } catch (error) {
    const mainstore = useMainStore();
    mainstore.showSnackbar("Failed to download log bundle", "error");
  }
}
