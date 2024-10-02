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
                    {{ props.isEdit ? "Edit" : "Add" }} Contribution
                  </h4>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col>
                  <v-text-field
                    v-model="contribution.value.value"
                    variant="outlined"
                    label="Contribution"
                    density="compact"
                    :error-messages="contribution.errorMessage.value"
                    :counter="254"
                  ></v-text-field>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col cols="3"
                  ><v-text-field
                    v-model="per_paycheck.value.value"
                    variant="outlined"
                    label="Paycheck(per)"
                    density="compact"
                    :error-messages="per_paycheck.errorMessage.value"
                    type="number"
                    step="1.00"
                    prefix="$"
                    @update:modelValue="updateDifference"
                  ></v-text-field
                ></v-col>
                <v-col cols="3"
                  ><v-text-field
                    v-model="emergency_amt.value.value"
                    variant="outlined"
                    label="Emergency Amt"
                    density="compact"
                    :error-messages="emergency_amt.errorMessage.value"
                    type="number"
                    step="1.00"
                    prefix="$"
                    @update:modelValue="updateDifference"
                  ></v-text-field
                ></v-col>
                <v-col cols="3">
                  <v-text-field
                    v-model="emergency_diff.value.value"
                    variant="outlined"
                    label="Difference"
                    density="compact"
                    :error-messages="emergency_diff.errorMessage.value"
                    type="number"
                    step="1.00"
                    prefix="$"
                    disabled
                  ></v-text-field>
                </v-col>
                <v-col cols="3"
                  ><v-text-field
                    v-model="cap.value.value"
                    variant="outlined"
                    label="Cap"
                    density="compact"
                    :error-messages="cap.errorMessage.value"
                    type="number"
                    step="1.00"
                    prefix="$"
                  ></v-text-field
                ></v-col>
              </v-row>
              <v-row dense>
                <v-col
                  ><v-checkbox
                    v-model="active.value.value"
                    :error-messages="active.errorMessage.value"
                    label="Active"
                    type="checkbox"
                    :value="true"
                  ></v-checkbox
                ></v-col>
              </v-row>
            </v-container>
          </v-sheet>
        </v-card-text>
        <v-card-actions
          ><v-spacer></v-spacer
          ><v-btn @click="clickClose" color="secondary">Close</v-btn
          ><v-btn color="secondary" type="submit">{{
            props.isEdit ? "Save Changes" : "Add Contribution"
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
    contribution(value) {
      if (value?.length >= 2 && value?.length <= 254) return true;

      return "Contribution needs to be at least 2 characters, and less than 254.";
    },
    per_paycheck(value) {
      if (value == null || value === "") return "Paycheck amount is required.";
      if (parseFloat(value) < 1) return "Paycheck amount must be more than 0.";
      if (parseFloat(value) < parseFloat(emergency_amt.value.value))
        return "Paycheck amount can't be less than emergency amount.";

      return true;
    },
    emergency_amt(value) {
      if (value == null || value === "") return "Emergency amount is required.";
      if (parseFloat(value) < 0) return "Emergency amount must be positive.";
      if (parseFloat(value) > parseFloat(per_paycheck.value.value))
        return "Emergency amount can't be greater than paycheck amount.";

      return true;
    },
    cap(value) {
      if (value == null || value === "")
        return "You must specify a cap(Can be 0).";
      if (value < 0) return "Cap amount must be positive.";

      return true;
    },
  },
});

const id = useField("id");
const contribution = useField("contribution");
const per_paycheck = useField("per_paycheck");
const emergency_diff = useField("emergency_diff");
const emergency_amt = useField("emergency_amt");
const cap = useField("cap");
const active = useField("active");

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
      contribution.value.value = props.passedFormData.contribution;
      per_paycheck.value.value = props.passedFormData.per_paycheck;
      emergency_diff.value.value = props.passedFormData.emergency_diff;
      emergency_amt.value.value = props.passedFormData.emergency_amt;
      cap.value.value = props.passedFormData.cap;
      active.value.value = props.passedFormData.active;
    }
  });
};
const submit = handleSubmit(values => {
  if (props.isEdit) {
    emit("editContribution", values);
  } else {
    emit("addContribution", values);
  }
  emit("updateDialog", false);
});

const emit = defineEmits([
  "updateDialog",
  "addContribution",
  "editContribution",
]);

const clickClose = () => {
  emit("updateDialog", false);
};

const updateDifference = () => {
  if (per_paycheck.value.value && emergency_amt.value.value) {
    emergency_diff.value.value =
      parseFloat(per_paycheck.value.value) -
      parseFloat(emergency_amt.value.value);
  }
};

onMounted(() => {
  watchPassedFormData();
});
</script>
