import { useQuery, useQueryClient, useMutation } from "@tanstack/vue-query";
import apiClient from "./apiClient";
import { useMainStore } from "@/stores/main";

async function handleApiError(error, message) {
  if (error.response?.status === 401) throw error;
  const mainstore = useMainStore();
  mainstore.showSnackbar(message + " : " + (error.response?.data?.detail ?? error.message), "error");
  throw error;
}

async function listDetectionsFunction() {
  try {
    const response = await apiClient.get("/planning/detected-recurring");
    return response.data;
  } catch (error) {
    return await handleApiError(error, "Failed to load detections");
  }
}

async function ignoreDetectionFunction(id) {
  try {
    const response = await apiClient.post(`/planning/detected-recurring/${id}/ignore`);
    return response.data;
  } catch (error) {
    return await handleApiError(error, "Failed to ignore detection");
  }
}

async function deleteDetectionFunction(id) {
  try {
    const response = await apiClient.delete(`/planning/detected-recurring/${id}`);
    return response.data;
  } catch (error) {
    return await handleApiError(error, "Failed to delete detection");
  }
}

export function useDetections() {
  const queryClient = useQueryClient();

  const { data: detections, isLoading, isFetching } = useQuery({
    queryKey: ["detected_recurring"],
    queryFn: listDetectionsFunction,
  });

  const ignoreMutation = useMutation({
    mutationFn: ignoreDetectionFunction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["detected_recurring"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteDetectionFunction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["detected_recurring"] });
    },
  });

  function ignoreDetection(id) {
    ignoreMutation.mutate(id);
  }

  function deleteDetection(id) {
    deleteMutation.mutate(id);
  }

  return {
    detections,
    isLoading,
    isFetching,
    ignoreDetection,
    deleteDetection,
  };
}
