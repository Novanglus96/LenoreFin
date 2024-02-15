import { useQuery, useQueryClient, useMutation } from "@tanstack/vue-query";
import axios from "axios";
import { useMainStore } from "@/stores/main";
import { logToDB } from "./logentriesComposable";

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
  mainstore.showSnackbar(message + "Error #" + error.response.status, "error");
  throw error;
}

async function getTagsFunction(tag_type) {
  try {
    let querytext = "";
    if (tag_type) {
      querytext = "?tag_type=" + tag_type;
    }
    const response = await apiClient.get("/tags" + querytext);
    logToDB(null, "Tags fetched", 0, null, null, null);
    return response.data;
  } catch (error) {
    handleApiError(error, "Tags not fetched: ");
    logToDB(error, "Tags not fetched", 2, null, null, null);
  }
}

async function getParentTagsFunction() {
  try {
    const response = await apiClient.get("/tags?parent_only=true");
    logToDB(null, "Parent Tags fetched", 0, null, null, null);
    return response.data;
  } catch (error) {
    handleApiError(error, "Parent Tags not fetched: ");
    logToDB(error, "Parent Tags not fetched", 2, null, null, null);
  }
}

async function getGraphByTagsFunction(widget_id) {
  try {
    const response = await apiClient.get(
      "/graphs_bytags?widget_id=" + widget_id,
    );
    logToDB(null, "Graph by tags fetched", 0, null, null, null);
    return response.data;
  } catch (error) {
    handleApiError(error, "Graph by tags not fetched: ");
    logToDB(error, "Graph by tags not fetched", 2, null, null, null);
  }
}

async function getTransactionsByTagsFunction(tag_id, month) {
  try {
    const response = await apiClient.get(
      "/transactions_bytag?tag=" + tag_id + "&month=" + month,
    );
    logToDB(null, "Transactions by tag fetched", 0, null, null, null);
    return response.data;
  } catch (error) {
    handleApiError(error, "Transactions by tag not fetched: ");
    logToDB(error, "Transactions by tag not fetched", 2, null, null, null);
  }
}

async function createTagFunction(newTag) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.post("/tags", newTag);
    mainstore.showSnackbar("Tag created successfully!", "success");
    logToDB(null, "Tag created: " + newTag.tag_name, 1, null, null, null);
    return response.data;
  } catch (error) {
    handleApiError(error, "Tag not created: ");
    logToDB(error, "Tag not created: " + newTag.tag_name, 2, null, null, null);
  }
}

export function useTags(tag_type) {
  const queryClient = useQueryClient();
  const { data: tags, isLoading } = useQuery({
    queryKey: ["tags"],
    queryFn: () => getTagsFunction(tag_type),
    select: response => response,
    client: queryClient,
  });

  const createTagMutation = useMutation({
    mutationFn: createTagFunction,
    onSuccess: () => {
      console.log("Success adding tag");
      queryClient.invalidateQueries({ queryKey: ["tags"] });
    },
  });

  async function addTag(newTag) {
    createTagMutation.mutate(newTag);
  }

  return {
    isLoading,
    tags,
    addTag,
  };
}

export function useParentTags() {
  const queryClient = useQueryClient();
  const { data: parent_tags, isLoading } = useQuery({
    queryKey: ["tags", { parent_only: true }],
    queryFn: () => getParentTagsFunction(),
    select: response => response,
    client: queryClient,
  });

  return {
    isLoading,
    parent_tags,
  };
}

export function useGraphs(widget_id) {
  const queryClient = useQueryClient();
  const { data: tag_graph, isLoading } = useQuery({
    queryKey: ["tag_graph", { widgetID: widget_id }],
    queryFn: () => getGraphByTagsFunction(widget_id),
    select: response => response,
    client: queryClient,
  });

  return {
    isLoading,
    tag_graph,
  };
}

export function useGraphTransactions(tag_id, month) {
  const queryClient = useQueryClient();
  const { data: tag_transactions, isLoading } = useQuery({
    queryKey: ["tag_transactions", { tagID: tag_id }],
    queryFn: () => getTransactionsByTagsFunction(tag_id, month),
    select: response => response,
    client: queryClient,
  });

  return {
    isLoading,
    tag_transactions,
  };
}
