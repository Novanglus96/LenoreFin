<template>
  <v-dialog persistent width="1024">
    <v-card>
      <v-card-title>
        <span class="text-h5" v-if="props.isEdit == false">
          Add Transaction
        </span>
        <span class="text-h5" v-else>Edit Transaction</span>
        <v-icon
          v-if="props.passedFormData.reminder"
          icon="mdi-bell"
          color="amber"
        ></v-icon>
      </v-card-title>

      <v-card-text>
        <form @submit.prevent="submit">
          <v-tabs v-model="tab" color="accent">
            <v-tab value="trans" density="compact">Transaction Details</v-tab>
            <v-tab value="pay" density="compact">Paycheck Info</v-tab>
            <v-tab value="attachments" density="compact">Attachments</v-tab>
          </v-tabs>
          <v-window v-model="tab">
            <v-window-item value="trans">
              <v-container>
                <v-row dense>
                  <v-col>
                    <VueDatePicker
                      v-model="transaction_date.value.value"
                      timezone="America/New_York"
                      model-type="yyyy-MM-dd"
                      :enable-time-picker="false"
                      auto-apply
                      format="yyyy-MM-dd"
                      :state="transaction_date.errorMessage.value ? false : null"
                    ></VueDatePicker>
                    <span
                      v-if="transaction_date.errorMessage.value"
                      class="text-error text-caption"
                    >
                      {{ transaction_date.errorMessage.value }}
                    </span>
                  </v-col>
                  <v-col></v-col>
                </v-row>
                <v-row dense>
                  <v-col>
                    <v-autocomplete
                      clearable
                      label="Transaction Type*"
                      :items="transaction_types"
                      variant="outlined"
                      :loading="transaction_types_isLoading"
                      item-title="transaction_type"
                      item-value="id"
                      v-model="transaction_type_id.value.value"
                      :error-messages="transaction_type_id.errorMessage.value"
                      :disabled="props.isEdit"
                      density="compact"
                    ></v-autocomplete>
                  </v-col>
                  <v-col>
                    <v-autocomplete
                      clearable
                      label="Transaction Status*"
                      :items="transaction_statuses"
                      variant="outlined"
                      :loading="transaction_statuses_isLoading"
                      item-title="transaction_status"
                      item-value="id"
                      v-model="status_id.value.value"
                      :error-messages="status_id.errorMessage.value"
                      density="compact"
                    ></v-autocomplete>
                  </v-col>
                </v-row>
                <v-row dense>
                  <v-col cols="3">
                    <v-text-field
                      v-model="amount.value.value"
                      variant="outlined"
                      label="Amount*"
                      :error-messages="amount.errorMessage.value"
                      prefix="$"
                      type="number"
                      step="1.00"
                      @blur="formatAmount"
                      density="compact"
                    >
                      <template v-slot:append-inner>
                        <v-tooltip text="Calculator" location="top">
                          <template v-slot:activator="{ props }">
                            <v-btn
                              icon="mdi-calculator-variant"
                              variant="text"
                              @click="showAmountCalculator = true"
                              v-bind="props"
                            ></v-btn>
                          </template>
                        </v-tooltip>
                      </template>
                    </v-text-field>
                    <CalculatorWidget
                      v-model="showAmountCalculator"
                      :amount="amount.value.value"
                      @update-dialog="updateShowAmountCalculator"
                      @update-amount="updateAmount"
                      key="amount"
                    />
                  </v-col>
                  <v-col cols="3">
                    <v-text-field
                      v-model="checkNumber.value.value"
                      variant="outlined"
                      label="Check #"
                      type="number"
                      density="compact"
                      v-if="transaction_type_id.value.value != 3"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="6">
                    <v-combobox
                      v-model="description.value.value"
                      :items="
                        descriptionHistory.map(item => item.description_pretty)
                      "
                      label="Description*"
                      clearable
                      hide-no-data
                      hide-selected
                      :loading="description_history_isLoading"
                      variant="outlined"
                      :error-messages="description.errorMessage.value"
                      density="compact"
                      auto-select-first="exact"
                      return-object="false"
                    />
                  </v-col>
                </v-row>
                <v-row dense>
                  <v-col>
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
                      density="compact"
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
                  <v-col>
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
                      v-if="transaction_type_id.value.value == 3"
                      density="compact"
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
                <v-row dense>
                  <v-col>
                    <TagTable
                      :tags="details"
                      :totalAmount="parseFloat(amount.value.value)"
                      @tag-table-updated="tagsUpdated"
                    />
                  </v-col>
                  <v-col>
                    <v-textarea
                      clearable
                      label="Memo"
                      variant="outlined"
                      v-model="memo.value.value"
                      :rows="11"
                      no-resize
                    ></v-textarea>
                  </v-col>
                </v-row>
              </v-container>
            </v-window-item>
            <v-window-item value="pay">
              <v-container>
                <v-row dense>
                  <v-col>
                    <v-checkbox
                      v-model="is_paycheck.value.value"
                      label="Is this a Paycheck?"
                      @update:model-value="selectPaycheckChange"
                      :disabled="transaction_type_id.value.value != 2"
                    ></v-checkbox>
                  </v-col>
                  <v-col></v-col>
                </v-row>
                <v-row dense>
                  <v-col>
                    <v-text-field
                      v-model="gross.value.value"
                      variant="outlined"
                      label="Gross*"
                      :error-messages="gross.errorMessage.value"
                      prefix="$"
                      type="number"
                      step="1.00"
                      @blur="() => { if (gross.value.value) gross.value.value = formatCurrencyNoSymbol(gross.value.value); }"
                      density="compact"
                      :disabled="!is_paycheck.value.value"
                    ></v-text-field>
                  </v-col>
                  <v-col>
                    <v-text-field
                      v-model="amount.value.value"
                      variant="outlined"
                      label="Net*"
                      :error-messages="amount.errorMessage.value"
                      prefix="$"
                      type="number"
                      step="1.00"
                      @blur="formatAmount"
                      density="compact"
                      :disabled="!is_paycheck.value.value"
                    ></v-text-field>
                  </v-col>
                  <v-col>
                    <v-text-field
                      v-model="taxes.value.value"
                      variant="outlined"
                      label="Taxes*"
                      :error-messages="taxes.errorMessage.value"
                      prefix="$"
                      type="number"
                      step="1.00"
                      @blur="() => { if (taxes.value.value) taxes.value.value = formatCurrencyNoSymbol(taxes.value.value); }"
                      density="compact"
                      :disabled="!is_paycheck.value.value"
                    ></v-text-field>
                  </v-col>
                </v-row>
                <v-row dense>
                  <v-col>
                    <v-text-field
                      v-model="health.value.value"
                      variant="outlined"
                      label="Health*"
                      :error-messages="health.errorMessage.value"
                      prefix="$"
                      type="number"
                      step="1.00"
                      @blur="() => { if (health.value.value) health.value.value = formatCurrencyNoSymbol(health.value.value); }"
                      density="compact"
                      :disabled="!is_paycheck.value.value"
                    >
                      <template v-slot:append-inner>
                        <v-tooltip text="Calculator" location="top">
                          <template v-slot:activator="{ props }">
                            <v-btn
                              icon="mdi-calculator-variant"
                              variant="text"
                              @click="showHealthCalculator = true"
                              v-bind="props"
                            ></v-btn>
                          </template>
                        </v-tooltip>
                      </template>
                    </v-text-field>
                    <CalculatorWidget
                      v-model="showHealthCalculator"
                      :amount="health.value.value"
                      @update-dialog="updateShowHealthCalculator"
                      @update-amount="updateHealth"
                      key="health"
                    />
                  </v-col>
                  <v-col>
                    <v-text-field
                      v-model="pension.value.value"
                      variant="outlined"
                      label="Pension*"
                      :error-messages="pension.errorMessage.value"
                      prefix="$"
                      type="number"
                      step="1.00"
                      @blur="() => { if (pension.value.value) pension.value.value = formatCurrencyNoSymbol(pension.value.value); }"
                      density="compact"
                      :disabled="!is_paycheck.value.value"
                    ></v-text-field>
                  </v-col>
                  <v-col>
                    <v-text-field
                      v-model="fsa.value.value"
                      variant="outlined"
                      label="FSA*"
                      :error-messages="fsa.errorMessage.value"
                      prefix="$"
                      type="number"
                      step="1.00"
                      @blur="() => { if (fsa.value.value) fsa.value.value = formatCurrencyNoSymbol(fsa.value.value); }"
                      density="compact"
                      :disabled="!is_paycheck.value.value"
                    ></v-text-field>
                  </v-col>
                </v-row>
                <v-row dense>
                  <v-col>
                    <v-text-field
                      v-model="dca.value.value"
                      variant="outlined"
                      label="DCA*"
                      :error-messages="dca.errorMessage.value"
                      prefix="$"
                      type="number"
                      step="1.00"
                      @blur="() => { if (dca.value.value) dca.value.value = formatCurrencyNoSymbol(dca.value.value); }"
                      density="compact"
                      :disabled="!is_paycheck.value.value"
                    ></v-text-field>
                  </v-col>
                  <v-col>
                    <v-text-field
                      v-model="union_dues.value.value"
                      variant="outlined"
                      label="Union Dues*"
                      :error-messages="union_dues.errorMessage.value"
                      prefix="$"
                      type="number"
                      step="1.00"
                      @blur="() => { if (union_dues.value.value) union_dues.value.value = formatCurrencyNoSymbol(union_dues.value.value); }"
                      density="compact"
                      :disabled="!is_paycheck.value.value"
                    ></v-text-field>
                  </v-col>
                  <v-col>
                    <v-text-field
                      v-model="four_fifty_seven_b.value.value"
                      variant="outlined"
                      label="457b*"
                      :error-messages="four_fifty_seven_b.errorMessage.value"
                      prefix="$"
                      type="number"
                      step="1.00"
                      @blur="() => { if (four_fifty_seven_b.value.value) four_fifty_seven_b.value.value = formatCurrencyNoSymbol(four_fifty_seven_b.value.value); }"
                      density="compact"
                      :disabled="!is_paycheck.value.value"
                    ></v-text-field>
                  </v-col>
                </v-row>
                <v-row dense>
                  <v-col>
                    <v-autocomplete
                      clearable
                      label="Payee*"
                      :items="payees"
                      variant="outlined"
                      :loading="payees_isLoading"
                      item-title="payee_name"
                      item-value="id"
                      v-model="payee_id.value.value"
                      :error-messages="payee_id.errorMessage.value"
                      density="compact"
                      :disabled="!is_paycheck.value.value"
                    ></v-autocomplete>
                  </v-col>
                  <v-col cols="auto" class="d-flex align-center">
                    <AddPayeeForm />
                  </v-col>
                </v-row>
              </v-container>
            </v-window-item>
            <v-window-item value="attachments">
              <v-container>
                <v-carousel>
                  <v-carousel-item
                    src="https://cdn.vuetifyjs.com/images/cards/docks.jpg"
                    cover
                  ></v-carousel-item>

                  <v-carousel-item
                    src="https://cdn.vuetifyjs.com/images/cards/hotel.jpg"
                    cover
                  ></v-carousel-item>

                  <v-carousel-item
                    src="https://cdn.vuetifyjs.com/images/cards/sunshine.jpg"
                    cover
                  ></v-carousel-item>
                </v-carousel>
              </v-container>
            </v-window-item>
          </v-window>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" variant="text" @click="closeDialog"
              >Close</v-btn
            >
            <v-btn color="primary" variant="text" type="submit">
              {{ props.isEdit ? "Update" : "Add" }}
            </v-btn>
          </v-card-actions>
        </form>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>
<script setup>
  import {
    ref,
    defineEmits,
    defineProps,
    onMounted,
    watchEffect,
    watch,
  } from "vue";
  import { useTransactionTypes } from "@/composables/transactionTypesComposable";
  import { useTransactionStatuses } from "@/composables/transactionStatusesComposable";
  import { useAccounts } from "@/composables/accountsComposable";
  import { useTransactions } from "@/composables/transactionsComposable";
  import { usePayees } from "@/composables/payeesComposable";
  import VueDatePicker from "@vuepic/vue-datepicker";
  import "@vuepic/vue-datepicker/dist/main.css";
  import TagTable from "@/components/TagTable.vue";
  import { useDescriptionHistory } from "@/composables/descriptionHistoryComposable";
  import CalculatorWidget from "./CalculatorWidget.vue";
  import AddPayeeForm from "./AddPayeeForm.vue";
  import { useField, useForm } from "vee-validate";
  import * as yup from "yup";

  function roundToTwoDecimals(value) {
    return Math.round(value * 100) / 100;
  }

  const paycheckRequiredWhen = then =>
    yup.number().when("is_paycheck", {
      is: true,
      then: schema =>
        schema.typeError(`${then} is required.`).required(`${then} is required.`),
      otherwise: schema => schema.nullable().notRequired(),
    });

  const schema = yup.object({
    transaction_date: yup
      .string()
      .nullable()
      .required("Transaction date is required."),
    transaction_type_id: yup
      .number()
      .typeError("Transaction type is required.")
      .required("Transaction type is required."),
    status_id: yup
      .number()
      .typeError("Status is required.")
      .required("Status is required."),
    amount: yup
      .number()
      .typeError("Amount is required.")
      .required("Amount is required.")
      .positive("Amount must be greater than zero."),
    description: yup.string().required("Description is required."),
    source_account_id: yup
      .number()
      .typeError("Source account is required.")
      .required("Source account is required."),
    destination_account_id: yup.mixed().when("transaction_type_id", {
      is: 3,
      then: schema =>
        schema.required("Destination account is required for transfers."),
      otherwise: schema => schema.nullable().notRequired(),
    }),
    memo: yup.string().nullable().notRequired(),
    checkNumber: yup.number().nullable().notRequired(),
    is_paycheck: yup.boolean().notRequired(),
    gross: yup.number().when("is_paycheck", {
      is: true,
      then: schema =>
        schema
          .typeError("Gross is required.")
          .required("Gross is required.")
          .test(
            "gross-total",
            "All paycheck fields must total gross.",
            function (value) {
              const {
                taxes,
                health,
                pension,
                fsa,
                dca,
                union_dues,
                four_fifty_seven_b,
                amount: net,
              } = this.parent;
              if (!value) return true;
              const sum = roundToTwoDecimals(
                parseFloat(dca || 0) +
                  parseFloat(four_fifty_seven_b || 0) +
                  parseFloat(fsa || 0) +
                  parseFloat(health || 0) +
                  parseFloat(pension || 0) +
                  parseFloat(taxes || 0) +
                  parseFloat(union_dues || 0) +
                  parseFloat(net || 0),
              );
              const grossVal = roundToTwoDecimals(parseFloat(value));
              if (sum === grossVal) return true;
              const diff = roundToTwoDecimals(grossVal - sum);
              return this.createError({
                message: `Fields total $${sum.toFixed(2)} but gross is $${grossVal.toFixed(2)} — ${diff > 0 ? "short" : "over"} by $${Math.abs(diff).toFixed(2)}.`,
              });
            },
          ),
      otherwise: schema => schema.nullable().notRequired(),
    }),
    taxes: paycheckRequiredWhen("Taxes"),
    health: paycheckRequiredWhen("Health"),
    pension: paycheckRequiredWhen("Pension"),
    fsa: paycheckRequiredWhen("FSA"),
    dca: paycheckRequiredWhen("DCA"),
    union_dues: paycheckRequiredWhen("Union dues"),
    four_fifty_seven_b: paycheckRequiredWhen("457b"),
    payee_id: yup.number().when("is_paycheck", {
      is: true,
      then: schema =>
        schema
          .typeError("Payee is required.")
          .required("Payee is required."),
      otherwise: schema => schema.nullable().notRequired(),
    }),
  });

  const { handleSubmit, resetForm } = useForm({ validationSchema: schema });

  const transaction_date = useField("transaction_date");
  const transaction_type_id = useField("transaction_type_id");
  const status_id = useField("status_id");
  const amount = useField("amount");
  const description = useField("description");
  const source_account_id = useField("source_account_id");
  const destination_account_id = useField("destination_account_id");
  const memo = useField("memo");
  const checkNumber = useField("checkNumber");
  const is_paycheck = useField("is_paycheck");
  const gross = useField("gross");
  const taxes = useField("taxes");
  const health = useField("health");
  const pension = useField("pension");
  const fsa = useField("fsa");
  const dca = useField("dca");
  const union_dues = useField("union_dues");
  const four_fifty_seven_b = useField("four_fifty_seven_b");
  const payee_id = useField("payee_id");

  // Non-validated state
  const tab = ref(0);
  const showAmountCalculator = ref(false);
  const showHealthCalculator = ref(false);
  const details = ref([]);
  const reminder = ref(null);
  const formId = ref(0);
  const formAddDate = ref(null);
  const paycheckId = ref(0);

  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, "0");
  const day = String(today.getDate()).padStart(2, "0");
  const formattedDate = `${year}-${month}-${day}`;

  const { accounts, isLoading: accounts_isLoading } = useAccounts();
  const { transaction_types, isLoading: transaction_types_isLoading } =
    useTransactionTypes();
  const { transaction_statuses, isLoading: transaction_statuses_isLoading } =
    useTransactionStatuses();
  const { addTransaction, editTransaction } = useTransactions();
  const { payees, isLoading: payees_isLoading } = usePayees();
  const { descriptionHistory, isLoading: description_history_isLoading } =
    useDescriptionHistory();

  const emit = defineEmits(["updateDialog"]);
  const props = defineProps({
    itemFormDialog: { type: Boolean, default: false },
    isEdit: { type: Boolean, default: false },
    passedFormData: Object,
    account_id: { type: Number, default: 1 },
  });

  // Re-validate gross when any paycheck amount changes so the total error updates live
  watch(
    () => [
      taxes.value.value,
      health.value.value,
      pension.value.value,
      fsa.value.value,
      dca.value.value,
      union_dues.value.value,
      four_fifty_seven_b.value.value,
      amount.value.value,
    ],
    () => {
      if (is_paycheck.value.value) {
        gross.validate();
      }
    },
  );

  const fillTagTable = detailsList => {
    if (!detailsList) return [];
    return detailsList.map(detail => ({
      tag_id: detail.tag.id,
      tag_amt: parseFloat(Math.abs(detail.detail_amt)).toFixed(2),
      tag_pretty_name: detail.tag.tag_name,
      tag_full_toggle: detail.full_toggle ?? false,
    }));
  };

  const initializeFormData = () => {
    const p = props.passedFormData;
    formId.value = p.id ?? 0;
    formAddDate.value = p.add_date ?? formattedDate;
    reminder.value = p.reminder ?? null;
    details.value = fillTagTable(p.details);

    transaction_date.value.value = p.transaction_date ?? formattedDate;
    transaction_type_id.value.value = p.transaction_type?.id ?? 1;
    status_id.value.value = p.status?.id ?? 1;
    amount.value.value = p.total_amount
      ? parseFloat(Math.abs(p.total_amount)).toFixed(2)
      : null;
    description.value.value = p.description ?? null;
    source_account_id.value.value =
      p.source_account_id ?? p.account_id ?? null;
    destination_account_id.value.value = p.destination_account_id ?? null;
    memo.value.value = p.memo ?? "";
    checkNumber.value.value = p.checkNumber ?? null;
    is_paycheck.value.value = !!p.paycheck;

    paycheckId.value = p.paycheck?.id ?? 0;
    gross.value.value = p.paycheck?.gross ?? null;
    taxes.value.value = p.paycheck?.taxes ?? null;
    health.value.value = p.paycheck?.health ?? null;
    pension.value.value = p.paycheck?.pension ?? null;
    fsa.value.value = p.paycheck?.fsa ?? null;
    dca.value.value = p.paycheck?.dca ?? null;
    union_dues.value.value = p.paycheck?.union_dues ?? null;
    four_fifty_seven_b.value.value = p.paycheck?.four_fifty_seven_b ?? null;
    payee_id.value.value = p.paycheck?.payee?.id ?? null;
  };

  const selectPaycheckChange = () => {
    gross.value.value = null;
    taxes.value.value = null;
    health.value.value = null;
    pension.value.value = null;
    fsa.value.value = null;
    dca.value.value = null;
    union_dues.value.value = null;
    four_fifty_seven_b.value.value = null;
    payee_id.value.value = null;
  };

  const submit = handleSubmit(values => {
    const payload = {
      id: formId.value,
      transaction_date: values.transaction_date,
      transaction_type_id: values.transaction_type_id,
      status_id: values.status_id,
      total_amount:
        values.transaction_type_id == 2
          ? Math.abs(values.amount)
          : -Math.abs(values.amount),
      description: values.description,
      source_account_id: values.source_account_id,
      destination_account_id:
        values.transaction_type_id == 3
          ? values.destination_account_id
          : null,
      memo: values.memo,
      checkNumber: values.checkNumber,
      edit_date: formattedDate,
      add_date: formAddDate.value,
      details: details.value,
      reminder: reminder.value,
      paycheck: values.is_paycheck
        ? {
            id: paycheckId.value,
            gross: values.gross,
            net: values.amount,
            taxes: values.taxes,
            health: values.health,
            pension: values.pension,
            fsa: values.fsa,
            dca: values.dca,
            union_dues: values.union_dues,
            four_fifty_seven_b: values.four_fifty_seven_b,
            payee_id: values.payee_id,
          }
        : null,
    };

    if (props.isEdit) {
      editTransaction(payload);
    } else {
      addTransaction(payload);
    }
    closeDialog();
  });

  const closeDialog = () => {
    resetForm();
    initializeFormData();
    tab.value = 0;
    emit("updateDialog", false);
  };

  const tagsUpdated = data => {
    details.value = data.tags;
  };

  const formatAmount = () => {
    if (amount.value.value) {
      amount.value.value = formatCurrencyNoSymbol(amount.value.value);
    }
  };

  const updateAmount = data => {
    amount.value.value = data;
  };

  const updateShowAmountCalculator = () => {
    showAmountCalculator.value = !showAmountCalculator.value;
  };

  const updateHealth = data => {
    health.value.value = data;
  };

  const updateShowHealthCalculator = () => {
    showHealthCalculator.value = !showHealthCalculator.value;
  };

  onMounted(() => {
    watchEffect(() => {
      if (props.passedFormData) {
        initializeFormData();
      }
    });
  });

  const formatCurrencyNoSymbol = value => {
    return new Intl.NumberFormat("en-US", {
      style: "decimal",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
      useGrouping: false,
    }).format(value);
  };
</script>
<style>
  /* alt-pagination */
  .alt-pagination .bh-pagination .bh-page-item {
    width: auto; /* equivalent to w-max */
    min-width: 32px;
    border-radius: 0.25rem; /* equivalent to rounded */
  }
  /* Customize the color of the selected page number */
  .alt-pagination .bh-pagination .bh-page-item.bh-active {
    background-color: #06966a; /* Change this to your desired color */
    border-color: black;
    font-weight: bold; /* Optional: Make the text bold */
  }
  .alt-pagination .bh-pagination .bh-page-item:not(.bh-active):hover {
    background-color: #ff5900;
    border-color: black;
  }
</style>
