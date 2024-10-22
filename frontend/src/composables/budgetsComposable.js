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

async function getBudgetsFunction() {
  try {
    const response = await apiClient.get("/planning/budget/list");
    return response.data;
  } catch (error) {
    handleApiError(error, "Budgets not fetched: ");
  }
}

async function createBudgetFunction(newBudget) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.post("/planning/budget/create", newBudget);
    mainstore.showSnackbar("Budget created successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Budget not created: ");
  }
}

async function deleteBudgetFunction(budget) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.delete(
      "/planning/budget/delete/" + budget.id,
    );
    mainstore.showSnackbar("Budget deleted successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Budget not deleted: ");
  }
}

async function updateBudgetFunction(budget) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.put(
      "/planning/budget/update/" + budget.id,
      budget,
    );
    mainstore.showSnackbar("Budget updated successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Budget not updated: ");
  }
}

export function useBudgets() {
  const queryClient = useQueryClient();
  const { data: budgets, isLoading } = useQuery({
    queryKey: ["budgets"],
    queryFn: () => getBudgetsFunction(),
    select: response => response,
    client: queryClient,
  });

  const createBudgetMutation = useMutation({
    mutationFn: createBudgetFunction,
    onSuccess: () => {
      console.log("Success adding budget");
      queryClient.invalidateQueries({ queryKey: ["budgets"] });
    },
  });

  const deleteBudgetMutation = useMutation({
    mutationFn: deleteBudgetFunction,
    onSuccess: () => {
      console.log("Success deleting budget");
      queryClient.invalidateQueries({ queryKey: ["budgets"] });
    },
  });

  const updateBudgetMutation = useMutation({
    mutationFn: updateBudgetFunction,
    onSuccess: () => {
      console.log("Success updating budget");
      queryClient.invalidateQueries({ queryKey: ["budgets"] });
    },
  });

  async function addBudget(newBudget) {
    createBudgetMutation.mutate(newBudget);
  }

  async function removeBudget(budget) {
    deleteBudgetMutation.mutate(budget);
  }

  async function editBudget(budget) {
    updateBudgetMutation.mutate(budget);
  }

  return {
    isLoading,
    budgets,
    addBudget,
    removeBudget,
    editBudget,
  };
}
