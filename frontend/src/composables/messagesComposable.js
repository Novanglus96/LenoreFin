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

async function getMessagesFunction() {
  try {
    const response = await apiClient.get("/messages");
    logToDB(null, "Messages fetched", 0, null, null, null);
    return response.data;
  } catch (error) {
    handleApiError(error, "Messages not fetched: ");
    logToDB(error, "Messages not fetched", 2, null, null, null);
  }
}

async function createMessageFunction(newMessage) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.post("/messages", newMessage);
    mainstore.showSnackbar("Message created successfully!", "success");
    logToDB(null, "Message created", 1, null, null, null);
    return response.data;
  } catch (error) {
    handleApiError(error, "Message not created: ");
    logToDB(error, "Message not created", 2, null, null, null);
  }
}

async function deleteAllMessagesFunction() {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.delete("/messages/deleteall/0");
    mainstore.showSnackbar("Messages deleted successfully!", "success");
    logToDB(null, "All messages deleted", 1, null, null, null);
    return response.data;
  } catch (error) {
    handleApiError(error, "Messages not deleted: ");
    logToDB(error, "All messages not deleted", 2, null, null, null);
  }
}

async function readAllMessagesFunction() {
  const mainstore = useMainStore();
  try {
    const payload = {
      unread: false,
    };
    const response = await apiClient.patch("/messages/readall/0", payload);
    mainstore.showSnackbar("Messages marked read successfully!", "success");
    logToDB(null, "All messages marked read", 1, null, null, null);
    return response.data;
  } catch (error) {
    handleApiError(error, "Messages not marked read: ");
    logToDB(error, "All messages not marked read", 2, null, null, null);
  }
}

export function useMessages() {
  const queryClient = useQueryClient();
  const { data: messages, isLoading } = useQuery({
    queryKey: ["messages"],
    queryFn: () => getMessagesFunction(),
    select: response => response,
    client: queryClient,
    refetchInterval: 180000,
    refetchIntervalInBackground: true,
  });

  const createMessageMutation = useMutation({
    mutationFn: createMessageFunction,
    onSuccess: () => {
      console.log("Success adding message");
      queryClient.invalidateQueries({ queryKey: ["messages"] });
    },
  });

  const markMessagesReadMutation = useMutation({
    mutationFn: readAllMessagesFunction,
    onSuccess: () => {
      console.log("Success marking messages read");
      queryClient.invalidateQueries({ queryKey: ["messages"] });
    },
  });

  const deleteAllMessagesMutation = useMutation({
    mutationFn: deleteAllMessagesFunction,
    onSuccess: () => {
      console.log("Success deleting all messages");
      queryClient.invalidateQueries({ queryKey: ["messages"] });
    },
  });

  async function addMessage(newMessage) {
    createMessageMutation.mutate(newMessage);
  }

  async function markRead() {
    markMessagesReadMutation.mutate();
  }

  async function deleteAll() {
    deleteAllMessagesMutation.mutate();
  }

  return {
    isLoading,
    messages,
    addMessage,
    markRead,
    deleteAll,
  };
}
