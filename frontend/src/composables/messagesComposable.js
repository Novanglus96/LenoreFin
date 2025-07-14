import { useQuery, useQueryClient, useMutation } from "@tanstack/vue-query";
import axios from "axios";
import { useMainStore } from "@/stores/main";
import { onUnmounted } from "vue";

const apiClient = axios.create({
  baseURL: "/api/v1",
  withCredentials: false,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
    Authorization: `Bearer ${
      window.VITE_API_KEY === "__VITE_API_KEY__"
        ? import.meta.env.VITE_API_KEY // Fallback to the environment variable if the value is the default placeholder
        : window.VITE_API_KEY // Otherwise, use the value in window.VITE_API_KEY
    }`,
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

async function getMessagesFunction() {
  try {
    const response = await apiClient.get("/administration/messages/list");
    return response.data;
  } catch (error) {
    handleApiError(error, "Messages not fetched: ");
  }
}

async function createMessageFunction(newMessage) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.post(
      "/administration/messages/create",
      newMessage,
    );
    mainstore.showSnackbar("Message created successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Message not created: ");
  }
}

async function deleteAllMessagesFunction() {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.delete(
      "/administration/messages/deleteall/0",
    );
    mainstore.showSnackbar("Messages deleted successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Messages not deleted: ");
  }
}

async function readAllMessagesFunction() {
  const mainstore = useMainStore();
  try {
    const payload = {
      unread: false,
    };
    const response = await apiClient.patch(
      "/administration/messages/readall/0",
      payload,
    );
    mainstore.showSnackbar("Messages marked read successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Messages not marked read: ");
  }
}

export function useMessages() {
  const queryClient = useQueryClient();
  const {
    data: messages,
    isLoading,
    refetch,
  } = useQuery({
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

  const refetchMessages = async () => {
    await refetch();
  };

  const intervalId = setInterval(refetchMessages, 1 * 60 * 1000);

  onUnmounted(() => {
    clearInterval(intervalId);
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
