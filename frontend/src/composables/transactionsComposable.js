import {
  useQuery,
  useQueryClient,
  useMutation,
  keepPreviousData,
} from "@tanstack/vue-query";
import axios from "axios";
import { useMainStore } from "@/stores/main";
import { useTransactionsStore } from "@/stores/transactions";

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

async function getTransactionsFunction(querydata) {
  try {
    if (querydata.account_id) {
      let querytext = "?account=" + querydata.account_id;
      if (querydata.maxdays) {
        querytext = querytext + "&maxdays=" + querydata.maxdays;
      }
      if (querydata.forecast) {
        querytext = querytext + "&forecast=" + querydata.forecast;
      }
      if (querydata.page) {
        querytext = querytext + "&page=" + querydata.page;
      }
      if (querydata.page_size) {
        querytext = querytext + "&page_size=" + querydata.page_size;
      }
      const response = await apiClient.get("/transactions/list" + querytext);
      return response.data;
    } else {
      const response = await apiClient.get("/transactions/list");
      return response.data;
    }
  } catch (error) {
    handleApiError(error, "Transactions not fetched: ");
  }
}

async function createTransactionFunction(newTransaction) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.post(
      "/transactions/create",
      newTransaction,
    );
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
      "/transactions/delete/" + deletedTransaction,
    );
    mainstore.showSnackbar("Transaction deleted successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Transaction not deleted: ");
  }
}

async function clearTransactionFunction(clearedTransaction) {
  const mainstore = useMainStore();
  let payload = {
    transactions: clearedTransaction,
  };
  try {
    const response = await apiClient.patch("/transactions/clear", payload);
    mainstore.showSnackbar("Transaction cleared successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Transaction not cleared: ");
  }
}

async function updateTransactionFunction(updatedTransaction) {
  try {
    const response = await apiClient.put(
      "/transactions/update/" + updatedTransaction.id,
      updatedTransaction,
    );
    return response.data;
  } catch (error) {
    handleApiError(error, "Transaction not updated: ");
  }
}

export function useTransactions() {
  const queryClient = useQueryClient();
  const transcation_store = useTransactionsStore();
  const {
    data: transactions,
    isLoading,
    isFetching,
  } = useQuery({
    queryKey: ["transactions", transcation_store.pageinfo],
    queryFn: () => getTransactionsFunction(transcation_store.pageinfo),
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
      queryClient.invalidateQueries({ queryKey: ["description-history"] });
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
      queryClient.invalidateQueries({ queryKey: ["description-history"] });
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
    isFetching,
    transactions,
    addTransaction,
    removeTransaction,
    clearTransaction,
    editTransaction,
  };
}
