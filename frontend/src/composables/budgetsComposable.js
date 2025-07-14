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

async function getBudgetsFunction(widget) {
  try {
    let options = "";
    let onlyWidgets = true;
    if (widget === undefined) {
      onlyWidgets = true;
    } else if (widget === false) {
      onlyWidgets = false;
    } else {
      onlyWidgets = true;
    }
    options = "?widget=" + onlyWidgets;
    const response = await apiClient.get("/planning/budget/list" + options);
    return response.data;
  } catch (error) {
    handleApiError(error, "Budgets not fetched: ");
  }
}

async function createBudgetFunction(newBudget) {
  const mainstore = useMainStore();
  try {
    const data = {
      id: newBudget.id,
      start_day: formatDateToYYYYMMDD(newBudget.start_date),
      next_start: formatDateToYYYYMMDD(newBudget.next_date),
      name: newBudget.name,
      active: newBudget.active,
      widget: newBudget.widget,
      amount: newBudget.amount,
      tag_ids: JSON.stringify(newBudget.tag_ids),
      roll_over: newBudget.roll_over,
      repeat_id: newBudget.repeat.id,
      roll_over_amt: 0,
    };
    const response = await apiClient.post("/planning/budget/create", data);
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
    const data = {
      id: budget.id,
      start_day: formatDateToYYYYMMDD(budget.start_date),
      next_start: formatDateToYYYYMMDD(budget.next_date),
      name: budget.name,
      active: budget.active,
      widget: budget.widget,
      amount: budget.amount,
      tag_ids: JSON.stringify(budget.tag_ids),
      roll_over: budget.roll_over,
      repeat_id: budget.repeat.id,
    };
    const response = await apiClient.put(
      "/planning/budget/update/" + data.id,
      data,
    );
    mainstore.showSnackbar("Budget updated successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Budget not updated: ");
  }
}

export function useBudgets(widget) {
  const queryClient = useQueryClient();
  const { data: budgets, isLoading } = useQuery({
    queryKey: ["budgets", { widget: widget }],
    queryFn: () => getBudgetsFunction(widget),
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

function formatDateToYYYYMMDD(date) {
  return new Intl.DateTimeFormat("en-CA", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(date);
}
