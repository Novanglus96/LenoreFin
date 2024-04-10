import {
  useQuery,
  useQueryClient,
  useMutation,
  keepPreviousData,
} from "@tanstack/vue-query";
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

async function getTransactionsFunction(
  account_id,
  maxdays,
  forecast,
  page,
  page_size,
) {
  try {
    if (account_id) {
      let querytext = "?account=" + account_id;
      if (maxdays) {
        querytext = querytext + "&maxdays=" + maxdays;
      }
      if (forecast) {
        querytext = querytext + "&forecast=" + forecast;
      }
      if (page) {
        querytext = querytext + "&pageno=" + page;
      }
      if (page_size) {
        querytext = querytext + "&recno=" + page_size;
      }
      const response = await apiClient.get("/transactions" + querytext);
      return response.data;
    } else {
      const response = await apiClient.get("/transactions");
      return response.data;
    }
  } catch (error) {
    handleApiError(error, "Transactions not fetched: ");
  }
}

async function createTransactionFunction(newTransaction) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.post("/transactions", newTransaction);
    mainstore.showSnackbar("Transaction created successfully!", "success");

    return response.id;
  } catch (error) {
    handleApiError(error, "Transaction not created: ");
  }
}

async function deleteTransactionFunction(deletedTransaction) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.delete(
      "/transactions/" + deletedTransaction,
    );
    mainstore.showSnackbar("Transaction deleted successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Transaction not deleted: ");
  }
}

async function clearTransactionFunction(clearedTransaction) {
  const mainstore = useMainStore();
  const payload = {
    status_id: 2,
  };
  try {
    const response = await apiClient.patch(
      "/transactions/clear/" + clearedTransaction,
      payload,
    );
    mainstore.showSnackbar("Transaction cleared successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Transaction not cleared: ");
  }
}

async function updateTransactionFunction(updatedTransaction) {
  try {
    const response = await apiClient.put(
      "/transactions/" + updatedTransaction.id,
      updatedTransaction,
    );
    return response.data;
  } catch (error) {
    handleApiError(error, "Transaction not updated: ");
  }
}

export function useTransactions(
  account_id,
  maxdays,
  forecast,
  page,
  page_size,
) {
  const queryClient = useQueryClient();
  const { data: transactions, isLoading } = useQuery({
    queryKey: [
      "transactions",
      { account: account_id, page: page, page_size: page_size },
    ],
    queryFn: () =>
      getTransactionsFunction(account_id, maxdays, forecast, page, page_size),
    placeholderData: keepPreviousData,
    select: response => response,
    client: queryClient,
  });

  const createTransactionMutation = useMutation({
    mutationFn: createTransactionFunction,
    onSuccess: data => {
      console.log("Success adding transaction", data);
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["accounts"] });
      queryClient.invalidateQueries({ queryKey: ["account_forecast"] });
      queryClient.invalidateQueries({ queryKey: ["tag_graph"] });
    },
  });

  const deleteTransactionMutation = useMutation({
    mutationFn: deleteTransactionFunction,
    onSuccess: () => {
      console.log("Success deleting transaction");
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["accounts"] });
      queryClient.invalidateQueries({ queryKey: ["account_forecast"] });
      queryClient.invalidateQueries({ queryKey: ["tag_graph"] });
    },
  });

  const clearTransactionMutation = useMutation({
    mutationFn: clearTransactionFunction,
    onSuccess: () => {
      console.log("Success clearing transaction");
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["accounts"] });
      queryClient.invalidateQueries({ queryKey: ["account_forecast"] });
      queryClient.invalidateQueries({ queryKey: ["tag_graph"] });
    },
  });

  const updateTransactionMutation = useMutation({
    mutationFn: updateTransactionFunction,
    onSuccess: () => {
      console.log("Success updating transaction");
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["accounts"] });
      queryClient.invalidateQueries({ queryKey: ["account_forecast"] });
      queryClient.invalidateQueries({ queryKey: ["tag_graph"] });
    },
  });

  async function editTransaction(updatedTransaction) {
    updateTransactionMutation.mutate(updatedTransaction);
  }

  async function addTransaction(newTransaction) {
    createTransactionMutation.mutate(newTransaction);
  }

  async function removeTransaction(deletedTransaction) {
    deleteTransactionMutation.mutate(deletedTransaction);
  }

  async function clearTransaction(clearedTransaction) {
    clearTransactionMutation.mutate(clearedTransaction);
  }

  return {
    isLoading,
    transactions,
    addTransaction,
    removeTransaction,
    clearTransaction,
    editTransaction,
  };
}
