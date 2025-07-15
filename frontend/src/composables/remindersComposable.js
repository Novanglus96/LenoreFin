import { useQuery, useQueryClient, useMutation } from "@tanstack/vue-query";
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

async function getRemindersFunction() {
  try {
    const response = await apiClient.get("/reminders/list");
    return response.data;
  } catch (error) {
    handleApiError(error, "Reminders not fetched: ");
  }
}

async function deleteReminderFunction(deletedReminder) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.delete(
      "/reminders/delete/" + deletedReminder,
    );
    mainstore.showSnackbar("Reminder deleted successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Reminder not deleted: ");
  }
}

async function createReminderFunction(newReminder) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.post("/reminders/create", newReminder);
    mainstore.showSnackbar("Reminder created successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Reminder not created: ");
  }
}

async function updateReminderFunction(updatedReminder) {
  try {
    const response = await apiClient.put(
      "/reminders/update/" + updatedReminder.id,
      updatedReminder,
    );
    return response.data;
  } catch (error) {
    handleApiError(error, "Reminder not updated: ");
  }
}

async function addReminderTrans(reminderTransObject) {
  try {
    const response = await apiClient.put(
      "/reminders/addtrans/" + reminderTransObject.reminder_id,
      reminderTransObject,
    );
    return response.data;
  } catch (error) {
    handleApiError(error, "Reminder transaction not added: ");
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

  const addReminderTransMutation = useMutation({
    mutationFn: addReminderTrans,
    onSuccess: () => {
      console.log("Success adding reminder transaction");
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

  async function addReminderTransaction(reminderTransObject) {
    addReminderTransMutation.mutate(reminderTransObject);
  }

  return {
    isLoading,
    reminders,
    removeReminder,
    addReminder,
    updateReminder,
    addReminderTransaction,
  };
}
