import { useQuery, useQueryClient, useMutation } from "@tanstack/vue-query";
import axios from "axios";
import { useMainStore } from "@/stores/main";

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

async function getContributionsFunction() {
  try {
    const response = await apiClient.get("/planning/contributions/list");
    return response.data;
  } catch (error) {
    handleApiError(error, "Contributions not fetched: ");
  }
}

async function createContributionFunction(newContribution) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.post(
      "/planning/contributions/create",
      newContribution,
    );
    mainstore.showSnackbar("Contribution created successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Contribution not created: ");
  }
}

async function deleteContributionFunction(contribution) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.delete(
      "/planning/contributions/delete/" + contribution.id,
    );
    mainstore.showSnackbar("Contribution deleted successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Contribution not deleted: ");
  }
}

async function updateContributionFunction(contribution) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.put(
      "/planning/contributions/update/" + contribution.id,
      contribution,
    );
    mainstore.showSnackbar("Contribution updated successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Contribution not updated: ");
  }
}

async function getContributionRulesFunction() {
  try {
    const response = await apiClient.get("/planning/contrib-rules/list");
    return response.data;
  } catch (error) {
    handleApiError(error, "Contribution Rules not fetched: ");
  }
}

async function createContributionRuleFunction(newContributionRule) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.post(
      "/planning/contrib-rules/create",
      newContributionRule,
    );
    mainstore.showSnackbar(
      "Contribution Rule created successfully!",
      "success",
    );
    return response.data;
  } catch (error) {
    handleApiError(error, "Contribution Rule not created: ");
  }
}

async function deleteContributionRuleFunction(contributionRule) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.delete(
      "/planning/contrib-rules/delete/" + contributionRule.id,
    );
    mainstore.showSnackbar(
      "Contribution Rule deleted successfully!",
      "success",
    );
    return response.data;
  } catch (error) {
    handleApiError(error, "Contribution Rule not deleted: ");
  }
}

async function updateContributionRuleFunction(contributionRule) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.put(
      "/planning/contrib-rules/update/" + contributionRule.id,
      contributionRule,
    );
    mainstore.showSnackbar("ContributionRule updated successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "ContributionRule not updated: ");
  }
}

export function useContributions() {
  const queryClient = useQueryClient();
  const { data: contributions, isLoading } = useQuery({
    queryKey: ["contributions"],
    queryFn: () => getContributionsFunction(),
    select: response => response,
    client: queryClient,
  });

  const createContributionMutation = useMutation({
    mutationFn: createContributionFunction,
    onSuccess: () => {
      console.log("Success adding contribution");
      queryClient.invalidateQueries({ queryKey: ["contributions"] });
    },
  });

  const deleteContributionMutation = useMutation({
    mutationFn: deleteContributionFunction,
    onSuccess: () => {
      console.log("Success deleting contribution");
      queryClient.invalidateQueries({ queryKey: ["contributions"] });
    },
  });

  const updateContributionMutation = useMutation({
    mutationFn: updateContributionFunction,
    onSuccess: () => {
      console.log("Success updating contribution");
      queryClient.invalidateQueries({ queryKey: ["contributions"] });
    },
  });

  async function addContribution(newContribution) {
    createContributionMutation.mutate(newContribution);
  }

  async function removeContribution(contribution) {
    deleteContributionMutation.mutate(contribution);
  }

  async function editContribution(contribution) {
    updateContributionMutation.mutate(contribution);
  }

  return {
    isLoading,
    contributions,
    addContribution,
    removeContribution,
    editContribution,
  };
}

export function useContributionRules() {
  const queryClient = useQueryClient();
  const { data: contributionRules, isLoading } = useQuery({
    queryKey: ["contributionRules"],
    queryFn: () => getContributionRulesFunction(),
    select: response => response,
    client: queryClient,
  });

  const createContributionRuleMutation = useMutation({
    mutationFn: createContributionRuleFunction,
    onSuccess: () => {
      console.log("Success adding contribution rule");
      queryClient.invalidateQueries({ queryKey: ["contributionRules"] });
    },
  });

  const deleteContributionRuleMutation = useMutation({
    mutationFn: deleteContributionRuleFunction,
    onSuccess: () => {
      console.log("Success deleting contribution rule");
      queryClient.invalidateQueries({ queryKey: ["contributionRules"] });
    },
  });

  const updateContributionRuleMutation = useMutation({
    mutationFn: updateContributionRuleFunction,
    onSuccess: () => {
      console.log("Success updating contribution rule");
      queryClient.invalidateQueries({ queryKey: ["contributionRules"] });
    },
  });

  async function addContributionRule(newContributionRule) {
    createContributionRuleMutation.mutate(newContributionRule);
  }

  async function removeContributionRule(contributionRule) {
    deleteContributionRuleMutation.mutate(contributionRule);
  }

  async function editContributionRule(contributionRule) {
    updateContributionRuleMutation.mutate(contributionRule);
  }

  return {
    isLoading,
    contributionRules,
    addContributionRule,
    removeContributionRule,
    editContributionRule,
  };
}
