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

async function getRetirementForecastFunction() {
  try {
    const response = await apiClient.get("/planning/retirement/get");
    return response.data;
  } catch (error) {
    handleApiError(error, "Retirement forecast not fetched: ");
  }
}

async function getRetirementTransactionsFunction() {
  try {
    const response = await apiClient.get("/planning/retirement/transactions");
    return response.data;
  } catch (error) {
    handleApiError(error, "Retirement transactions not fetched: ");
  }
}

export function useRetirementForecast() {
  const queryClient = useQueryClient();
  const {
    data: retirement_forecast,
    isLoading,
    isFetching,
  } = useQuery({
    queryKey: ["retirement_forecast"],
    queryFn: () => getRetirementForecastFunction(),
    select: response => response,
    client: queryClient,
  });

  return {
    isLoading,
    isFetching,
    retirement_forecast,
  };
}

export function useRetirementTransactions() {
  const queryClient = useQueryClient();
  const { data: retirement_transactions, isLoading } = useQuery({
    queryKey: ["retirement_transactions"],
    queryFn: () => getRetirementTransactionsFunction(),
    select: response => response,
    client: queryClient,
  });

  return {
    retirement_transactions,
    isLoading,
  };
}
