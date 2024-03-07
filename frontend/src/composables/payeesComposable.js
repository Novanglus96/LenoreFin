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
  mainstore.showSnackbar(message + " : " + error.response.data.detail, "error");
  throw error;
}

async function getPayeesFunction() {
  try {
    const response = await apiClient.get("/payees");
    return response.data;
  } catch (error) {
    handleApiError(error, "Payees not fetched: ");
  }
}

async function createPayeeFunction(newPayee) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.post("/payees", newPayee);
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
