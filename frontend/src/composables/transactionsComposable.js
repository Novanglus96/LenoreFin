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
      if (querydata.view_type) {
        querytext = querytext + "&view_type=" + querydata.view_type;
      }
      if (querydata.rule_id) {
        querytext = querytext + "&rule_id=" + querydata.rule_id;
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
  let payload = {
    transactions: deletedTransaction,
  };
  try {
    const response = await apiClient.patch("/transactions/delete", payload);
    mainstore.showSnackbar("Transaction deleted successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Transaction not deleted: ");
  }
}

async function multiEditTransactionsFunction(data) {
  const mainstore = useMainStore();
  let payload = {
    transaction_ids: data.transaction_ids,
    new_date: formatDateToYYYYMMDD(data.new_date),
  };
  try {
    const response = await apiClient.patch("/transactions/multiedit", payload);
    mainstore.showSnackbar("Transaction dates edited successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Transaction dates not edited: ");
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
      queryClient.invalidateQueries({ queryKey: ["calculator"] });
      queryClient.invalidateQueries({ queryKey: ["expense_graph"] });
      queryClient.invalidateQueries({ queryKey: ["pay_graph"] });
      queryClient.invalidateQueries({ queryKey: ["retirement_forecast"] });
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
      queryClient.invalidateQueries({ queryKey: ["calculator"] });
      queryClient.invalidateQueries({ queryKey: ["expense_graph"] });
      queryClient.invalidateQueries({ queryKey: ["pay_graph"] });
      queryClient.invalidateQueries({ queryKey: ["retirement_forecast"] });
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
      queryClient.invalidateQueries({ queryKey: ["calculator"] });
      queryClient.invalidateQueries({ queryKey: ["expense_graph"] });
      queryClient.invalidateQueries({ queryKey: ["pay_graph"] });
      queryClient.invalidateQueries({ queryKey: ["retirement_forecast"] });
    },
  });

  const multiEditTransactionsMutation = useMutation({
    mutationFn: multiEditTransactionsFunction,
    onSuccess: () => {
      console.log("Success editing dates of transactions");
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["accounts"] });
      queryClient.invalidateQueries({ queryKey: ["account_forecast"] });
      queryClient.invalidateQueries({ queryKey: ["tag_graph"] });
      queryClient.invalidateQueries({ queryKey: ["calculator"] });
      queryClient.invalidateQueries({ queryKey: ["expense_graph"] });
      queryClient.invalidateQueries({ queryKey: ["pay_graph"] });
      queryClient.invalidateQueries({ queryKey: ["retirement_forecast"] });
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
      queryClient.invalidateQueries({ queryKey: ["calculator"] });
      queryClient.invalidateQueries({ queryKey: ["expense_graph"] });
      queryClient.invalidateQueries({ queryKey: ["pay_graph"] });
      queryClient.invalidateQueries({ queryKey: ["retirement_forecast"] });
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

  async function mutliEditTransactions(data) {
    multiEditTransactionsMutation.mutate(data);
  }

  return {
    isLoading,
    isFetching,
    transactions,
    addTransaction,
    removeTransaction,
    clearTransaction,
    editTransaction,
    mutliEditTransactions,
  };
}

function formatDateToYYYYMMDD(date) {
  return new Intl.DateTimeFormat("en-CA", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(date);
}
