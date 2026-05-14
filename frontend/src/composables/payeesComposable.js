import { useQuery, useQueryClient, useMutation } from "@tanstack/vue-query";
import apiClient from "./apiClient";
import { useMainStore } from "@/stores/main";

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

async function updatePayeeFunction(updatedPayee) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.put(
      "/administration/payees/update/" + updatedPayee.id,
      updatedPayee,
    );
    mainstore.showSnackbar("Payee updated successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Payee not updated: ");
  }
}

async function deletePayeeFunction(payeeId) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.delete(
      "/administration/payees/delete/" + payeeId,
    );
    mainstore.showSnackbar("Payee deleted successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Payee not deleted: ");
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
      queryClient.invalidateQueries({ queryKey: ["payees"] });
    },
  });

  const updatePayeeMutation = useMutation({
    mutationFn: updatePayeeFunction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["payees"] });
    },
  });

  const deletePayeeMutation = useMutation({
    mutationFn: deletePayeeFunction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["payees"] });
    },
  });

  function addPayee(newPayee) {
    createPayeeMutation.mutate(newPayee);
  }

  function editPayee(updatedPayee) {
    updatePayeeMutation.mutate(updatedPayee);
  }

  function removePayee(payeeId) {
    deletePayeeMutation.mutate(payeeId);
  }

  return {
    isLoading,
    payees,
    addPayee,
    editPayee,
    removePayee,
  };
}
