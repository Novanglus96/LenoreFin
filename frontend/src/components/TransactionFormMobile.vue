<template>
  <v-dialog fullscreen persistent>
    <v-card>
      <v-card-title>
        <span class="text-h5" v-if="props.isEdit == false"
          >Add Transaction</span
        >
        <span class="text-h5" v-else>Edit Transaction</span
        ><v-icon
          v-if="props.passedFormData.reminder"
          icon="mdi-bell"
          color="amber"
        ></v-icon>
      </v-card-title>

      <v-card-text>
        <v-form v-model="formValid" @submit.prevent ref="transactionForm">
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
                      v-model="formData.transaction_date"
                      timezone="America/New_York"
                      model-type="yyyy-MM-dd"
                      :enable-time-picker="false"
                      auto-apply
                      format="yyyy-MM-dd"
                      :state="!formData.transaction_date ? false : null"
                    ></VueDatePicker>
                  </v-col>
                  <v-col>
                    <span
                      v-if="!formData.transaction_date"
                      class="text-red text-caption"
                      >This field is required.</span
                    >
                  </v-col>
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
                      v-model="formData.transaction_type_id"
                      :rules="required"
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
                      v-model="formData.status_id"
                      :rules="required"
                      density="compact"
                    ></v-autocomplete>
                  </v-col>
                </v-row>
                <v-row dense>
                  <v-col cols="3">
                    <v-text-field
                      v-model="amount"
                      variant="outlined"
                      label="Amount*"
                      :rules="required"
                      prefix="$"
                      type="number"
                      step="1.00"
                      @blur="
                        () => {
                          amount = formatCurrencyNoSymbol(amount);
                          transactionForm.validate();
                        }
                      "
                      density="compact"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="3">
                    <v-text-field
                      v-model="formData.checkNumber"
                      variant="outlined"
                      label="Check #"
                      type="number"
                      @update:model-value="
                        () => {
                          resetTagField();
                        }
                      "
                      density="compact"
                      v-if="formData.transaction_type_id != 3"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="6">
                    <v-combobox
                      v-model="formData.description"
                      :items="
                        descriptionHistory.map(item => item.description_pretty)
                      "
                      label="Description*"
                      clearable
                      hide-no-data
                      hide-selected
                      :loading="description_history_isLoading"
                      variant="outlined"
                      :rules="required"
                      @update:model-value="
                        () => {
                          resetTagField();
                        }
                      "
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
                      v-model="formData.source_account_id"
                      :rules="required"
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
                      v-model="formData.destination_account_id"
                      :rules="required"
                      v-if="formData.transaction_type_id == 3"
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
                    <!-- TODO: Enable adding tags here -->
                    <TagTable
                      :tags="formData.details"
                      :totalAmount="parseFloat(amount)"
                      @tag-table-updated="tagsUpdated"
                    />
                  </v-col>
                  <v-col>
                    <v-textarea
                      clearable
                      label="Memo"
                      variant="outlined"
                      v-model="formData.memo"
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
                      v-model="isPaycheck"
                      label="Is this a Paycheck?"
                      @update:model-value="selectPaycheckChange()"
                      :disabled="
                        formData.transaction_type_id == 2 ? false : true
                      "
                    ></v-checkbox>
                  </v-col>
                  <v-col> </v-col>
                </v-row>
                <v-row dense>
                  <v-col>
                    <v-text-field
                      v-model="paycheck.gross"
                      variant="outlined"
                      label="Gross*"
                      :rules="[...requiredPaycheck, ...grossTotal]"
                      prefix="$"
                      type="number"
                      step="1.00"
                      @blur="
                        () => {
                          paycheck.gross = formatCurrencyNoSymbol(
                            paycheck.gross,
                          );
                          transactionForm.validate();
                        }
                      "
                      density="compact"
                      :disabled="!isPaycheck"
                    ></v-text-field>
                  </v-col>
                  <v-col>
                    <v-text-field
                      v-model="amount"
                      variant="outlined"
                      label="Net*"
                      :rules="[...requiredPaycheck, ...grossTotal]"
                      prefix="$"
                      type="number"
                      step="1.00"
                      @blur="
                        () => {
                          amount = formatCurrencyNoSymbol(amount);
                          transactionForm.validate();
                        }
                      "
                      density="compact"
                      :disabled="!isPaycheck"
                    ></v-text-field>
                  </v-col>
                  <v-col>
                    <v-text-field
                      v-model="paycheck.taxes"
                      variant="outlined"
                      label="Taxes*"
                      :rules="[...requiredPaycheck, ...grossTotal]"
                      prefix="$"
                      type="number"
                      step="1.00"
                      @blur="
                        () => {
                          paycheck.taxes = formatCurrencyNoSymbol(
                            paycheck.taxes,
                          );
                          transactionForm.validate();
                        }
                      "
                      density="compact"
                      :disabled="!isPaycheck"
                    ></v-text-field>
                  </v-col>
                </v-row>
                <v-row dense>
                  <v-col>
                    <v-text-field
                      v-model="paycheck.health"
                      variant="outlined"
                      label="Health*"
                      :rules="[...requiredPaycheck, ...grossTotal]"
                      prefix="$"
                      type="number"
                      step="1.00"
                      @blur="
                        () => {
                          paycheck.health = formatCurrencyNoSymbol(
                            paycheck.health,
                          );
                          transactionForm.validate();
                        }
                      "
                      density="compact"
                      :disabled="!isPaycheck"
                    ></v-text-field>
                  </v-col>
                  <v-col>
                    <v-text-field
                      v-model="paycheck.pension"
                      variant="outlined"
                      label="Pension*"
                      :rules="[...requiredPaycheck, ...grossTotal]"
                      prefix="$"
                      type="number"
                      step="1.00"
                      @blur="
                        () => {
                          paycheck.pension = formatCurrencyNoSymbol(
                            paycheck.pension,
                          );
                          transactionForm.validate();
                        }
                      "
                      density="compact"
                      :disabled="!isPaycheck"
                    ></v-text-field>
                  </v-col>
                  <v-col>
                    <v-text-field
                      v-model="paycheck.fsa"
                      variant="outlined"
                      label="FSA*"
                      :rules="[...requiredPaycheck, ...grossTotal]"
                      prefix="$"
                      type="number"
                      step="1.00"
                      @blur="
                        () => {
                          paycheck.fsa = formatCurrencyNoSymbol(paycheck.fsa);
                          transactionForm.validate();
                        }
                      "
                      density="compact"
                      :disabled="!isPaycheck"
                    ></v-text-field>
                  </v-col>
                </v-row>
                <v-row dense>
                  <v-col>
                    <v-text-field
                      v-model="paycheck.dca"
                      variant="outlined"
                      label="DCA*"
                      :rules="[...requiredPaycheck, ...grossTotal]"
                      prefix="$"
                      type="number"
                      step="1.00"
                      @blur="
                        () => {
                          paycheck.dca = formatCurrencyNoSymbol(paycheck.dca);
                          transactionForm.validate();
                        }
                      "
                      density="compact"
                      :disabled="!isPaycheck"
                    ></v-text-field>
                  </v-col>
                  <v-col>
                    <v-text-field
                      v-model="paycheck.union_dues"
                      variant="outlined"
                      label="Union Dues*"
                      :rules="[...requiredPaycheck, ...grossTotal]"
                      prefix="$"
                      type="number"
                      step="1.00"
                      @blur="
                        () => {
                          paycheck.union_dues = formatCurrencyNoSymbol(
                            paycheck.union_dues,
                          );
                          transactionForm.validate();
                        }
                      "
                      density="compact"
                      :disabled="!isPaycheck"
                    ></v-text-field>
                  </v-col>
                  <v-col>
                    <v-text-field
                      v-model="paycheck.four_fifty_seven_b"
                      variant="outlined"
                      label="457b*"
                      :rules="[...requiredPaycheck, ...grossTotal]"
                      prefix="$"
                      type="number"
                      step="1.00"
                      @blur="
                        () => {
                          paycheck.four_fifty_seven_b = formatCurrencyNoSymbol(
                            paycheck.four_fifty_seven_b,
                          );
                          transactionForm.validate();
                        }
                      "
                      density="compact"
                      :disabled="!isPaycheck"
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
                      v-model="paycheck.payee_id"
                      :rules="requiredPaycheck"
                      density="compact"
                      :disabled="!isPaycheck"
                    ></v-autocomplete>
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
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="secondary" variant="text" @click="closeDialog">
          Close
        </v-btn>
        <v-btn
          color="secondary"
          variant="text"
          @click="submitForm"
          :disabled="!formValid"
          type="submit"
        >
          {{ props.isEdit ? "Update" : "Add" }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
<script setup>
/**
 * Vue script setup for transaction creation/editing
 * @fileoverview
 * @author John Adams
 * @version 1.0.0
 */

// Import Vue composition functions and components...
import {
  ref,
  defineEmits,
  defineProps,
  onMounted,
  watchEffect,
  computed,
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

// Define reactive variables...
const tagToAdd = ref(null); // Tag object to add to tag list
const tagAmount = ref(null); // Tag amount to add to tag list
const tab = ref(0); // Tab model
const isPaycheck = ref(null); // True if this transaction a paycheck
const paycheckTotalsMatch = ref(false); // True if the paycheck fields total = gross
const formValid = ref(false);
const transactionForm = ref(null);

// Define emits
const emit = defineEmits(["updateDialog"]);

// Define validation rules
// General required validation rule
const required = [
  value => {
    if (value !== null && value !== undefined && value !== "") return true;
    return "This field is required.";
  },
];

// Computed property for conditional validation based on `isPaycheck`
const requiredPaycheck = computed(() => {
  return isPaycheck.value
    ? [
        value => {
          if (value !== null && value !== undefined && value !== "")
            return true;
          return "This field is required for paycheck.";
        },
      ]
    : [];
});

// Computed property for conditional validation based on `isPaycheck`
const grossTotal = computed(() => {
  return isPaycheck.value
    ? [
        () => {
          if (
            roundToTwoDecimals(
              parseFloat(paycheck.value.dca) +
                parseFloat(paycheck.value.four_fifty_seven_b) +
                parseFloat(paycheck.value.fsa) +
                parseFloat(paycheck.value.health) +
                parseFloat(paycheck.value.pension) +
                parseFloat(paycheck.value.taxes) +
                parseFloat(paycheck.value.union_dues) +
                parseFloat(amount.value),
            ) === roundToTwoDecimals(parseFloat(paycheck.value.gross))
          )
            return true;
          return "All fields must total gross.";
        },
      ]
    : [];
});

function roundToTwoDecimals(value) {
  return Math.round(value * 100) / 100; // Round to 2 decimal places
}

// Date variables...
const today = new Date();
const year = today.getFullYear();
const month = String(today.getMonth() + 1).padStart(2, "0");
const day = String(today.getDate()).padStart(2, "0");
const formattedDate = `${year}-${month}-${day}`;

// API calls and data retrieval...
const { accounts, isLoading: accounts_isLoading } = useAccounts();
const { transaction_types, isLoading: transaction_types_isLoading } =
  useTransactionTypes();
const { transaction_statuses, isLoading: transaction_statuses_isLoading } =
  useTransactionStatuses();
const { addTransaction, editTransaction } = useTransactions();
const { payees, isLoading: payees_isLoading } = usePayees();
const { descriptionHistory, isLoading: description_history_isLoading } =
  useDescriptionHistory();
// Define props...
const props = defineProps({
  itemFormDialog: {
    type: Boolean,
    default: false,
  },
  isEdit: {
    type: Boolean,
    default: false,
  },
  passedFormData: Object,
  account_id: {
    type: Number,
    default: 1,
  },
});

// Initialze Form Data...
const formData = ref({
  id: props.passedFormData ? props.passedFormData.id : 0,
  status_id: props.passedFormData.status.id || 1,
  transaction_type_id: props.passedFormData.transaction_type.id || 1,
  transaction_date: props.passedFormData.transaction_date || formattedDate,
  memo: props.passedFormData.memo || "",
  source_account_id:
    props.passedFormData.source_account_id || props.passedFormData.account_id,
  destination_account_id: props.passedFormData.destination_account_id || null,
  edit_date: formattedDate,
  add_date: props.passedFormData.add_date || formattedDate,
  total_amount: props.passedFormData.total_amount || 0,
  checkNumber: props.passedFormData.checkNumber || null,
  description: props.passedFormData.description || null,
  details: [],
  paycheck: null,
  reminder: null,
});

const paycheck = ref({
  id: 0,
  gross: null,
  net: null,
  taxes: null,
  health: null,
  pension: null,
  fsa: null,
  dca: null,
  union_dues: null,
  four_fifty_seven_b: null,
  payee_id: null,
});

// Initialize amount with absolute value...
const amount = ref(
  props.passedFormData.total_amount
    ? parseFloat(Math.abs(props.passedFormData.total_amount)).toFixed(2)
    : null,
);

// Define functions...

/**
 * `watchpassedFormData` Watches for changes to passedFormData prop and updates
 * local variable formData as appropiate.
 */
const watchPassedFormData = () => {
  watchEffect(() => {
    if (props.passedFormData) {
      formData.value = {
        id: props.passedFormData.id,
        status_id: props.passedFormData.status.id,
        transaction_type_id: props.passedFormData.transaction_type.id,
        transaction_date: props.passedFormData.transaction_date,
        memo: props.passedFormData.memo,
        source_account_id:
          props.passedFormData.source_account_id ||
          props.passedFormData.account_id,
        destination_account_id: props.passedFormData.destination_account_id,
        edit_date: formattedDate,
        add_date: props.passedFormData.add_date,
        tag_id: props.passedFormData.tag_id,
        total_amount: props.passedFormData.total_amount,
        checkNumber: props.passedFormData.checkNumber,
        description: props.passedFormData.description,
        details: fillTagTable(props.passedFormData.details),
        reminder: props.passedFormData.reminder,
      };
      paycheck.value = {
        id: props.passedFormData.paycheck
          ? props.passedFormData.paycheck.id
          : 0,
        gross: props.passedFormData.paycheck
          ? props.passedFormData.paycheck.gross
          : null,
        net: props.passedFormData.paycheck
          ? props.passedFormData.paycheck.net
          : null,
        taxes: props.passedFormData.paycheck
          ? props.passedFormData.paycheck.taxes
          : null,
        health: props.passedFormData.paycheck
          ? props.passedFormData.paycheck.health
          : null,
        pension: props.passedFormData.paycheck
          ? props.passedFormData.paycheck.pension
          : null,
        fsa: props.passedFormData.paycheck
          ? props.passedFormData.paycheck.fsa
          : null,
        dca: props.passedFormData.paycheck
          ? props.passedFormData.paycheck.dca
          : null,
        union_dues: props.passedFormData.paycheck
          ? props.passedFormData.paycheck.union_dues
          : null,
        four_fifty_seven_b: props.passedFormData.paycheck
          ? props.passedFormData.paycheck.four_fifty_seven_b
          : null,
        payee_id: props.passedFormData.paycheck
          ? props.passedFormData.paycheck.payee.id
          : null,
      };
      amount.value = props.passedFormData.total_amount
        ? parseFloat(Math.abs(props.passedFormData.total_amount)).toFixed(2)
        : null;
      if (props.passedFormData.paycheck) {
        isPaycheck.value = true;
        paycheckTotalsMatch.value = true;
      } else {
        isPaycheck.value = false;
        paycheckTotalsMatch.value = false;
      }
    }
  });
};

/**
 * `fillTagTable` Formats tag details for display in tag table.
 * @param {list} details - The list of tag details.
 * @returns {table} - A list of formatted tags for display in the table.
 */
const fillTagTable = details => {
  let table = [];
  let pretty_name = "";
  let tag_full_toggle = null;
  if (details) {
    for (const detail of details) {
      if (detail.full_toggle) {
        tag_full_toggle = detail.full_toggle;
      } else {
        tag_full_toggle = false;
      }
      pretty_name = detail.tag.tag_name;
      let tag_row = {
        tag_id: detail.tag.id,
        tag_amt: parseFloat(Math.abs(detail.detail_amt)).toFixed(2),
        tag_pretty_name: pretty_name,
        tag_full_toggle: tag_full_toggle,
      };
      table.push(tag_row);
    }
  }

  return table;
};

/**
 * `submitForm` Submits the formData and creates/edits transaction.
 */
const submitForm = async () => {
  if (formData.value.transaction_type_id == 2) {
    formData.value.total_amount = Math.abs(amount.value);
  } else {
    formData.value.total_amount = -Math.abs(amount.value);
  }
  if (isPaycheck.value) {
    paycheck.value.net = amount.value;
    formData.value.paycheck = paycheck.value;
  }
  if (props.isEdit == false) {
    await addTransaction(formData.value);
  } else {
    await editTransaction(formData.value);
  }

  closeDialog();
};

/**
 * `closeDialog` Emits updateDialog to close form.
 */
const closeDialog = () => {
  formData.value = {
    id: props.passedFormData ? props.passedFormData.id : 0,
    status_id: props.passedFormData.status.id || 1,
    transaction_type_id: props.passedFormData.transaction_type.id || 1,
    transaction_date: props.passedFormData.transaction_date || formattedDate,
    memo: props.passedFormData.memo || "",
    source_account_id: props.passedFormData.source_account_id || null,
    destination_account_id: props.passedFormData.destination_account_id || null,
    edit_date: formattedDate,
    add_date: props.passedFormData.add_date || formattedDate,
    total_amount: props.passedFormData.total_amount || 0,
    checkNumber: props.passedFormData.checkNumber || null,
    description: props.passedFormData.description || null,
    details: fillTagTable(props.passedFormData.details),
    paycheck: null,
  };
  amount.value = props.passedFormData.total_amount
    ? parseFloat(Math.abs(props.passedFormData.total_amount)).toFixed(2)
    : null;
  paycheck.value = {
    id: props.passedFormData.paycheck ? props.passedFormData.paycheck.id : 0,
    gross: props.passedFormData.paycheck
      ? props.passedFormData.paycheck.gross
      : null,
    net: props.passedFormData.paycheck
      ? props.passedFormData.paycheck.net
      : null,
    taxes: props.passedFormData.paycheck
      ? props.passedFormData.paycheck.taxes
      : null,
    health: props.passedFormData.paycheck
      ? props.passedFormData.paycheck.health
      : null,
    pension: props.passedFormData.paycheck
      ? props.passedFormData.paycheck.pension
      : null,
    fsa: props.passedFormData.paycheck
      ? props.passedFormData.paycheck.fsa
      : null,
    dca: props.passedFormData.paycheck
      ? props.passedFormData.paycheck.dca
      : null,
    union_dues: props.passedFormData.paycheck
      ? props.passedFormData.paycheck.union_dues
      : null,
    four_fifty_seven_b: props.passedFormData.paycheck
      ? props.passedFormData.paycheck.four_fifty_seven_b
      : null,
    payee_id: props.passedFormData.paycheck
      ? props.passedFormData.paycheck.payee.id
      : null,
  };
  tagToAdd.value = null;
  tagAmount.value = null;
  if (props.passedFormData.paycheck) {
    isPaycheck.value = true;
  } else {
    isPaycheck.value = false;
  }
  tab.value = 0;
  emit("updateDialog", false);
};

/**
 * `selectPaycheckChange` Handles when switching between paycheck or not.
 */
const selectPaycheckChange = () => {
  paycheck.value.dca = null;
  paycheck.value.four_fifty_seven_b = null;
  paycheck.value.fsa = null;
  paycheck.value.gross = null;
  paycheck.value.health = null;
  paycheck.value.payee_id = null;
  paycheck.value.pension = null;
  paycheck.value.taxes = null;
  paycheck.value.union_dues = null;
  transactionForm.value.validate();
};

/**
 * `resetTagField` Convenience function adds total and Untagged as default option for tags.
 */
const resetTagField = () => {
  tagAmount.value = amount.value;
};

/**
 * `clickTagAdd` Adds a tag to the tag table.
 */
const tagsUpdated = data => {
  formData.value.details = data.tags;
};

// Lifecycle hook...

onMounted(() => {
  // Perform actions on mount
  watchPassedFormData();
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
