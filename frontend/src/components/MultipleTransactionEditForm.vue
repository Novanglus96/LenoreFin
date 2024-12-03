<template>
  <v-dialog persistent width="512">
    <v-card>
      <form @submit.prevent="submit">
        <v-card-title
          ><span class="text-h5"
            >Edit
            {{ props.transactionIds ? props.transactionIds.length : 0 }}
            Transactions</span
          ></v-card-title
        ><v-card-text
          ><v-date-input
            label="New Date"
            prepend-icon=""
            prepend-inner-icon="$calendar"
            variant="outlined"
            :error-messages="new_date.errorMessage.value"
            v-model="new_date.value.value"
            density="compact"
          ></v-date-input></v-card-text
        ><v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="secondary" variant="text" @click="closeDialog">
            Close
          </v-btn>
          <v-btn color="secondary" variant="text" type="submit" @click="submit">
            Update
          </v-btn>
        </v-card-actions>
      </form></v-card
    >
  </v-dialog>
</template>
<script setup>
import { defineEmits, defineProps, onMounted, watchEffect } from "vue";
import { useField, useForm } from "vee-validate";
import { useTransactions } from "@/composables/transactionsComposable";

const { mutliEditTransactions } = useTransactions();

const { handleSubmit } = useForm({
  validationSchema: {
    new_date(value) {
      if (value) return true;

      return "Date is required.";
    },
  },
});

const transaction_ids = useField("transaction_ids");
const new_date = useField("new_date");

const props = defineProps({
  transactionIds: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["updateDialog"]);

const closeDialog = () => {
  emit("updateDialog", false);
};

const watchPassedFormData = () => {
  watchEffect(() => {
    if (props.transactionIds) {
      transaction_ids.value.value = props.transactionIds;
    }
  });
};

const submit = handleSubmit(values => {
    mutliEditTransactions(values);
  emit("updateDialog", false);
});

onMounted(() => {
  watchPassedFormData();
});
</script>
