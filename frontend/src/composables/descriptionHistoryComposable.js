import { useQuery, useQueryClient } from "@tanstack/vue-query";
import axios from "axios";
import { useMainStore } from "@/stores/main";
import { useApiKey } from "./ueApiKey";

const apiKey = useApiKey();

const apiClient = axios.create({
  baseURL: "/api/v1",
  withCredentials: false,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
    Authorization: `Bearer ${apiKey}`,
  },
});

function handleApiError(error, message) {
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

async function getDescriptionHistoryFunction() {
  try {
    const response = await apiClient.get(
      "/administration/description-histories/list",
    );
    return response.data;
  } catch (error) {
    handleApiError(error, "Description Histories not fetched: ");
  }
}

export function useDescriptionHistory() {
  const queryClient = useQueryClient();
  const { data: descriptionHistory, isLoading } = useQuery({
    queryKey: ["description-history"],
    queryFn: () => getDescriptionHistoryFunction(),
    select: response => response,
    client: queryClient,
  });

  return {
    isLoading,
    descriptionHistory,
  };
}
