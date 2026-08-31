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

async function getBucketsFunction() {
  try {
    const response = await apiClient.get("/planning/buckets/list");
    return response.data;
  } catch (error) {
    handleApiError(error, "Buckets not fetched: ");
  }
}

async function createBucketFunction(newBucket) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.post(
      "/planning/buckets/create",
      newBucket,
    );
    mainstore.showSnackbar("Bucket created successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Bucket not created: ");
  }
}

async function deleteBucketFunction(bucket) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.delete(
      "/planning/buckets/delete/" + bucket.id,
    );
    mainstore.showSnackbar("Bucket deleted successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Bucket not deleted: ");
  }
}

async function updateBucketFunction(bucket) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.put(
      "/planning/buckets/update/" + bucket.id,
      bucket,
    );
    mainstore.showSnackbar("Bucket updated successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Bucket not updated: ");
  }
}

async function getWindfallRulesFunction() {
  try {
    const response = await apiClient.get("/planning/windfall-rules/list");
    return response.data;
  } catch (error) {
    handleApiError(error, "Windfall Rules not fetched: ");
  }
}

async function createWindfallRuleFunction(newWindfallRule) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.post(
      "/planning/windfall-rules/create",
      newWindfallRule,
    );
    mainstore.showSnackbar(
      "Windfall Rule created successfully!",
      "success",
    );
    return response.data;
  } catch (error) {
    handleApiError(error, "Windfall Rule not created: ");
  }
}

async function deleteWindfallRuleFunction(windfallRule) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.delete(
      "/planning/windfall-rules/delete/" + windfallRule.id,
    );
    mainstore.showSnackbar(
      "Windfall Rule deleted successfully!",
      "success",
    );
    return response.data;
  } catch (error) {
    handleApiError(error, "Windfall Rule not deleted: ");
  }
}

async function updateWindfallRuleFunction(windfallRule) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.put(
      "/planning/windfall-rules/update/" + windfallRule.id,
      windfallRule,
    );
    mainstore.showSnackbar("WindfallRule updated successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "WindfallRule not updated: ");
  }
}

export function useBuckets() {
  const queryClient = useQueryClient();
  const { data: buckets, isLoading } = useQuery({
    queryKey: ["buckets"],
    queryFn: () => getBucketsFunction(),
    select: response => response,
    client: queryClient,
  });

  // The planner is derived from these records — its goal, account, reminder
  // and per-paycheck figure all live on Bucket — so every write here has
  // to invalidate it too. Applying a suggestion already invalidates
  // "buckets" from the other direction; this is the missing half.
  const invalidateBuckets = () => {
    queryClient.invalidateQueries({ queryKey: ["buckets"] });
    queryClient.invalidateQueries({ queryKey: ["planner"] });
  };

  const createBucketMutation = useMutation({
    mutationFn: createBucketFunction,
    onSuccess: invalidateBuckets,
  });

  const deleteBucketMutation = useMutation({
    mutationFn: deleteBucketFunction,
    onSuccess: invalidateBuckets,
  });

  const updateBucketMutation = useMutation({
    mutationFn: updateBucketFunction,
    onSuccess: invalidateBuckets,
  });

  async function addBucket(newBucket) {
    createBucketMutation.mutate(newBucket);
  }

  async function removeBucket(bucket) {
    deleteBucketMutation.mutate(bucket);
  }

  async function editBucket(bucket) {
    updateBucketMutation.mutate(bucket);
  }

  return {
    isLoading,
    buckets,
    addBucket,
    removeBucket,
    editBucket,
  };
}

export function useWindfallRules() {
  const queryClient = useQueryClient();
  const { data: windfallRules, isLoading } = useQuery({
    queryKey: ["windfallRules"],
    queryFn: () => getWindfallRulesFunction(),
    select: response => response,
    client: queryClient,
  });

  const createWindfallRuleMutation = useMutation({
    mutationFn: createWindfallRuleFunction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["windfallRules"] });
    },
  });

  const deleteWindfallRuleMutation = useMutation({
    mutationFn: deleteWindfallRuleFunction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["windfallRules"] });
    },
  });

  const updateWindfallRuleMutation = useMutation({
    mutationFn: updateWindfallRuleFunction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["windfallRules"] });
    },
  });

  async function addWindfallRule(newWindfallRule) {
    createWindfallRuleMutation.mutate(newWindfallRule);
  }

  async function removeWindfallRule(windfallRule) {
    deleteWindfallRuleMutation.mutate(windfallRule);
  }

  async function editWindfallRule(windfallRule) {
    updateWindfallRuleMutation.mutate(windfallRule);
  }

  return {
    isLoading,
    windfallRules,
    addWindfallRule,
    removeWindfallRule,
    editWindfallRule,
  };
}
