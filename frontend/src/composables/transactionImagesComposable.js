import { useQuery, useQueryClient, useMutation } from "@tanstack/vue-query";
import { computed } from "vue";
import apiClient from "./apiClient";
import { useMainStore } from "@/stores/main";

function handleApiError(error, message) {
  if (error.response?.status === 401) throw error;
  const mainstore = useMainStore();
  mainstore.showSnackbar(
    message + " : " + (error.response?.data?.detail ?? "Unknown error"),
    "error",
  );
  throw error;
}

async function getTransactionImagesFunction(transactionId) {
  try {
    const response = await apiClient.get(
      `/transactions/attachments/list/${transactionId}`,
    );
    return response.data;
  } catch (error) {
    return handleApiError(error, "Attachments not fetched");
  }
}

async function uploadTransactionImageFunction({ transactionId, file }) {
  const mainstore = useMainStore();
  try {
    const formData = new FormData();
    formData.append("file", file);
    const response = await apiClient.post(
      `/transactions/attachments/upload/${transactionId}`,
      formData,
      { headers: { "Content-Type": "multipart/form-data" } },
    );
    mainstore.showSnackbar("Attachment uploaded!", "success");
    return response.data;
  } catch (error) {
    return handleApiError(error, "Attachment not uploaded");
  }
}

async function deleteTransactionImageFunction(imageId) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.delete(
      `/transactions/attachments/delete/${imageId}`,
    );
    mainstore.showSnackbar("Attachment deleted!", "success");
    return response.data;
  } catch (error) {
    return handleApiError(error, "Attachment not deleted");
  }
}

export function useTransactionImages(transactionId) {
  const queryClient = useQueryClient();
  const id = computed(() =>
    transactionId?.value !== undefined ? transactionId.value : transactionId,
  );

  const { data: images, isLoading: attachments_isLoading } = useQuery({
    queryKey: computed(() => ["transaction_images", id.value]),
    queryFn: () => getTransactionImagesFunction(id.value),
    enabled: computed(() => !!id.value),
  });

  const uploadMutation = useMutation({
    mutationFn: uploadTransactionImageFunction,
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["transaction_images", id.value],
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteTransactionImageFunction,
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["transaction_images", id.value],
      });
    },
  });

  function uploadImage(file) {
    uploadMutation.mutate({ transactionId: id.value, file });
  }

  function deleteImage(imageId) {
    deleteMutation.mutate(imageId);
  }

  return { images, attachments_isLoading, uploadImage, deleteImage };
}
