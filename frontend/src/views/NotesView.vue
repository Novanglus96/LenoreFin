<template>
  <v-row class="pa-1 ga-1" no-gutters>
    <v-col class="rounded">
      <v-card variant="outlined" :elevation="4" class="bg-surface">
        <v-card-title class="text-left">
          <span class="text-subtitle-2 text-primary">Notes</span>
          <v-tooltip text="Add Note" location="top">
            <template v-slot:activator="{ props }">
              <v-btn
                icon="mdi-note-plus"
                flat
                variant="plain"
                v-bind="props"
                @click="addNoteDialog = true"
                size="small"
              ></v-btn>
            </template>
          </v-tooltip>
          <NoteForm
            v-model="addNoteDialog"
            key="0"
            :isEdit="false"
            @update-dialog="updateAddDialog"
            @add-note="clickAddNote"
            :passedFormData="newNoteData"
          />
        </v-card-title>
        <v-card-text class="ma-0 pa-0 ga-0">
          <v-data-table
            :headers="displayHeaders"
            :items="notes ? notes : []"
            :items-length="notes ? notes.length : 0"
            :loading="isLoading"
            item-value="id"
            v-model:items-per-page="itemsPerPage"
            v-model:page="page"
            :items-per-page-options="[
              {
                value: 10,
                title: 10,
              },
            ]"
            items-per-page-text="Notes per page"
            no-data-text="No notes!"
            loading-text="Loading notes..."
            disable-sort
            :show-select="true"
            fixed-footer
            striped="odd"
            density="compact"
            width="100%"
            :header-props="{ class: 'font-weight-bold bg-secondary' }"
            v-model="selectedNote"
            select-strategy="single"
            return-object
            :row-props="getRowProps"
            class="bg-background"
          >
            <template v-slot:top>
              <div class="d-flex align-center">
                <v-btn
                  variant="plain"
                  icon
                  @click="editNoteDialog = true"
                  :disabled="selectedNote.length === 0"
                >
                  <v-icon icon="mdi-pencil"></v-icon>
                </v-btn>
                <NoteForm
                  v-model="editNoteDialog"
                  :key="editedNote ? editedNote.id : 0"
                  :isEdit="true"
                  @update-dialog="updateEditDialog"
                  :passedFormData="editedNote"
                  @edit-note="clickEditNote"
                />
                <v-btn
                  variant="plain"
                  icon
                  :disabled="selectedNote.length === 0"
                >
                  <v-icon
                    icon="mdi-delete"
                    @click="deleteNoteDialog = true"
                    color="error"
                  ></v-icon>
                </v-btn>
                <v-dialog
                  v-model="deleteNoteDialog"
                  :key="editedNote ? editedNote.id : 0"
                  width="400"
                >
                  <v-card>
                    <v-card-title>Delete Note?</v-card-title>
                    <v-card-text>
                      <span :style="clampedStyle" class="text-body-2">
                        {{ editedNote.note_text }}
                      </span>
                    </v-card-text>
                    <v-card-actions>
                      <v-btn @click="deleteNoteDialog = false">Close</v-btn>
                      <v-btn @click="clickDeleteNote(editedNote)">Delete</v-btn>
                    </v-card-actions>
                  </v-card>
                </v-dialog>
              </div>
            </template>
            <template v-slot:bottom>
              <div class="text-center pt-2">
                <v-pagination v-model="page" :length="pageCount"></v-pagination>
              </div>
            </template>
            <!-- Mobile View -->
            <template v-slot:[`item.mobile`]="{ item }">
              <v-container class="ma-0 pa-0 ga-0">
                <v-row dense class="ma-0 pa-0 ga-0">
                  <v-col
                    class="ma-0 pa-0 ga-0 font-weight-bold text-center"
                    cols="3"
                  >
                    {{ formatDate(item.note_date, true) }}
                  </v-col>
                  <v-col class="ma-0 pa-0 ga-0" cols="9">
                    {{ item.note_text }}
                  </v-col>
                </v-row>
              </v-container>
            </template>
          </v-data-table>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>
<script setup>
  import { ref, computed, watch } from "vue";
  import { useNotes } from "@/composables/notesComposable";
  import NoteForm from "@/components/NoteForm.vue";
  import { useDisplay } from "vuetify";

  const page = ref(1);
  const itemsPerPage = ref(10);
  const { mdAndUp } = useDisplay();
  const editedNote = ref({ id: 0 });

  const { notes, addNote, removeNote, editNote, isLoading } = useNotes();
  const addNoteDialog = ref(false);
  const editNoteDialog = ref(false);
  const deleteNoteDialog = ref(false);

  // Date variables...
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, "0");
  const day = String(today.getDate()).padStart(2, "0");
  const formattedDate = `${year}-${month}-${day}`;

  const clampedStyle = {
    whiteSpace: "pre-line",
    display: "-webkit-box",
    WebkitLineClamp: 3, // Limit to 3 lines
    WebkitBoxOrient: "vertical",
    overflow: "hidden",
    textOverflow: "ellipsis", // Add "..." at the end if text is truncated
  };
  const newNoteData = ref({
    id: 0,
    note_date: formattedDate,
    note_text: null,
  });
  const selectedNote = ref([]);

  const headers = ref([
    { title: "Date", key: "note_date", width: "150px" },
    { title: "Note", key: "note_text" },
  ]);
  const displayHeaders = computed(() => {
    if (mdAndUp.value) {
      return headers.value;
    }
    // For small screens, use your single mobile column
    return [{ title: "", key: "mobile" }];
  });

  const updateAddDialog = () => {
    addNoteDialog.value = false;
  };

  const updateEditDialog = () => {
    editNoteDialog.value = false;
  };

  const clickAddNote = note => {
    addNote(note);
  };

  const clickEditNote = () => {
    editNote(editedNote.value);
    selectedNote.value = [];
  };

  const clickDeleteNote = note => {
    removeNote(note);
    deleteNoteDialog.value = false;
    selectedNote.value = [];
  };

  const pageCount = computed(() =>
    notes.value && itemsPerPage.value
      ? Math.ceil(notes.value.length / itemsPerPage.value)
      : 1,
  );

  watch(
    () => selectedNote.value,
    val => {
      if (val) {
        editedNote.value = val[0];
      }
    },
  );

  const formatDate = (input, padDay = false) => {
    // Normalize input to a Date object
    const date = input instanceof Date ? input : new Date(input);

    if (isNaN(date)) {
      console.warn("Invalid date:", input);
      return "";
    }

    const month = date.toLocaleString("en-US", { month: "short" }); // 'Sep'
    const day = date.getDate(); // 16

    return `${month}-${padDay ? String(day).padStart(2, "0") : day}`;
  };
  function getRowProps({ item }) {
    let rowformat = "";
    const isSelected = selectedNote.value.some(sel => sel.id === item.id);
    if (isSelected) {
      rowformat += "bg-primary-lighten-3";
    }
    return {
      class: rowformat,
    };
  }
</script>
