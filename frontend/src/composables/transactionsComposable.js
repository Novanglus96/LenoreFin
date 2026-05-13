import {
  useQuery,
  useQueryClient,
  useMutation,
  keepPreviousData,
} from "@tanstack/vue-query";
import apiClient from "./apiClient";
import { useMainStore } from "@/stores/main";
import { useTransactionsStore } from "@/stores/transactions";

function handleApiError(error, message) {
  if (error.response?.status === 401) throw error;
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
  const mainstore = useMainStore();
  try {
    const response = await apiClient.put(
      "/transactions/update/" + updatedTransaction.id,
      updatedTransaction,
    );
    mainstore.showSnackbar("Transaction updated successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Transaction not updated: ");
  }
}

// Keys invalidated after any transaction mutation. Add new dependent queries here.
const TRANSACTION_DEPENDENT_KEYS = [
  ["transactions"],
  ["accounts"],
  ["account_forecast"],
  ["tag_graph"],
  ["tag_graph_items"],
  ["calculator"],
  ["expense_graph"],
  ["pay_graph"],
  ["budgets"],
  ["retirement_forecast"],
  ["retirement_transactions"],
];

function invalidateTransactionDependencies(queryClient, extra = []) {
  [...TRANSACTION_DEPENDENT_KEYS, ...extra].forEach(key =>
    queryClient.invalidateQueries({ queryKey: key }),
  );
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
      invalidateTransactionDependencies(queryClient, [["description-history"]]);
    },
  });

  const deleteTransactionMutation = useMutation({
    mutationFn: deleteTransactionFunction,
    onSuccess: () => {
      console.log("Success deleting transaction");
      invalidateTransactionDependencies(queryClient);
    },
  });

  const clearTransactionMutation = useMutation({
    mutationFn: clearTransactionFunction,
    onSuccess: () => {
      console.log("Success clearing transaction");
      invalidateTransactionDependencies(queryClient);
    },
  });

  const multiEditTransactionsMutation = useMutation({
    mutationFn: multiEditTransactionsFunction,
    onSuccess: () => {
      console.log("Success editing dates of transactions");
      invalidateTransactionDependencies(queryClient);
    },
  });

  const updateTransactionMutation = useMutation({
    mutationFn: updateTransactionFunction,
    onSuccess: () => {
      console.log("Success updating transaction");
      invalidateTransactionDependencies(queryClient, [["description-history"]]);
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
