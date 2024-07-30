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

async function getBanksFunction() {
  try {
    const response = await apiClient.get("/accounts/banks/list");
    return response.data;
  } catch (error) {
    handleApiError(error, "Banks not fetched: ");
  }
}

async function createBankFunction(newBank) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.post("/accounts/banks/create", newBank);
    mainstore.showSnackbar("Bank created successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Bank not created: ");
  }
}

export function useBanks() {
  const queryClient = useQueryClient();
  const { data: banks, isLoading } = useQuery({
    queryKey: ["banks"],
    queryFn: () => getBanksFunction(),
    select: response => response,
    client: queryClient,
  });

  const createBankMutation = useMutation({
    mutationFn: createBankFunction,
    onSuccess: () => {
      console.log("Success adding bank");
      queryClient.invalidateQueries({ queryKey: ["banks"] });
    },
  });

  async function addBank(newBank) {
    createBankMutation.mutate(newBank);
  }

  return {
    isLoading,
    banks,
    addBank,
  };
}
