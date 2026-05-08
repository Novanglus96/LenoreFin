import { useQuery, useQueryClient } from "@tanstack/vue-query";
import apiClient from "./apiClient";
import { useMainStore } from "@/stores/main";

function handleApiError(error, message) {
  if (error.response?.status === 401) throw error;
  const mainstore = useMainStore();
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

async function getTagTypesFunction() {
  try {
    const response = await apiClient.get("/tags/tag-types/list");
    return response.data;
  } catch (error) {
    handleApiError(error, "Tag types not fetched: ");
  }
}

export function useTagTypes() {
  const queryClient = useQueryClient();
  const { data: tag_types, isLoading } = useQuery({
    queryKey: ["tag_types"],
    queryFn: () => getTagTypesFunction(),
    select: response => response,
    client: queryClient,
  });

  return {
    isLoading,
    tag_types,
  };
}
