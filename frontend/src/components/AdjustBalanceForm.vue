<template>
  <v-dialog width="400">
    <form @submit.prevent="submit">
      <v-card>
        <v-card-title>Adjust Balance</v-card-title>
        <v-card-text>
          <v-container>
            <v-row density>
              <v-col>
                <v-text-field
                  v-model="currentBalance"
                  variant="outlined"
                  label="Current Balance"
                  prefix="$"
                  disabled
                ></v-text-field>
              </v-col>
            </v-row>
            <v-row density>
              <v-col>
                <v-text-field
                  v-model="new_balance.value.value"
                  variant="outlined"
                  label="New Balance*"
                  :error-messages="new_balance.errorMessage.value"
                  prefix="$"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="emit('updateDialog', false)" color="primary">Close</v-btn>
          <v-btn color="primary" type="submit">Adjust</v-btn>
        </v-card-actions>
      </v-card>
    </form>
  </v-dialog>
</template>
<script setup>
  import { defineEmits, defineProps, ref, watch } from "vue";
  import { useTransactions } from "@/composables/transactionsComposable";
  import { useField, useForm } from "vee-validate";
  import * as yup from "yup";

  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, "0");
  const day = String(today.getDate()).padStart(2, "0");
  const formattedDate = `${year}-${month}-${day}`;

  const props = defineProps({ account: Object });
  const emit = defineEmits(["updateDialog"]);
  const { addTransaction } = useTransactions();

  const currentBalance = ref(props.account.balance);
  watch(
    () => props.account.balance,
    newValue => {
      currentBalance.value = newValue;
    },
  );

  const schema = yup.object({
    new_balance: yup
      .number()
      .typeError("New balance is required.")
      .required("New balance is required."),
  });

  const { handleSubmit, resetForm } = useForm({ validationSchema: schema });
  const new_balance = useField("new_balance");

  const submit = handleSubmit(values => {
    const diff = parseFloat(
      (values.new_balance - currentBalance.value).toFixed(2),
    );
    addTransaction({
      id: 0,
      status_id: 2,
      transaction_type_id: diff < 0 ? 1 : 2,
      transaction_date: formattedDate,
      memo: "",
      source_account_id: props.account.id,
      destination_account_id: null,
      edit_date: formattedDate,
      add_date: formattedDate,
      details: [
        {
          tag_id: 4,
          tag_amt: 0,
          tag_pretty_name: "Balance Adjustment",
          tag_full_toggle: true,
        },
      ],
      total_amount: diff,
      description: "Balance Adjustment",
    });
    resetForm();
    emit("updateDialog", false);
  });
</script>
