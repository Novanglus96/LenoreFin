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

async function getExpenseGraphFunction() {
  try {
    const response = await apiClient.get(
      "/planning/graph/list?graph_type=expense",
    );
    return response.data;
  } catch (error) {
    handleApiError(error, "Expense graph not fetched: ");
  }
}

async function getPayGraphFunction() {
  try {
    const response = await apiClient.get("/planning/graph/list?graph_type=pay");
    return response.data;
  } catch (error) {
    handleApiError(error, "Pay graph not fetched: ");
  }
}

export function useExpenseGraph() {
  const queryClient = useQueryClient();
  const { data: expense_graph, isLoading } = useQuery({
    queryKey: ["expense_graph"],
    queryFn: () => getExpenseGraphFunction(),
    select: response => response,
    client: queryClient,
  });

  return {
    isLoading,
    expense_graph,
  };
}

export function usePayGraph() {
  const queryClient = useQueryClient();
  const { data: pay_graph, isLoading } = useQuery({
    queryKey: ["pay_graph"],
    queryFn: () => getPayGraphFunction(),
    select: response => response,
    client: queryClient,
  });

  return {
    isLoading,
    pay_graph,
  };
}
