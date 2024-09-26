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
                    {{ props.isEdit ? "Edit" : "Add" }} Calculator Rule
                  </h4>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col>
                  <v-text-field
                    v-model="name.value.value"
                    :counter="254"
                    :error-messages="name.errorMessage.value"
                    label="Name*"
                    variant="outlined"
                    density="comfortable"
                  ></v-text-field>

                  <v-autocomplete
                    clearable
                    chips
                    multiple
                    label="Tag(s)*"
                    :items="tag_items"
                    variant="outlined"
                    :loading="tags_isLoading"
                    item-title="tag_name"
                    item-value="id"
                    v-model="tag_ids.value.value"
                    density="comfortable"
                    :error-messages="tag_ids.errorMessage.value"
                  >
                    <template v-slot:item="{ props, item }">
                      <v-list-item
                        v-bind="props"
                        :title="
                          item.raw.parent
                            ? item.raw.parent.tag_name
                            : item.raw.tag_name
                        "
                        :subtitle="item.raw.parent ? item.raw.tag_name : null"
                      >
                        <template v-slot:prepend>
                          <v-icon
                            icon="mdi-tag"
                            :color="tagColor(item.raw.tag_type.id)"
                          ></v-icon>
                        </template>
                      </v-list-item>
                    </template>
                  </v-autocomplete>

                  <v-autocomplete
                    clearable
                    label="Funding Source*"
                    :items="accounts"
                    variant="outlined"
                    :loading="accounts_isLoading"
                    item-title="account_name"
                    item-value="id"
                    v-model="source_account_id.value.value"
                    :error-messages="source_account_id.errorMessage.value"
                    density="comfortable"
                  >
                    <template v-slot:item="{ props, item }">
                      <v-list-item
                        v-bind="props"
                        :title="item.raw.account_name"
                        :subtitle="item.raw.bank.bank_name"
                      >
                        <template v-slot:prepend>
                          <v-icon :icon="item.raw.account_type.icon"></v-icon>
                        </template>
                      </v-list-item>
                    </template>
                  </v-autocomplete>

                  <v-autocomplete
                    clearable
                    label="Funding Destination*"
                    :items="accounts"
                    variant="outlined"
                    :loading="accounts_isLoading"
                    item-title="account_name"
                    item-value="id"
                    v-model="destination_account_id.value.value"
                    :error-messages="destination_account_id.errorMessage.value"
                    density="comfortable"
                  >
                    <template v-slot:item="{ props, item }">
                      <v-list-item
                        v-bind="props"
                        :title="item.raw.account_name"
                        :subtitle="item.raw.bank.bank_name"
                      >
                        <template v-slot:prepend>
                          <v-icon :icon="item.raw.account_type.icon"></v-icon>
                        </template>
                      </v-list-item>
                    </template>
                  </v-autocomplete>
                </v-col>
              </v-row>
            </v-container>
          </v-sheet>
        </v-card-text>
        <v-card-actions
          ><v-spacer></v-spacer
          ><v-btn @click="clickClose" color="secondary">Close</v-btn
          ><v-btn color="secondary" type="submit">{{
            props.isEdit ? "Save Changes" : "Add Rule"
          }}</v-btn></v-card-actions
        >
      </v-card>
    </form>
  </v-dialog>
</template>
<script setup>
import { defineEmits, defineProps, watchEffect, onMounted } from "vue";
import { useField, useForm } from "vee-validate";
import { useTags } from "@/composables/tagsComposable";
import { useAccounts } from "@/composables/accountsComposable";
import { useCalculationRule } from "@/composables/calculatorComposable";

const { tags: tag_items, isLoading: tags_isLoading } = useTags();
const { accounts, isLoading: accounts_isLoading } = useAccounts();
const { addCalculationRule, editCalculationRule } = useCalculationRule();

const { handleSubmit, handleReset } = useForm({
  validationSchema: {
    name(value) {
      if (value?.length >= 2 && value?.length <= 254) return true;

      return "Name needs to be at least 2 characters, and less than 254.";
    },
    source_account_id(value) {
      if (value && value != destination_account_id.value.value) return true;

      return "Select a funding source.  Source and destination can't be the same.";
    },
    destination_account_id(value) {
      if (value && value != source_account_id.value.value) return true;

      return "Select a funding destination.  Source and destination can't be the same.";
    },
    tag_ids(value) {
      if (value?.length > 0) return true;

      return "Select at least 1 tag";
    },
  },
});

const id = useField("id");
const name = useField("name");
const source_account_id = useField("source_account_id");
const destination_account_id = useField("destination_account_id");
const tag_ids = useField("tag_ids");

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
      name.value.value = props.passedFormData.name;
      tag_ids.value.value = props.passedFormData.tag_ids
        ? JSON.parse(props.passedFormData.tag_ids)
        : [];
      source_account_id.value.value = props.passedFormData.source_account_id;
      destination_account_id.value.value =
        props.passedFormData.destination_account_id;
    }
  });
};
const submit = handleSubmit(values => {
  if (props.isEdit) {
    editCalculationRule(values);
  } else {
    addCalculationRule(values);
  }
  emit("updateDialog", false);
  handleReset();
});

const emit = defineEmits(["updateDialog"]);

const clickClose = () => {
  if (!props.isEdit) {
    handleReset();
  }
  emit("updateDialog", false);
};

const tagColor = typeID => {
  if (typeID == 1) {
    return "red";
  } else if (typeID == 2) {
    return "green";
  } else if (typeID == 3) {
    return "grey";
  }
};

onMounted(() => {
  watchPassedFormData();
});
</script>
