import { useQuery, useQueryClient, useMutation } from "@tanstack/vue-query";
import axios from "axios";
import { useMainStore } from "@/stores/main";

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

async function getLogEntriesFunction() {
  try {
    const response = await apiClient.get("/logentries");
    return response.data;
  } catch (error) {
    handleApiError(error, "Log entries not fetched: ");
  }
}

async function createLogEntryFunction(newLogEntry) {
  try {
    const response = await apiClient.post("/logentries", newLogEntry);
    return response.data;
  } catch (error) {
    handleApiError(error, "Log entry not created: ");
  }
}

export function useLogEntries() {
  const queryClient = useQueryClient();
  const { data: log_entries, isLoading } = useQuery({
    queryKey: ["log_entries"],
    queryFn: () => getLogEntriesFunction(),
    select: response => response,
    client: queryClient,
  });

  const createLogEntryMutation = useMutation({
    mutationFn: createLogEntryFunction,
    onSuccess: () => {
      console.log("Success adding log entry");
      queryClient.invalidateQueries({ queryKey: ["log_entries"] });
    },
  });

  async function addLogEntry(newLogEntry) {
    console.log(newLogEntry);
    createLogEntryMutation.mutate(newLogEntry);
  }

  return {
    isLoading,
    log_entries,
    addLogEntry,
  };
}

export async function logToDB(
  error,
  message,
  errorlevel,
  account_id,
  reminder_id,
  transaction_id,
) {
  let error_num = 0;
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, "0");
  const day = String(today.getDate()).padStart(2, "0");
  const formattedDate = `${year}-${month}-${day}`;
  if (error) {
    error_num = error.response.status;
  } else {
    error_num = null;
  }
  const logEntry = {
    log_date: formattedDate,
    log_entry: message,
    account_id: account_id,
    reminder_id: reminder_id,
    transaction_id: transaction_id,
    error_num: error_num,
    error_level_id: errorlevel,
  };
  const response = await apiClient.post("/logentries", logEntry);
  return response.data;
}
