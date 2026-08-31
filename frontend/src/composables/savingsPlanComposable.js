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

async function getSavingsPlanFunction() {
  try {
    const response = await apiClient.get("/planning/savings-plan/get");
    return response.data;
  } catch (error) {
    handleApiError(error, "Savings plan not fetched: ");
  }
}

export function useSavingsPlan() {
  const queryClient = useQueryClient();

  // Keyed "planner" because contributions, reminders and transactions already
  // invalidate that key when they change — the plan is derived from all three,
  // and every one of them can move it.
  const { data: plan, isLoading } = useQuery({
    queryKey: ["planner"],
    queryFn: getSavingsPlanFunction,
    select: response => response,
    // The plan projects a year across every account, which takes a couple of
    // seconds. It is worth not re-running it every time the page is revisited;
    // the invalidations above are what keep it honest.
    staleTime: 5 * 60 * 1000,
    client: queryClient,
  });

  return { plan, isLoading };
}
