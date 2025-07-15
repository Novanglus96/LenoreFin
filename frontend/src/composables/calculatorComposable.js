import { useQuery, useQueryClient, useMutation } from "@tanstack/vue-query";
import axios from "axios";
import { useMainStore } from "@/stores/main";
import { useApiKey } from "./ueApiKey";

const apiKey = useApiKey();

const apiClient = axios.create({
  baseURL: "/api/v1",
  withCredentials: false,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
    Authorization: `Bearer ${apiKey}`,
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

async function getCalculationRulesFunction() {
  try {
    const response = await apiClient.get(
      "/planning/calculator/calculation_rule/list",
    );
    return response.data;
  } catch (error) {
    handleApiError(error, "Calculation rules not fetched: ");
  }
}

async function getCalculatorFunction(rule_id, timeframe) {
  if (rule_id) {
    try {
      const response = await apiClient.get(
        "/planning/calculator/get/" + rule_id + "?timeframe=" + timeframe,
      );
      return response.data;
    } catch (error) {
      handleApiError(error, "Calculator not fetched: ");
    }
  } else {
    return null;
  }
}

async function createCalculationRuleFunction(newRule) {
  const mainstore = useMainStore();
  try {
    const data = {
      name: newRule.name,
      tag_ids: JSON.stringify(newRule.tag_ids),
      source_account_id: newRule.source_account_id,
      destination_account_id: newRule.destination_account_id,
    };
    const response = await apiClient.post(
      "/planning/calculator/calculation_rule/create",
      data,
    );
    mainstore.showSnackbar("Calculation rule created successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Calculation rule not created: ");
  }
}

async function deleteCalculationRuleFunction(ruleToDelete) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.delete(
      "/planning/calculator/calculation_rule/delete/" + ruleToDelete,
    );
    mainstore.showSnackbar("Calculation rule deleted successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Calculation rule not deleted: ");
  }
}

async function updateCalculationRuleFunction(ruleToEdit) {
  const mainstore = useMainStore();
  try {
    const data = {
      name: ruleToEdit.name,
      tag_ids: JSON.stringify(ruleToEdit.tag_ids),
      source_account_id: ruleToEdit.source_account_id,
      destination_account_id: ruleToEdit.destination_account_id,
    };
    const response = await apiClient.put(
      "/planning/calculator/calculation_rule/update/" + ruleToEdit.id,
      data,
    );
    mainstore.showSnackbar("Calculation rule updated successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Calculation rule not updated: ");
  }
}

export function useCalculationRule() {
  const queryClient = useQueryClient();
  const { data: calculation_rules, isLoading } = useQuery({
    queryKey: ["calculation_rules"],
    queryFn: () => getCalculationRulesFunction(),
    select: response => response,
    client: queryClient,
  });

  const createCalculationRuleMutation = useMutation({
    mutationFn: createCalculationRuleFunction,
    onSuccess: () => {
      console.log("Success adding calculation rule");
      queryClient.invalidateQueries({ queryKey: ["calculation_rules"] });
    },
  });

  const deleteCalculationRuleMutation = useMutation({
    mutationFn: deleteCalculationRuleFunction,
    onSuccess: () => {
      console.log("Success deleteing calculation rule");
      queryClient.invalidateQueries({ queryKey: ["calculation_rules"] });
    },
  });

  const updateCalculationRuleMutation = useMutation({
    mutationFn: updateCalculationRuleFunction,
    onSuccess: () => {
      console.log("Success updating calculation rule");
      queryClient.invalidateQueries({ queryKey: ["calculation_rules"] });
    },
  });

  async function addCalculationRule(newRule) {
    createCalculationRuleMutation.mutate(newRule);
  }

  async function removeCalculationRule(ruleToDelete) {
    deleteCalculationRuleMutation.mutate(ruleToDelete);
  }

  async function editCalculationRule(ruleToEdit) {
    updateCalculationRuleMutation.mutate(ruleToEdit);
  }

  return {
    isLoading,
    calculation_rules,
    addCalculationRule,
    removeCalculationRule,
    editCalculationRule,
  };
}

export function useCalculator(rule_id, timeframe) {
  const queryClient = useQueryClient();
  const { data: calculator, isLoading } = useQuery({
    queryKey: ["calculator", { ruleID: rule_id, timeframe: timeframe }],
    queryFn: () => getCalculatorFunction(rule_id, timeframe),
    select: response => response,
    client: queryClient,
  });

  return {
    isLoading,
    calculator,
  };
}
