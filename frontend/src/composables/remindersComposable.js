import { useQuery, useQueryClient, useMutation } from "@tanstack/vue-query";
import axios from "axios";
import { useMainStore } from "@/stores/main";
import { logToDB } from "./logentriesComposable";

const apiClient = axios.create({
  baseURL: "/api/v1",
  withCredentials: false,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
    Authorization:
      "Bearer sVruPBzWnGEDrLb7JjfVNrs9wk8LtgnDQef6iXDXc4bWMUk3XFcsCtEgT8dKzhJd", //TODO: Pull API_KEY from somewhere secure
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
  mainstore.showSnackbar(message + "Error #" + error.response.status, "error");
  throw error;
}

async function getRemindersFunction() {
  try {
    const response = await apiClient.get("/reminders");
    logToDB(null, "Reminders fetched", 0, null, null, null);
    return response.data;
  } catch (error) {
    handleApiError(error, "Reminders not fetched: ");
    logToDB(error, "Reminders not fetched", 2, null, null, null);
  }
}

async function deleteReminderFunction(deletedReminder) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.delete("/reminders/" + deletedReminder);
    logToDB(null, "Reminder deleted", 1, null, deletedReminder, null);
    mainstore.showSnackbar("Reminder deleted successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Reminder not deleted: ");
    logToDB(error, "Reminder not deleted", 2, null, deletedReminder, null);
  }
}

async function createReminderFunction(newReminder) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.post("/reminders", newReminder);
    logToDB(null, "Reminder create", 1, null, newReminder, null);
    mainstore.showSnackbar("Reminder created successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Reminder not created: ");
    logToDB(error, "Reminder not created", 2, null, newReminder, null);
  }
}

async function updateReminderFunction(updatedReminder) {
  try {
    const response = await apiClient.put(
      "/reminders/" + updatedReminder.id,
      updatedReminder,
    );
    logToDB(null, "Reminder updated", 1, null, updatedReminder.id, null);
    return response.data;
  } catch (error) {
    handleApiError(error, "Reminder not updated: ");
    logToDB(error, "Reminder not updated", 2, null, updatedReminder.id, null);
  }
}

export function useReminders() {
  const queryClient = useQueryClient();
  const { data: reminders, isLoading } = useQuery({
    queryKey: ["reminders"],
    queryFn: () => getRemindersFunction(),
    select: response => response,
    client: queryClient,
  });

  const deleteReminderMutation = useMutation({
    mutationFn: deleteReminderFunction,
    onSuccess: () => {
      console.log("Success deleting reminder");
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["accounts"] });
      queryClient.invalidateQueries({ queryKey: ["account_forecast"] });
      queryClient.invalidateQueries({ queryKey: ["tag_graph"] });
      queryClient.invalidateQueries({ queryKey: ["reminders"] });
    },
  });

  const createReminderMutation = useMutation({
    mutationFn: createReminderFunction,
    onSuccess: () => {
      console.log("Success creating reminder");
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["accounts"] });
      queryClient.invalidateQueries({ queryKey: ["account_forecast"] });
      queryClient.invalidateQueries({ queryKey: ["tag_graph"] });
      queryClient.invalidateQueries({ queryKey: ["reminders"] });
    },
  });

  const updateReminderMutation = useMutation({
    mutationFn: updateReminderFunction,
    onSuccess: () => {
      console.log("Success updating reminder");
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["accounts"] });
      queryClient.invalidateQueries({ queryKey: ["account_forecast"] });
      queryClient.invalidateQueries({ queryKey: ["tag_graph"] });
      queryClient.invalidateQueries({ queryKey: ["reminders"] });
    },
  });

  async function removeReminder(deletedReminder) {
    deleteReminderMutation.mutate(deletedReminder);
  }

  async function addReminder(newReminder) {
    createReminderMutation.mutate(newReminder);
  }

  async function updateReminder(updatedReminder) {
    updateReminderMutation.mutate(updatedReminder);
  }

  return {
    isLoading,
    reminders,
    removeReminder,
    addReminder,
    updateReminder,
  };
}
