<template>
  <v-dialog width="800">
    <form @submit.prevent="submit">
      <v-card min-height="550px">
        <v-card-text>
          <v-sheet border rounded>
            <v-container>
              <v-row dense>
                <v-col>
                  <h4 class="text-h6 font-weight-bold mb-2">
                    {{ props.isEdit ? "Edit" : "Add" }} Overage Rule
                  </h4>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col>
                  <VueDatePicker
                    v-model="note_date.value.value"
                    timezone="America/New_York"
                    model-type="yyyy-MM-dd"
                    :enable-time-picker="false"
                    auto-apply
                    format="yyyy-MM-dd"
                  ></VueDatePicker
                ></v-col>
              </v-row>
              <v-row dense
                ><v-col>
                  <v-textarea
                    clearable
                    label="Note"
                    variant="outlined"
                    v-model="note_text.value.value"
                    :rows="11"
                    no-resize
                    :error-messages="note_text.errorMessage.value"
                    :counter="254"
                  ></v-textarea> </v-col
              ></v-row>
            </v-container>
          </v-sheet>
        </v-card-text>
        <v-card-actions
          ><v-spacer></v-spacer
          ><v-btn @click="clickClose" color="secondary">Close</v-btn
          ><v-btn color="secondary" type="submit">{{
            props.isEdit ? "Save Changes" : "Add Note"
          }}</v-btn></v-card-actions
        >
      </v-card>
    </form>
  </v-dialog>
</template>
<script setup>
import { defineEmits, defineProps, watchEffect, onMounted } from "vue";
import { useField, useForm } from "vee-validate";
import VueDatePicker from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css";

const { handleSubmit } = useForm({
  validationSchema: {
    note_text(value) {
      if (value?.length >= 2 && value?.length <= 254) return true;

      return "Note needs to be at least 2 characters, and less than 254.";
    },
    note_date(value) {
      if (value) return true;

      return "Must provide a date.";
    },
  },
});

const id = useField("id");
const note_date = useField("note_date");
const note_text = useField("note_text");

const props = defineProps({
  isEdit: {
    type: Boolean,
    default: false,
  },
  passedFormData: Object,
});

const watchPassedFormData = () => {
  watchEffect(() => {
    if (props.passedFormData) {
      id.value.value = props.passedFormData.id;
      note_date.value.value = props.passedFormData.note_date;
      note_text.value.value = props.passedFormData.note_text;
    }
  });
};
const submit = handleSubmit(values => {
  if (props.isEdit) {
    emit("editNote", values);
  } else {
    emit("addNote", values);
  }
  emit("updateDialog", false);
});

const emit = defineEmits(["updateDialog", "addNote", "editNote"]);

const clickClose = () => {
  emit("updateDialog", false);
};

onMounted(() => {
  watchPassedFormData();
});
</script>
