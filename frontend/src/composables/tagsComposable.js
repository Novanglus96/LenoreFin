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

async function getTagsFunction(tag_type) {
  try {
    let querytext = "";
    if (tag_type) {
      querytext = "?tag_type=" + tag_type;
    }
    const response = await apiClient.get("/tags/list" + querytext);
    return response.data;
  } catch (error) {
    handleApiError(error, "Tags not fetched: ");
  }
}

async function getParentTagsFunction(tag_type) {
  try {
    let query = "";
    if (tag_type) {
      query = "?tag_type=" + tag_type;
    }
    const response = await apiClient.get("/tags/main-tags/list" + query);
    return response.data;
  } catch (error) {
    handleApiError(error, "Parent Tags not fetched: ");
  }
}

async function getMainTagsFunction() {
  try {
    const response = await apiClient.get("/tags/list?main_only=true");
    return response.data;
  } catch (error) {
    handleApiError(error, "Main Tags not fetched: ");
  }
}

async function getGraphByTagsFunction(widget_id) {
  try {
    const response = await apiClient.get(
      "/tags/graph-by-tags/get?widget_id=" + widget_id,
    );
    return response.data;
  } catch (error) {
    handleApiError(error, "Graph by tags not fetched: ");
  }
}

async function getTransactionsByTagsFunction(tag_id) {
  try {
    const response = await apiClient.get("/tags/tag-graphs/list?tag=" + tag_id);
    return response.data;
  } catch (error) {
    handleApiError(error, "Transactions by tag not fetched: ");
  }
}

async function createTagFunction(newTag) {
  const mainstore = useMainStore();
  try {
    let data = {};
    if (newTag.parent_id == null) {
      data = {
        parent_name: newTag.tag_name,
        tag_type_id: newTag.tag_type_id,
      };
    } else {
      data = {
        child_name: newTag.tag_name,
        tag_type_id: newTag.tag_type_id,
        parent_id: newTag.parent_id,
      };
    }
    const response = await apiClient.post("/tags/create", data);
    mainstore.showSnackbar("Tag created successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Tag not created: ");
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

export function useParentTags(tag_type) {
  const queryClient = useQueryClient();
  const { data: parent_tags, isLoading } = useQuery({
    queryKey: ["tags", { parent_only: true }],
    queryFn: () => getParentTagsFunction(tag_type),
    select: response => response,
    client: queryClient,
  });

  return {
    isLoading,
    parent_tags,
  };
}

export function useMainTags() {
  const queryClient = useQueryClient();
  const { data: main_tags, isLoading } = useQuery({
    queryKey: ["tags", { main_only: true }],
    queryFn: () => getMainTagsFunction(),
    select: response => response,
    client: queryClient,
  });

  return {
    isLoading,
    main_tags,
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

export function useGraphTransactions(tag_id) {
  const queryClient = useQueryClient();
  const { data: tag_transactions, isLoading } = useQuery({
    queryKey: ["tag_transactions", { tagID: tag_id }],
    queryFn: () => getTransactionsByTagsFunction(tag_id),
    select: response => response,
    client: queryClient,
  });

  return {
    isLoading,
    tag_transactions,
  };
}
