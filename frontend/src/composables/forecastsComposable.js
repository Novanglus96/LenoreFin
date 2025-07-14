import { useQuery, useQueryClient } from "@tanstack/vue-query";
import axios from "axios";
import { useMainStore } from "@/stores/main";

const apiClient = axios.create({
  baseURL: "/api/v1",
  withCredentials: false,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
    Authorization: `Bearer ${
      window.VITE_API_KEY === "__VITE_API_KEY__"
        ? import.meta.env.VITE_API_KEY // Fallback to the environment variable if the value is the default placeholder
        : window.VITE_API_KEY // Otherwise, use the value in window.VITE_API_KEY
    }`,
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

async function getAccountForecastFunction(
  account_id,
  start_integer,
  end_integer,
) {
  try {
    const response = await apiClient.get(
      "/accounts/forecast/get/" +
        account_id +
        "?start_interval=" +
        start_integer +
        "&end_interval=" +
        end_integer,
    );
    return response.data;
  } catch (error) {
    handleApiError(error, "Account forecast not fetched: ");
  }
}

export function useAccountForecasts(account_id, start_integer, end_integer) {
  const queryClient = useQueryClient();
  const {
    data: account_forecast,
    isLoading,
    isFetching,
  } = useQuery({
    queryKey: ["account_forecast", { account: account_id }],
    queryFn: () =>
      getAccountForecastFunction(account_id, start_integer, end_integer),
    select: response => response,
    client: queryClient,
  });

  return {
    isLoading,
    isFetching,
    account_forecast,
  };
}
