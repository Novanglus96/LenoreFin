import { useQuery, useQueryClient, useMutation } from "@tanstack/vue-query";
import axios from "axios";
import { useMainStore } from "@/stores/main";

const apiClient = axios.create({
  baseURL: "/api/v1",
  withCredentials: false,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
    Authorization: `Bearer ${window.__APP_CONFIG__?.VITE_API_KEY}`,
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

async function getNotesFunction() {
  try {
    const response = await apiClient.get("/planning/notes/list");
    return response.data;
  } catch (error) {
    handleApiError(error, "Notes not fetched: ");
  }
}

async function createNoteFunction(newNote) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.post("/planning/notes/create", newNote);
    mainstore.showSnackbar("Note created successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Note not created: ");
  }
}

async function deleteNoteFunction(note) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.delete(
      "/planning/notes/delete/" + note.id,
    );
    mainstore.showSnackbar("Note deleted successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Note not deleted: ");
  }
}

async function updateNoteFunction(note) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.put(
      "/planning/notes/update/" + note.id,
      note,
    );
    mainstore.showSnackbar("Note updated successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Note not updated: ");
  }
}

export function useNotes() {
  const queryClient = useQueryClient();
  const { data: notes, isLoading } = useQuery({
    queryKey: ["notes"],
    queryFn: () => getNotesFunction(),
    select: response => response,
    client: queryClient,
  });

  const createNoteMutation = useMutation({
    mutationFn: createNoteFunction,
    onSuccess: () => {
      console.log("Success adding note");
      queryClient.invalidateQueries({ queryKey: ["notes"] });
    },
  });

  const deleteNoteMutation = useMutation({
    mutationFn: deleteNoteFunction,
    onSuccess: () => {
      console.log("Success deleting note");
      queryClient.invalidateQueries({ queryKey: ["notes"] });
    },
  });

  const updateNoteMutation = useMutation({
    mutationFn: updateNoteFunction,
    onSuccess: () => {
      console.log("Success updating note");
      queryClient.invalidateQueries({ queryKey: ["notes"] });
    },
  });

  async function addNote(newNote) {
    createNoteMutation.mutate(newNote);
  }

  async function removeNote(note) {
    deleteNoteMutation.mutate(note);
  }

  async function editNote(note) {
    updateNoteMutation.mutate(note);
  }

  return {
    isLoading,
    notes,
    addNote,
    removeNote,
    editNote,
  };
}
