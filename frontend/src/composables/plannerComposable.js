import { useQuery, useQueryClient, useMutation } from "@tanstack/vue-query";
import { unref } from "vue";
import apiClient from "./apiClient";
import { useMainStore } from "@/stores/main";

function handleApiError(error, message) {
  if (error.response?.status === 401) throw error;
  const mainstore = useMainStore();
  if (error.response) {
    console.error("Response error:", error.response.data);
    console.error("Status code:", error.response.status);
  } else if (error.request) {
    console.error("No response received:", error.request);
  } else {
    console.error("Error during request setup:", error.message);
  }
  mainstore.showSnackbar(
    message + " : " + (error.response?.data?.detail ?? error.message),
    "error",
  );
  throw error;
}

async function getPlannerAnalysisFunction(months, horizonMonths, incomeAdjustment) {
  try {
    const response = await apiClient.get("/planning/planner/analysis", {
      params: {
        months,
        horizon_months: horizonMonths,
        income_adjustment: incomeAdjustment,
      },
    });
    return response.data;
  } catch (error) {
    handleApiError(error, "Planner analysis not fetched");
  }
}

async function getPlannerProjectionFunction(contributionId, months) {
  try {
    const response = await apiClient.get(
      "/planning/planner/projection/" + contributionId,
      { params: { months } },
    );
    return response.data;
  } catch (error) {
    handleApiError(error, "Projection not fetched");
  }
}

async function applySuggestionsFunction(contributionIds) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.post("/planning/planner/apply", {
      contribution_ids: contributionIds,
    });
    const { applied_count: applied, results } = response.data;
    const skipped = results.filter(r => !r.applied);
    if (applied === 0) {
      // Every row bounced — say why rather than claiming success.
      mainstore.showSnackbar(
        skipped[0]?.reason ?? "Nothing was applied.",
        "warning",
      );
    } else if (skipped.length > 0) {
      mainstore.showSnackbar(
        `Applied ${applied}; skipped ${skipped.length} (${skipped[0].reason})`,
        "warning",
      );
    } else {
      mainstore.showSnackbar(
        `Applied ${applied} contribution${applied === 1 ? "" : "s"}!`,
        "success",
      );
    }
    return response.data;
  } catch (error) {
    handleApiError(error, "Suggestions not applied");
  }
}

export function usePlanner(months, horizonMonths, incomeAdjustment) {
  const queryClient = useQueryClient();

  const {
    data: planner,
    isLoading,
    isFetching,
  } = useQuery({
    queryKey: ["planner", months, horizonMonths, incomeAdjustment],
    queryFn: () =>
      getPlannerAnalysisFunction(
        unref(months),
        unref(horizonMonths),
        unref(incomeAdjustment),
      ),
    select: response => response,
    client: queryClient,
  });

  const applyMutation = useMutation({
    mutationFn: applySuggestionsFunction,
    onSuccess: () => {
      // Applying moves both the contribution and its reminder, so everything
      // downstream of either is now stale.
      queryClient.invalidateQueries({ queryKey: ["planner"] });
      queryClient.invalidateQueries({ queryKey: ["contributions"] });
      queryClient.invalidateQueries({ queryKey: ["reminders"] });
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["accounts"] });
    },
  });

  async function applySuggestions(contributionIds) {
    return applyMutation.mutateAsync(contributionIds);
  }

  return {
    planner,
    isLoading,
    isFetching,
    isApplying: applyMutation.isPending,
    applySuggestions,
  };
}

export function usePlannerProjection(contributionId, months) {
  const queryClient = useQueryClient();
  const { data: projection, isLoading } = useQuery({
    queryKey: ["plannerProjection", contributionId, months],
    queryFn: () =>
      getPlannerProjectionFunction(unref(contributionId), unref(months)),
    enabled: () => Boolean(unref(contributionId)),
    select: response => response,
    client: queryClient,
  });

  return { projection, isLoading };
}
