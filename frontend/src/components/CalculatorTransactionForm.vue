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
                    {{ props.isEdit ? "Edit" : "Add" }} Transfer
                  </h4>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col cols="3">
                  <VueDatePicker
                    v-model="transaction_date.value.value"
                    timezone="America/New_York"
                    model-type="yyyy-MM-dd"
                    :enable-time-picker="false"
                    auto-apply
                    format="yyyy-MM-dd"
                  ></VueDatePicker>
                </v-col>
                <v-col cols="3"
                  ><v-text-field
                    v-model="total_amount.value.value"
                    variant="outlined"
                    :label="props.isEdit ? 'New Amount*' : 'Amount*'"
                    prefix="$"
                    type="number"
                    step="1.00"
                    density="compact"
                    class="mb-0"
                    :error-messages="total_amount.errorMessage.value"
                  ></v-text-field
                  ><v-text-field
                    v-model="oldTotal"
                    variant="outlined"
                    label="Old Amount"
                    prefix="$"
                    type="number"
                    step="1.00"
                    density="compact"
                    class="mt-0"
                    :disabled="true"
                    v-if="props.isEdit"
                  ></v-text-field
                ></v-col>
                <v-col cols="6">
                  <v-text-field
                    v-model="description.value.value"
                    :counter="254"
                    :error-messages="description.errorMessage.value"
                    label="Name*"
                    variant="outlined"
                    density="compact"
                  ></v-text-field></v-col></v-row
              ><v-row
                ><v-col cols="6">
                  <v-autocomplete
                    clearable
                    label="Source Account*"
                    :items="accounts"
                    variant="outlined"
                    :loading="accounts_isLoading"
                    item-title="account_name"
                    item-value="id"
                    v-model="source_account_id.value.value"
                    :error-messages="source_account_id.errorMessage.value"
                    density="comfortable"
                    :disabled="true"
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
                    label="Destination Account*"
                    :items="accounts"
                    variant="outlined"
                    :loading="accounts_isLoading"
                    item-title="account_name"
                    item-value="id"
                    v-model="destination_account_id.value.value"
                    :error-messages="destination_account_id.errorMessage.value"
                    density="comfortable"
                    :disabled="true"
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
                <v-col cols="6"
                  ><v-textarea
                    clearable
                    label="Memo"
                    variant="outlined"
                    v-model="memo.value.value"
                    :rows="11"
                    no-resize
                    :counter="254"
                    :error-messages="memo.errorMessage.value"
                  ></v-textarea
                ></v-col>
              </v-row>
            </v-container>
          </v-sheet>
        </v-card-text>
        <v-card-actions
          ><v-spacer></v-spacer
          ><v-btn @click="clickClose" color="secondary">Close</v-btn
          ><v-btn color="secondary" type="submit">{{
            props.isEdit ? "Edit Transfer" : "Add Transfer"
          }}</v-btn></v-card-actions
        >
      </v-card>
    </form>
  </v-dialog>
</template>
<script setup>
import { ref, defineEmits, defineProps, watchEffect, onMounted } from "vue";
import { useField, useForm } from "vee-validate";
import { useAccounts } from "@/composables/accountsComposable";
import { useTransactions } from "@/composables/transactionsComposable";
import VueDatePicker from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css";

const { accounts, isLoading: accounts_isLoading } = useAccounts();
const { addTransaction, editTransaction } = useTransactions();
const oldTotal = ref(null);

const { handleSubmit, handleReset } = useForm({
  validationSchema: {
    description(value) {
      if (value?.length >= 2 && value?.length <= 254) return true;

      return "Description needs to be at least 2 characters, and less than 254.";
    },
    source_account_id(value) {
      if (value && value != destination_account_id.value.value) return true;

      return "Select a source account.  Source and destination can't be the same.";
    },
    destination_account_id(value) {
      if (value && value != source_account_id.value.value) return true;

      return "Select a destination account.  Source and destination can't be the same.";
    },
    memo(value) {
      if (value?.length >= 2 && value?.length <= 254) return true;

      return "Memo needs to be at least 2 characters, and less than 254.";
    },
    total_amount(value) {
      if (value) return true;

      return "Amount is required.";
    },
    transaction_date(value) {
      if (value) return true;

      return "Transaction date is required.";
    },
    pretty_total(value) {
      if (value || !props.isEdit) return true;

      return "Amount is required.";
    },
  },
});

const description = useField("description");
const source_account_id = useField("source_account_id");
const destination_account_id = useField("destination_account_id");
const total_amount = useField("total_amount");
const memo = useField("memo");
const transaction_date = useField("transaction_date");
const pretty_total = useField("pretty_total");
const id = useField("id");
const status_id = useField("status_id");
const edit_date = useField("edit_date");
const add_date = useField("add_date");
const transaction_type_id = useField("transaction_type_id");
const details = useField("details");

const props = defineProps({
  isEdit: {
    type: Boolean,
    default: false,
  },
  passedFormData: Object,
  newTotal: Number,
  newMemo: String,
});

const watchPassedFormData = () => {
  watchEffect(() => {
    if (props.passedFormData) {
      description.value.value = props.passedFormData.description;
      source_account_id.value.value = props.passedFormData.source_account_id;
      destination_account_id.value.value =
        props.passedFormData.destination_account_id;
      memo.value.value = props.newMemo
        ? (props.passedFormData.memo + "\n" + props.newMemo).trim()
        : props.passedFormData.memo;
      total_amount.value.value = props.newTotal
        ? parseFloat(props.newTotal) +
          parseFloat(props.passedFormData.total_amount)
        : props.passedFormData.total_amount;
      transaction_date.value.value = props.passedFormData.transaction_date;
      oldTotal.value = props.passedFormData.total_amount;
      pretty_total.value.value = props.newTotal
        ? parseFloat(props.newTotal) +
          parseFloat(props.passedFormData.total_amount)
        : props.passedFormData.total_amount;
      id.value.value = props.passedFormData.id ? props.passedFormData.id : 0;
      status_id.value.value = props.passedFormData.status
        ? props.passedFormData.status.id
        : 1;
      edit_date.value.value = props.passedFormData.edit_date;
      add_date.value.value = props.passedFormData.add_date;
      transaction_type_id.value.value = props.passedFormData.transaction_type
        ? props.passedFormData.transaction_type.id
        : 3;
      details.value.value = [
        {
          tag_amt: props.newTotal
            ? parseFloat(props.newTotal) +
              parseFloat(props.passedFormData.total_amount)
            : props.passedFormData.total_amount,
          tag_pretty_name: "Transfer",
          tag_id: 34,
          tag_full_toggle: true,
        },
      ];
    }
  });
};
const submit = handleSubmit(values => {
  if (props.isEdit) {
    editTransaction(values);
  } else {
    addTransaction(values);
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

onMounted(() => {
  watchPassedFormData();
});
</script>
