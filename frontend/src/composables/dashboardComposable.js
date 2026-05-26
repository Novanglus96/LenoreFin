import { useQuery, useQueryClient, useMutation } from "@tanstack/vue-query";
import apiClient from "./apiClient";
import { useMainStore } from "@/stores/main";

const DEFAULT_LAYOUT = [
  { id: "graphs", visible: true },
  { id: "budgets", visible: true },
  { id: "reminders", visible: true },
  { id: "transactions", visible: true },
];

async function getDashboardConfigFunction() {
  try {
    const response = await apiClient.get("/administration/dashboard-config/");
    return response.data;
  } catch {
    return { layout: DEFAULT_LAYOUT };
  }
}

async function updateDashboardConfigFunction(layout) {
  const response = await apiClient.patch("/administration/dashboard-config/", {
    layout,
  });
  return response.data;
}

export function useDashboardConfig() {
  const queryClient = useQueryClient();

  const { data: dashboardConfig, isLoading } = useQuery({
    queryKey: ["dashboard_config"],
    queryFn: getDashboardConfigFunction,
    select: response => response,
    placeholderData: { layout: DEFAULT_LAYOUT },
  });

  const updateConfigMutation = useMutation({
    mutationFn: updateDashboardConfigFunction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard_config"] });
    },
    onError: () => {
      const mainstore = useMainStore();
      mainstore.showSnackbar("Widget config not saved", "error");
    },
  });

  function saveLayout(layout) {
    updateConfigMutation.mutate(layout);
  }

  return { dashboardConfig, isLoading, saveLayout, DEFAULT_LAYOUT };
}
