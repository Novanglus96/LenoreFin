import { useQuery, useQueryClient } from "@tanstack/vue-query";
import axios from "axios";
import { useMainStore } from "@/stores/main";

const apiClient = axios.create({
  baseURL: "/api/v1",
  withCredentials: false,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
    Authorization:
      "Bearer sVruPBzWnGEDrLb7JjfVNrs9wk8LtgnDQef6iXDXc4bWMUk3XFcsCtEgT8dKzhJd", //TODO: Pull API_KEY from somewhere secure
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
  mainstore.showSnackbar(message + "Error #" + error.response.status, "error");
  throw error;
}

async function getLogEntriesFunction() {
  try {
    const response = await apiClient.get("/administration/log-entries/list");
    return response.data;
  } catch (error) {
    handleApiError(error, "Log entries not fetched: ");
  }
}

export function useLogEntries() {
  const queryClient = useQueryClient();
  const { data: log_entries, isLoading } = useQuery({
    queryKey: ["log_entries"],
    queryFn: () => getLogEntriesFunction(),
    select: response => response,
    client: queryClient,
  });

  return {
    isLoading,
    log_entries,
  };
}
