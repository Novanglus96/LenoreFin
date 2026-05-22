import { useQuery, useQueryClient, useMutation } from "@tanstack/vue-query";
import apiClient from "./apiClient";
import { useMainStore } from "@/stores/main";

async function handleApiError(error, message) {
  if (error.response?.status === 401) throw error;
  const mainstore = useMainStore();
  const backendHealthy = await isBackendHealthy();

  if (!backendHealthy) {
    console.warn("Backend is not healthy. Suppressing error.");
    return null; // or return undefined
  }
  if (error.response) {
    console.error("Response error:", error.response.data);
    console.error("Status code:", error.response.status);
    console.error("Headers", error.response.headers);
  } else if (error.request) {
    console.error("No response received:", error.request);
  } else {
    console.error("Error during request setup:", error.message);
  }
  mainstore.showSnackbar(message + " : " + error.response.data.detail, "error");
  throw error;
}

async function getOptionsFunction() {
  try {
    const response = await apiClient.get("/administration/options/get/1");
    return response.data;
  } catch (error) {
    return await handleApiError(error, "Options not fetched: ");
  }
}

async function updateOptionsFunction(updatedOptions) {
  try {
    const response = await apiClient.patch(
      "/administration/options/update/1",
      updatedOptions,
    );
    return response.data;
  } catch (error) {
    return await handleApiError(error, "Options not updated: ");
  }
}

export function useOptions() {
  const queryClient = useQueryClient();
  const {
    data: options,
    isLoading,
    isFetched,
  } = useQuery({
    queryKey: ["options"],
    queryFn: () => getOptionsFunction(),
    select: response => response,
    client: queryClient,
  });

  const prefetchOptions = async () => {
    await queryClient.prefetchQuery({
      queryKey: ["options"],
      queryFn: () => getOptionsFunction(),
    });
  };

  const updateOptionsMutation = useMutation({
    mutationFn: updateOptionsFunction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["options"] });
      queryClient.invalidateQueries({ queryKey: ["tag_graph"] });
      queryClient.invalidateQueries({ queryKey: ["tag_graph_items"] });
      queryClient.invalidateQueries({ queryKey: ["retirement_forecast"] });
      queryClient.invalidateQueries({ queryKey: ["expense_graph"] });
    },
  });

  async function editOptions(updatedOptions) {
    updateOptionsMutation.mutate(updatedOptions);
  }

  return {
    isLoading,
    options,
    editOptions,
    isFetched,
    prefetchOptions,
  };
}

async function isBackendHealthy() {
  try {
    const response = await apiClient.get("/administration/health/");
    return response?.data?.status === "ok";
  } catch (e) {
    return false;
  }
}
