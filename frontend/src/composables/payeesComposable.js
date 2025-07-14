import { useQuery, useQueryClient, useMutation } from "@tanstack/vue-query";
import axios from "axios";
import { useMainStore } from "@/stores/main";

const apiClient = axios.create({
  baseURL: "/api/v1",
  withCredentials: false,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
    Authorization: `Bearer ${window.__APP_CONFIG__?.VITE_API_KEY}`,
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

async function getPayeesFunction() {
  try {
    const response = await apiClient.get("/administration/payees/list");
    return response.data;
  } catch (error) {
    handleApiError(error, "Payees not fetched: ");
  }
}

async function createPayeeFunction(newPayee) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.post(
      "/administration/payees/create",
      newPayee,
    );
    mainstore.showSnackbar("Payee created successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Payee not created: ");
  }
}

export function usePayees() {
  const queryClient = useQueryClient();
  const { data: payees, isLoading } = useQuery({
    queryKey: ["payees"],
    queryFn: () => getPayeesFunction(),
    select: response => response,
    client: queryClient,
  });

  const createPayeeMutation = useMutation({
    mutationFn: createPayeeFunction,
    onSuccess: () => {
      console.log("Success adding payee");
      queryClient.invalidateQueries({ queryKey: ["payees"] });
    },
  });

  async function addPayee(newPayee) {
    createPayeeMutation.mutate(newPayee);
  }

  return {
    isLoading,
    payees,
    addPayee,
  };
}
