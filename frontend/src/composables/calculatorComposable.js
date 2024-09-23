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
    const response = await apiClient.post(
      "/planning/calculator/calculation_rule/create",
      newRule,
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

  async function addCalculationRule(newRule) {
    createCalculationRuleMutation.mutate(newRule);
  }

  async function removeCalculationRule(ruleToDelete) {
    deleteCalculationRuleMutation.mutate(ruleToDelete);
  }

  return {
    isLoading,
    calculation_rules,
    addCalculationRule,
    removeCalculationRule,
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
