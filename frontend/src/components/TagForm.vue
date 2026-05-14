<template>
  <v-dialog persistent width="1024">
    <form @submit.prevent="submit">
      <v-card>
        <v-card-title>
          <span class="text-h5">Add Tag</span>
        </v-card-title>
        <v-card-text>
          <v-container>
            <v-row>
              <v-col>
                <v-text-field
                  v-model="tag_name.value.value"
                  variant="outlined"
                  label="Tag Name*"
                  :error-messages="tag_name.errorMessage.value"
                ></v-text-field>
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <v-autocomplete
                  clearable
                  label="Tag Type*"
                  :items="tag_types"
                  variant="outlined"
                  :loading="tag_types_isLoading"
                  item-title="tag_type"
                  item-value="id"
                  v-model="tag_type_id.value.value"
                  :error-messages="tag_type_id.errorMessage.value"
                ></v-autocomplete>
              </v-col>
              <v-col>
                <v-autocomplete
                  clearable
                  label="Parent"
                  :items="parent_tags"
                  variant="outlined"
                  :loading="parent_tags_isLoading"
                  item-title="tag_name"
                  item-value="id"
                  v-model="parent_id.value.value"
                ></v-autocomplete>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="text" @click="closeDialog">Close</v-btn>
          <v-btn color="primary" variant="text" type="submit">Save</v-btn>
        </v-card-actions>
      </v-card>
    </form>
  </v-dialog>
</template>
<script setup>
  import { defineEmits } from "vue";
  import { useTags, useParentTags } from "@/composables/tagsComposable";
  import { useTagTypes } from "@/composables/tagtypesComposable";
  import { useField, useForm } from "vee-validate";
  import * as yup from "yup";

  const schema = yup.object({
    tag_name: yup.string().required("Tag name is required."),
    tag_type_id: yup
      .number()
      .typeError("Tag type is required.")
      .required("Tag type is required."),
    parent_id: yup.number().nullable().notRequired(),
  });

  const { handleSubmit, resetForm } = useForm({ validationSchema: schema });

  const tag_name = useField("tag_name");
  const tag_type_id = useField("tag_type_id");
  const parent_id = useField("parent_id");

  const { tag_types, isLoading: tag_types_isLoading } = useTagTypes();
  const { addTag } = useTags();
  const { parent_tags, isLoading: parent_tags_isLoading } = useParentTags();

  const emit = defineEmits(["updateDialog"]);

  const submit = handleSubmit(values => {
    addTag(values);
    closeDialog();
  });

  const closeDialog = () => {
    resetForm();
    emit("updateDialog", false);
  };
</script>
