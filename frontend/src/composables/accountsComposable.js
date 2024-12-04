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

async function getAccountsFunction(account_type, inactive) {
  try {
    let querytext = "/accounts/list?";
    let account_text = "";
    let inactive_text = "";
    if (account_type !== "all") {
      account_text = "&account_type=" + account_type;
    }
    if (inactive) {
      inactive_text = "inactive=true";
    } else {
      inactive_text = "inactive=false";
    }
    querytext = querytext + inactive_text + account_text;
    const response = await apiClient.get(querytext);
    return response.data;
  } catch (error) {
    handleApiError(error, "Accounts not fetched: ");
  }
}

async function getAccountByIDFunction(account_id) {
  try {
    const response = await apiClient.get("/accounts/get/" + account_id);
    return response.data;
  } catch (error) {
    handleApiError(error, "Account not fetched: ");
  }
}

async function createAccountFunction(newAccount) {
  const chorestore = useMainStore();
  try {
    const response = await apiClient.post("/accounts/create", newAccount);
    chorestore.showSnackbar("Account created successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Account not created: ");
  }
}

async function deleteAccountFunction(deletedAccount) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.delete(
      "/accounts/delete/" + deletedAccount,
    );
    mainstore.showSnackbar("Account deleted successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Account not deleted: ");
  }
}

async function updateAccountFunction(updatedAccount) {
  try {
    const response = await apiClient.patch(
      "/accounts/update/" + updatedAccount.id,
      updatedAccount,
    );
    return response.data;
  } catch (error) {
    handleApiError(error, "Account not updated: ");
  }
}

export function useAccounts(inactive) {
  const queryClient = useQueryClient();
  const { data: accounts, isLoading } = useQuery({
    queryKey: ["accounts", { type: "all", inactive }],
    queryFn: () => getAccountsFunction("all", inactive),
    select: response => response,
    client: queryClient,
  });

  const { data: cc_accounts, cc_isLoading } = useQuery({
    queryKey: ["accounts", { type: "1" }],
    queryFn: () => getAccountsFunction("1"),
    select: response => response,
    client: queryClient,
  });

  const { data: checking_accounts, checking_isLoading } = useQuery({
    queryKey: ["accounts", { type: "2" }],
    queryFn: () => getAccountsFunction("2"),
    select: response => response,
    client: queryClient,
  });

  const { data: savings_accounts, savings_isLoading } = useQuery({
    queryKey: ["accounts", { type: "3" }],
    queryFn: () => getAccountsFunction("3"),
    select: response => response,
    client: queryClient,
  });

  const { data: investment_accounts, investment_isLoading } = useQuery({
    queryKey: ["accounts", { type: "4" }],
    queryFn: () => getAccountsFunction("4"),
    select: response => response,
    client: queryClient,
  });

  const { data: loan_accounts, loan_isLoading } = useQuery({
    queryKey: ["accounts", { type: "5" }],
    queryFn: () => getAccountsFunction("5"),
    select: response => response,
    client: queryClient,
  });

  const { data: inactive_accounts, inactive_isLoading } = useQuery({
    queryKey: ["accounts", { type: "0" }],
    queryFn: () => getAccountsFunction("0", true),
    select: response => response,
    client: queryClient,
  });

  const createAccountMutation = useMutation({
    mutationFn: createAccountFunction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["accounts"] });
    },
  });

  async function addAccount(newAccount) {
    createAccountMutation.mutate(newAccount);
  }

  return {
    accounts,
    isLoading,
    cc_accounts,
    cc_isLoading,
    checking_accounts,
    checking_isLoading,
    savings_accounts,
    savings_isLoading,
    investment_accounts,
    investment_isLoading,
    loan_accounts,
    loan_isLoading,
    inactive_accounts,
    inactive_isLoading,
    addAccount,
  };
}

export function useAccountByID(account_id) {
  const queryClient = useQueryClient();
  const { data: account, isLoading } = useQuery({
    queryKey: ["accounts", { id: account_id }],
    queryFn: () => getAccountByIDFunction(account_id),
    select: response => response,
    client: queryClient,
  });

  const deleteAccountMutation = useMutation({
    mutationFn: deleteAccountFunction,
    onSuccess: () => {
      console.log("Success deleting account");
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["accounts"] });
      queryClient.invalidateQueries({ queryKey: ["account_forecast"] });
      queryClient.invalidateQueries({ queryKey: ["tag_graph"] });
      queryClient.invalidateQueries({ queryKey: ["retirement_forecast"] });
    },
  });

  const updateAccountMutation = useMutation({
    mutationFn: updateAccountFunction,
    onSuccess: () => {
      console.log("Success updating account");
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["accounts"] });
      queryClient.invalidateQueries({ queryKey: ["account_forecast"] });
      queryClient.invalidateQueries({ queryKey: ["tag_graph"] });
      queryClient.invalidateQueries({ queryKey: ["retirement_forecast"] });
    },
  });

  async function editAccount(updatedAccount) {
    updateAccountMutation.mutate(updatedAccount);
  }

  async function removeAccount(deletedAccount) {
    deleteAccountMutation.mutate(deletedAccount);
  }

  return {
    isLoading,
    account,
    removeAccount,
    editAccount,
  };
}
