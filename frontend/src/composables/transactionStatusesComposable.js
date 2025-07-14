import { useQuery, useQueryClient } from "@tanstack/vue-query";
import axios from "axios";
import { useMainStore } from "@/stores/main";

const apiClient = axios.create({
  baseURL: "/api/v1",
  withCredentials: false,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
    Authorization: `Bearer ${window.__APP_CONFIG__?.VITE_API_KEY}`,
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

async function getTransactionStatusesFunction() {
  try {
    const response = await apiClient.get(
      "/transactions/transaction-statuses/list",
    );
    return response.data;
  } catch (error) {
    handleApiError(error, "Transaction statuses not fetched: ");
  }
}

export function useTransactionStatuses() {
  const queryClient = useQueryClient();
  const { data: transaction_statuses, isLoading } = useQuery({
    queryKey: ["transaction_statuses"],
    queryFn: () => getTransactionStatusesFunction(),
    select: response => response,
    client: queryClient,
  });

  return {
    isLoading,
    transaction_statuses,
  };
}
