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
