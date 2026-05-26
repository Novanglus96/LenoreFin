import { useQuery, useQueryClient, useMutation } from "@tanstack/vue-query";
import { computed } from "vue";
import apiClient from "./apiClient";
import { useMainStore } from "@/stores/main";

export const DEFAULT_LAYOUT = [
  { id: "graphs", visible: true },
  { id: "budgets", visible: true },
  { id: "reminders", visible: true },
  { id: "transactions", visible: true },
];

export const DEFAULT_GRAPH_WIDGETS = [
  { widget_id: 1, graph_name: "Expenses", type_id: 1, tag_id: null, month: 0, exclude: "[0]" },
  { widget_id: 2, graph_name: "Income", type_id: 2, tag_id: null, month: 0, exclude: "[0]" },
  { widget_id: 3, graph_name: "Untagged", type_id: 3, tag_id: null, month: 0, exclude: "[0]" },
];

async function getDashboardConfigFunction() {
  try {
    const response = await apiClient.get("/administration/dashboard-config/");
    return response.data;
  } catch {
    return { layout: DEFAULT_LAYOUT, graph_widgets: DEFAULT_GRAPH_WIDGETS };
  }
}

async function updateDashboardConfigFunction(payload) {
  const response = await apiClient.patch("/administration/dashboard-config/", payload);
  return response.data;
}

export function useDashboardConfig() {
  const queryClient = useQueryClient();

  const { data: dashboardConfig, isLoading } = useQuery({
    queryKey: ["dashboard_config"],
    queryFn: getDashboardConfigFunction,
    select: response => response,
    placeholderData: { layout: DEFAULT_LAYOUT, graph_widgets: DEFAULT_GRAPH_WIDGETS },
  });

  const updateConfigMutation = useMutation({
    mutationFn: updateDashboardConfigFunction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard_config"] });
      queryClient.invalidateQueries({ queryKey: ["tag_graph_items"] });
    },
    onError: () => {
      const mainstore = useMainStore();
      mainstore.showSnackbar("Widget config not saved", "error");
    },
  });

  const graphWidgets = computed(
    () => dashboardConfig.value?.graph_widgets ?? DEFAULT_GRAPH_WIDGETS,
  );

  function saveLayout(layout) {
    updateConfigMutation.mutate({ layout });
  }

  function saveGraphWidget(widgetId, widgetConfig) {
    const current = graphWidgets.value.map(w =>
      w.widget_id === widgetId ? { ...w, ...widgetConfig, widget_id: widgetId } : w,
    );
    updateConfigMutation.mutate({ graph_widgets: current });
  }

  return { dashboardConfig, isLoading, saveLayout, saveGraphWidget, graphWidgets, DEFAULT_LAYOUT, DEFAULT_GRAPH_WIDGETS };
}
