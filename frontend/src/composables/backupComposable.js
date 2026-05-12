import { useQuery, useQueryClient, useMutation } from "@tanstack/vue-query";
import apiClient from "./apiClient";
import { useMainStore } from "@/stores/main";

async function handleApiError(error, message) {
  if (error.response?.status === 401) throw error;
  const mainstore = useMainStore();
  if (error.response) {
    console.error("Response error:", error.response.data);
  } else if (error.request) {
    console.error("No response received:", error.request);
  } else {
    console.error("Error during request setup:", error.message);
  }
  mainstore.showSnackbar(message + " : " + (error.response?.data?.detail ?? error.message), "error");
  throw error;
}

async function getBackupConfigFunction() {
  try {
    const response = await apiClient.get("/administration/backups/config");
    return response.data;
  } catch (error) {
    return await handleApiError(error, "Failed to load backup config");
  }
}

async function updateBackupConfigFunction(data) {
  try {
    const response = await apiClient.patch("/administration/backups/config", data);
    return response.data;
  } catch (error) {
    return await handleApiError(error, "Failed to update backup config");
  }
}

async function listBackupsFunction() {
  try {
    const response = await apiClient.get("/administration/backups/files");
    return response.data;
  } catch (error) {
    return await handleApiError(error, "Failed to list backups");
  }
}

async function runBackupFunction() {
  try {
    const response = await apiClient.post("/administration/backups/run");
    return response.data;
  } catch (error) {
    return await handleApiError(error, "Failed to trigger backup");
  }
}

async function deleteBackupFunction(filename) {
  try {
    const response = await apiClient.delete(`/administration/backups/files/${encodeURIComponent(filename)}`);
    return response.data;
  } catch (error) {
    return await handleApiError(error, "Failed to delete backup");
  }
}

async function restoreDatabaseFunction(filename) {
  try {
    const response = await apiClient.post(`/administration/backups/restore/database?filename=${encodeURIComponent(filename)}`);
    return response.data;
  } catch (error) {
    return await handleApiError(error, "Failed to restore database");
  }
}

async function restoreFromUploadFunction(file) {
  try {
    const formData = new FormData();
    formData.append("file", file);
    const response = await apiClient.post("/administration/backups/restore/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  } catch (error) {
    return await handleApiError(error, "Failed to restore from upload");
  }
}

export function useBackupConfig() {
  const queryClient = useQueryClient();
  const mainstore = useMainStore();

  const { data: backupConfig, isLoading } = useQuery({
    queryKey: ["backup_config"],
    queryFn: getBackupConfigFunction,
  });

  const updateMutation = useMutation({
    mutationFn: updateBackupConfigFunction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["backup_config"] });
      mainstore.showSnackbar("Backup settings saved", "success");
    },
  });

  function editBackupConfig(data) {
    updateMutation.mutate(data);
  }

  return { backupConfig, isLoading, editBackupConfig };
}

export function useBackupFiles() {
  const queryClient = useQueryClient();
  const mainstore = useMainStore();

  const { data: backupFiles, isLoading, refetch } = useQuery({
    queryKey: ["backup_files"],
    queryFn: listBackupsFunction,
  });

  const runBackupMutation = useMutation({
    mutationFn: runBackupFunction,
    onSuccess: () => {
      mainstore.showSnackbar("Backup queued — it will appear in the list shortly", "success");
      setTimeout(() => queryClient.invalidateQueries({ queryKey: ["backup_files"] }), 3000);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteBackupFunction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["backup_files"] });
      mainstore.showSnackbar("Backup deleted", "success");
    },
  });

  const restoreMutation = useMutation({
    mutationFn: restoreDatabaseFunction,
    onSuccess: () => {
      mainstore.showSnackbar("Database restored successfully", "success");
    },
  });

  const restoreUploadMutation = useMutation({
    mutationFn: restoreFromUploadFunction,
    onSuccess: () => {
      mainstore.showSnackbar("Database restored from uploaded file", "success");
    },
  });

  function runBackup() {
    runBackupMutation.mutate();
  }

  function deleteBackup(filename) {
    deleteMutation.mutate(filename);
  }

  function restoreDatabase(filename) {
    restoreMutation.mutate(filename);
  }

  function restoreFromUpload(file) {
    restoreUploadMutation.mutate(file);
  }

  return {
    backupFiles,
    isLoading,
    refetch,
    runBackup,
    deleteBackup,
    restoreDatabase,
    restoreFromUpload,
    isRestoring: restoreMutation.isPending || restoreUploadMutation.isPending,
  };
}

export function downloadBackup(filename) {
  window.location.href = `/api/v1/administration/backups/files/${encodeURIComponent(filename)}/download`;
}
