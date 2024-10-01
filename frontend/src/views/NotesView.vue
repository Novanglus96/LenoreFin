<template>
  <v-card variant="outlined" :elevation="4" class="bg-white">
    <template v-slot:append>
      <v-tooltip text="Add Note" location="top">
        <template v-slot:activator="{ props }">
          <v-btn
            icon="mdi-note-plus"
            flat
            variant="plain"
            v-bind="props"
            @click="addNoteDialog = true"
          ></v-btn>
        </template>
      </v-tooltip>
    </template>
    <NoteForm
      v-model="addNoteDialog"
      key="0"
      :isEdit="false"
      @update-dialog="updateAddDialog"
      @add-note="clickAddNote"
      :passedFormData="newNoteData"
    />
    <template v-slot:title>
      <span class="text-subtitle-2 text-secondary">Notes</span>
    </template>
    <template v-slot:text>
      <vue3-datatable
        :rows="notes ? notes : []"
        :columns="columns"
        :loading="isLoading"
        :totalRows="notes ? notes.length : 0"
        :isServerMode="false"
        pageSize="10"
        :hasCheckbox="false"
        :stickyHeader="true"
        firstArrow="First"
        lastArrow="Last"
        previousArrow="Prev"
        nextArrow="Next"
        :showNumbersCount="3"
        noDataContent="No notes"
        search=""
        ref="notes_table"
        height="650px"
        :pageSizeOptions="[60]"
        :showPageSize="false"
        paginationInfo="Showing {0} to {1} of {2} notes"
        @change="pageChanged"
        class="alt-pagination"
        rowClass="cursor-pointer"
        @rowClick="rowClick"
      >
        <template #note_text="row">
          <span :style="clampedStyle" class="text-body-2">{{
            row.value.note_text
          }}</span>
        </template>
        <template #edit="row">
          <v-btn variant="plain" icon @click="clickEditButton(row.value)"
            ><v-icon icon="mdi-pencil"></v-icon
          ></v-btn>
          <NoteForm
            v-model="editNoteDialog"
            :key="row.value.id"
            :isEdit="true"
            @update-dialog="updateEditDialog"
            :passedFormData="selectedNote"
            @edit-note="clickEditNote"
          />
        </template>
        <template #delete="row">
          <v-btn variant="plain" icon
            ><v-icon
              icon="mdi-delete"
              @click="clickDeleteButton(row.value)"
            ></v-icon
          ></v-btn>
          <v-dialog v-model="deleteNoteDialog" :key="row.value.id" width="400"
            ><v-card
              ><v-card-title>Delete Note?</v-card-title
              ><v-card-text
                ><span :style="clampedStyle" class="text-body-2">{{
                  selectedNote.note_text
                }}</span></v-card-text
              >
              <v-card-actions
                ><v-btn @click="deleteNoteDialog = false">Close</v-btn
                ><v-btn @click="clickDeleteNote(selectedNote)"
                  >Delete</v-btn
                ></v-card-actions
              ></v-card
            ></v-dialog
          >
        </template>
      </vue3-datatable>
    </template>
  </v-card>
</template>
<script setup>
import { ref } from "vue";
import Vue3Datatable from "@bhplugin/vue3-datatable";
import "@bhplugin/vue3-datatable/dist/style.css";
import { useNotes } from "@/composables/notesComposable";
import NoteForm from "@/components/NoteForm.vue";

const { notes, addNote, removeNote, editNote, isLoading } = useNotes();
const addNoteDialog = ref(false);
const editNoteDialog = ref(false);
const deleteNoteDialog = ref(false);
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
  note_date: "2024-10-01",
  note_text: "Test",
});
const selectedNote = ref(null);

const columns = ref([
  { field: "id", title: "ID", isUnique: true, hide: true },
  { field: "note_date", title: "Date", width: "150px" },
  { field: "note_text", title: "Note" },
  { field: "edit", title: "Edit", width: "40px" },
  { field: "delete", title: "Delete", width: "40px" },
]);

const updateAddDialog = () => {
  addNoteDialog.value = false;
};

const updateEditDialog = () => {
  editNoteDialog.value = false;
};

const clickAddNote = note => {
  addNote(note);
};

const clickEditNote = note => {
  editNote(note);
};

const clickEditButton = note => {
  selectedNote.value = note;
  editNoteDialog.value = true;
};
const clickDeleteButton = note => {
  selectedNote.value = note;
  deleteNoteDialog.value = true;
};
const clickDeleteNote = note => {
  removeNote(note);
  deleteNoteDialog.value = false;
};
</script>
