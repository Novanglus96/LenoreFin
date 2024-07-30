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

export async function uploadFile(mappings, file) {
  const mainstore = useMainStore();
  try {
    const formData = new FormData();
    formData.append("import_file", file);
    formData.append("payload", JSON.stringify(mappings));
    const response = await apiClient.post(
      "/administration/file-imports/create",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      },
    );
    mainstore.showSnackbar(
      "File import ID #" + response.data.id + " started!",
      "success",
    );
    return response.data;
  } catch (error) {
    handleApiError(error, "File not imported: ");
  }
}
