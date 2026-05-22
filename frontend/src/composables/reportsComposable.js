import { useQuery, useQueryClient, useMutation } from "@tanstack/vue-query";
import apiClient from "./apiClient";
import { useMainStore } from "@/stores/main";

async function handleApiError(error, message) {
  if (error.response?.status === 401) throw error;
  const mainstore = useMainStore();
  mainstore.showSnackbar(message + " : " + (error.response?.data?.detail ?? error.message), "error");
  throw error;
}

async function listReportsFunction() {
  try {
    const response = await apiClient.get("/reports");
    return response.data;
  } catch (error) {
    return await handleApiError(error, "Failed to load reports");
  }
}

async function createReportFunction(data) {
  try {
    const response = await apiClient.post("/reports", data);
    return response.data;
  } catch (error) {
    return await handleApiError(error, "Failed to save report");
  }
}

async function updateReportFunction({ id, data }) {
  try {
    const response = await apiClient.put(`/reports/${id}`, data);
    return response.data;
  } catch (error) {
    return await handleApiError(error, "Failed to update report");
  }
}

async function deleteReportFunction(id) {
  try {
    const response = await apiClient.delete(`/reports/${id}`);
    return response.data;
  } catch (error) {
    return await handleApiError(error, "Failed to delete report");
  }
}

async function runAdhocReportFunction(payload) {
  try {
    const response = await apiClient.post("/reports/run", payload);
    return response.data;
  } catch (error) {
    return await handleApiError(error, "Failed to run report");
  }
}

async function runSavedReportFunction(id) {
  try {
    const response = await apiClient.post(`/reports/${id}/run`);
    return response.data;
  } catch (error) {
    return await handleApiError(error, "Failed to run saved report");
  }
}

export function useReports() {
  const queryClient = useQueryClient();
  const mainstore = useMainStore();

  const { data: reports, isLoading, refetch } = useQuery({
    queryKey: ["reports"],
    queryFn: listReportsFunction,
  });

  const createMutation = useMutation({
    mutationFn: createReportFunction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reports"] });
      mainstore.showSnackbar("Report saved", "success");
    },
  });

  const updateMutation = useMutation({
    mutationFn: updateReportFunction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reports"] });
      mainstore.showSnackbar("Report updated", "success");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteReportFunction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reports"] });
      mainstore.showSnackbar("Report deleted", "success");
    },
  });

  const runMutation = useMutation({
    mutationFn: runAdhocReportFunction,
  });

  const runSavedMutation = useMutation({
    mutationFn: runSavedReportFunction,
  });

  function saveReport(data) {
    createMutation.mutate(data);
  }

  function updateReport(id, data) {
    updateMutation.mutate({ id, data });
  }

  function deleteReport(id) {
    deleteMutation.mutate(id);
  }

  async function runReport(payload) {
    return runMutation.mutateAsync(payload);
  }

  async function runSavedReport(id) {
    return runSavedMutation.mutateAsync(id);
  }

  return {
    reports,
    isLoading,
    refetch,
    saveReport,
    updateReport,
    deleteReport,
    runReport,
    runSavedReport,
    isSaving: createMutation.isPending || updateMutation.isPending,
    isRunning: runMutation.isPending || runSavedMutation.isPending,
  };
}
