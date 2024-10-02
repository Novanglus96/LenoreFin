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
                <v-col cols="10">
                  <v-text-field
                    v-model="rule.value.value"
                    variant="outlined"
                    label="Rule"
                    density="compact"
                    :error-messages="rule.errorMessage.value"
                    :counter="254"
                  ></v-text-field
                ></v-col>
                <v-col cols="2">
                  <v-text-field
                    v-model="order.value.value"
                    variant="outlined"
                    label="Order"
                    density="compact"
                    :error-messages="order.errorMessage.value"
                    type="number"
                    step="1"
                  ></v-text-field>
                </v-col>
              </v-row>
              <v-row dense
                ><v-col>
                  <v-textarea
                    clearable
                    label="Cap"
                    variant="outlined"
                    v-model="cap.value.value"
                    :rows="9"
                    no-resize
                    :error-messages="cap.errorMessage.value"
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

const { handleSubmit } = useForm({
  validationSchema: {
    rule(value) {
      if (value?.length >= 2 && value?.length <= 254) return true;

      return "Rule needs to be at least 2 characters, and less than 254.";
    },
    order(value) {
      if (value) return true;

      return "Order is required.";
    },
    cap(value) {
      if (value) return true;

      return "Cap is required.";
    },
  },
});

const id = useField("id");
const rule = useField("rule");
const order = useField("order");
const cap = useField("cap");

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
      rule.value.value = props.passedFormData.rule;
      order.value.value = props.passedFormData.order;
      cap.value.value = props.passedFormData.cap;
    }
  });
};
const submit = handleSubmit(values => {
  if (props.isEdit) {
    emit("editContributionRule", values);
  } else {
    emit("addContributionRule", values);
  }
  emit("updateDialog", false);
});

const emit = defineEmits([
  "updateDialog",
  "addContributionRule",
  "editContributionRule",
]);

const clickClose = () => {
  emit("updateDialog", false);
};

onMounted(() => {
  watchPassedFormData();
});
</script>
