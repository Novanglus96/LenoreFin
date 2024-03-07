<template>
  <v-dialog persistent width="1024">
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
      <v-card-subtitle>
        <span
          class="text-subtitle-2 font-italic text-red-lighten-2"
          v-if="props.passedFormData.reminder"
          >* This transaction is part of a reminder. Modifying it will remove it
          from the reminder.</span
        >
      </v-card-subtitle>

      <v-card-text>
        <v-tabs v-model="tab" color="accent">
          <v-tab value="trans" density="compact">Transaction Details</v-tab>
          <v-tab value="pay" density="compact">Paycheck Info</v-tab>
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
                  ></VueDatePicker>
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
                    @update:model-value="checkFormComplete"
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
                    @update:model-value="checkFormComplete"
                    density="compact"
                  ></v-autocomplete>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col>
                  <v-text-field
                    v-model="amount"
                    variant="outlined"
                    label="Amount*"
                    :rules="required"
                    prefix="$"
                    @update:model-value="checkFormComplete"
                    type="number"
                    step="1.00"
                    @update:focused="reformatNumberToMoney"
                    density="compact"
                  ></v-text-field>
                </v-col>
                <v-col>
                  <v-text-field
                    v-model="formData.description"
                    variant="outlined"
                    label="Description*"
                    :rules="required"
                    @update:model-value="checkFormComplete"
                    density="compact"
                  ></v-text-field>
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
                    @update:model-value="checkFormComplete"
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
                    @update:model-value="checkFormComplete"
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
                  <v-sheet
                    border
                    rounded
                    v-if="formData.transaction_type_id != 3"
                    :height="300"
                    :color="verifyTagTotal() ? 'white' : 'red-lighten-5'"
                  >
                    <v-container class="pa-0 ma-1">
                      <v-row dense>
                        <v-col cols="1">
                          <v-tooltip text="Delete Tag(s)" location="top">
                            <template v-slot:activator="{ props }">
                              <v-btn
                                icon="mdi-tag-minus"
                                flat
                                variant="plain"
                                color="error"
                                @click="clickTagRemove"
                                v-bind="props"
                                :disabled="selected && selected.length === 0"
                              ></v-btn>
                            </template>
                          </v-tooltip>
                        </v-col>
                        <v-col>
                          <v-autocomplete
                            clearable
                            label="Tag"
                            :items="tags"
                            variant="outlined"
                            :loading="tags_isLoading"
                            item-title="tag_name"
                            v-model="tagToAdd"
                            @update:model-value="checkTagComplete"
                            density="compact"
                            return-object
                          >
                            <template v-slot:item="{ props, item }">
                              <v-list-item
                                v-bind="props"
                                :title="
                                  item.raw.parent
                                    ? item.raw.parent.tag_name
                                    : item.raw.tag_name
                                "
                                :subtitle="
                                  item.raw.parent ? item.raw.tag_name : null
                                "
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
                        </v-col>
                        <v-col cols="4">
                          <v-text-field
                            v-model="tagAmount"
                            variant="outlined"
                            label="Amount"
                            prefix="$"
                            @update:model-value="checkTagComplete"
                            type="number"
                            step="1.00"
                            @update:focused="reformatNumberToMoney"
                            density="compact"
                          ></v-text-field>
                        </v-col>
                        <v-col cols="1">
                          <v-tooltip text="Add New Tag" location="top">
                            <template v-slot:activator="{ props }">
                              <v-btn
                                icon="mdi-tag-plus"
                                flat
                                variant="plain"
                                color="success"
                                @click="clickTagAdd"
                                v-bind="props"
                                :disabled="!tagComplete && !verifyTagTotal()"
                              ></v-btn>
                            </template>
                          </v-tooltip>
                        </v-col>
                      </v-row>
                      <v-row dense>
                        <v-col
                          ><span
                            class="text-error text-subtitle-2 font-italic"
                            v-if="!verifyTagTotal()"
                            >* Tags must equal total</span
                          ></v-col
                        >
                      </v-row>
                    </v-container>
                    <vue3-datatable
                      :rows="formData.details"
                      :columns="columns"
                      :totalRows="
                        formData.details ? formData.details.length : 0
                      "
                      :isServerMode="false"
                      pageSize="4"
                      :hasCheckbox="true"
                      :stickyHeader="true"
                      noDataContent="No Tags"
                      search=""
                      @rowSelect="rowSelected"
                      ref="details_table"
                      height="210px"
                      skin="bh-table-striped bh-table-compact"
                      :pageSizeOptions="[4]"
                      :showPageSize="false"
                      paginationInfo="{0} to {1} of {2}"
                      class="alt-pagination"
                    >
                      <template #tag_pretty_name="row">
                        <v-icon icon="mdi-tag"></v-icon>
                        <span class="font-weight-bold text-black">{{
                          row.value.tag_pretty_name
                        }}</span>
                      </template>
                      <template #tag_amt="row">
                        <span class="font-weight-bold text-black"
                          >${{ row.value.tag_amt }}</span
                        >
                      </template>
                    </vue3-datatable>
                  </v-sheet>
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
                  ></v-checkbox>
                </v-col>
                <v-col>
                  <span
                    class="text-subtitle-2 text-red font-italic"
                    v-if="!paycheckTotalsMatch && isPaycheck"
                    >* Paycheck fields must total Gross</span
                  >
                </v-col>
              </v-row>
              <v-row dense>
                <v-col>
                  <v-text-field
                    v-model="paycheck.gross"
                    variant="outlined"
                    label="Gross*"
                    :rules="required"
                    prefix="$"
                    @update:model-value="checkFormComplete"
                    type="number"
                    step="1.00"
                    @update:focused="reformatNumberToMoney"
                    density="compact"
                    :disabled="!isPaycheck"
                  ></v-text-field>
                </v-col>
                <v-col>
                  <v-text-field
                    v-model="amount"
                    variant="outlined"
                    label="Net*"
                    :rules="required"
                    prefix="$"
                    @update:model-value="checkFormComplete"
                    type="number"
                    step="1.00"
                    @update:focused="reformatNumberToMoney"
                    density="compact"
                    :disabled="!isPaycheck"
                  ></v-text-field>
                </v-col>
                <v-col>
                  <v-text-field
                    v-model="paycheck.taxes"
                    variant="outlined"
                    label="Taxes*"
                    :rules="required"
                    prefix="$"
                    @update:model-value="checkFormComplete"
                    type="number"
                    step="1.00"
                    @update:focused="reformatNumberToMoney"
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
                    :rules="required"
                    prefix="$"
                    @update:model-value="checkFormComplete"
                    type="number"
                    step="1.00"
                    @update:focused="reformatNumberToMoney"
                    density="compact"
                    :disabled="!isPaycheck"
                  ></v-text-field>
                </v-col>
                <v-col>
                  <v-text-field
                    v-model="paycheck.pension"
                    variant="outlined"
                    label="Pension*"
                    :rules="required"
                    prefix="$"
                    @update:model-value="checkFormComplete"
                    type="number"
                    step="1.00"
                    @update:focused="reformatNumberToMoney"
                    density="compact"
                    :disabled="!isPaycheck"
                  ></v-text-field>
                </v-col>
                <v-col>
                  <v-text-field
                    v-model="paycheck.fsa"
                    variant="outlined"
                    label="FSA*"
                    :rules="required"
                    prefix="$"
                    @update:model-value="checkFormComplete"
                    type="number"
                    step="1.00"
                    @update:focused="reformatNumberToMoney"
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
                    :rules="required"
                    prefix="$"
                    @update:model-value="checkFormComplete"
                    type="number"
                    step="1.00"
                    @update:focused="reformatNumberToMoney"
                    density="compact"
                    :disabled="!isPaycheck"
                  ></v-text-field>
                </v-col>
                <v-col>
                  <v-text-field
                    v-model="paycheck.union_dues"
                    variant="outlined"
                    label="Union Dues*"
                    :rules="required"
                    prefix="$"
                    @update:model-value="checkFormComplete"
                    type="number"
                    step="1.00"
                    @update:focused="reformatNumberToMoney"
                    density="compact"
                    :disabled="!isPaycheck"
                  ></v-text-field>
                </v-col>
                <v-col>
                  <v-text-field
                    v-model="paycheck.four_fifty_seven_b"
                    variant="outlined"
                    label="457b*"
                    :rules="required"
                    prefix="$"
                    @update:model-value="checkFormComplete"
                    type="number"
                    step="1.00"
                    @update:focused="reformatNumberToMoney"
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
                    :rules="required"
                    @update:model-value="checkFormComplete"
                    density="compact"
                    :disabled="!isPaycheck"
                  ></v-autocomplete>
                </v-col>
              </v-row>
            </v-container>
          </v-window-item>
        </v-window>
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
          :disabled="!formComplete"
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
import { ref, defineEmits, defineProps, onMounted, watchEffect } from "vue";
import { useTransactionTypes } from "@/composables/transactionTypesComposable";
import { useTransactionStatuses } from "@/composables/transactionStatusesComposable";
import { useAccounts } from "@/composables/accountsComposable";
import { useTags } from "@/composables/tagsComposable";
import { useTransactions } from "@/composables/transactionsComposable";
import { usePayees } from "@/composables/payeesComposable";
import VueDatePicker from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css";
import Vue3Datatable from "@bhplugin/vue3-datatable";
import "@bhplugin/vue3-datatable/dist/style.css";

// Define reactive variables...
const tagToAdd = ref(null); // Tag object to add to tag list
const tagAmount = ref(null); // Tag amount to add to tag list
const tagComplete = ref(false); // True when tag/amount are filled out, enables add button
const formComplete = ref(false); // True when form is validated, enables add/update button
const selected = ref([]); // The objects of the rows selected in table
const details_table = ref(null); // The reference to the table
const tab = ref(null); // Tab model
const isPaycheck = ref(null); // True if this transaction a paycheck
const paycheckTotalsMatch = ref(false); // True if the paycheck fields total = gross

// Define emits
const emit = defineEmits(["updateDialog"]);

// Define validation rules
const required = [
  value => {
    if (value) return true;

    return "This field is required.";
  },
];

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
const { addTransaction } = useTransactions();
const { tags, isLoading: tags_isLoading } = useTags();
const { payees, isLoading: payees_isLoading } = usePayees();

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
  source_account_id: props.passedFormData.source_account_id || null,
  destination_account_id: props.passedFormData.destination_account_id || null,
  edit_date: formattedDate,
  add_date: props.passedFormData.add_date || formattedDate,
  total_amount: props.passedFormData.total_amount || 0,
  description: props.passedFormData.description || null,
  details: [],
  paycheck: null,
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

// Define table columns...
const columns = ref([
  { field: "tag_id", title: "ID", isUnique: true, hide: true },
  { field: "tag_pretty_name", title: "Tag" },
  { field: "tag_amt", title: "Amount", type: "number", width: "100px" },
]);

// Define functions...
/**
 * `rowSelected` Populates selected variable with selected rows in table.
 */
const rowSelected = () => {
  selected.value = [];
  let selectedrows = details_table.value.getSelectedRows();
  for (const selectedrow of selectedrows) {
    selected.value.push(selectedrow.tag_id);
  }
};

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
        source_account_id: props.passedFormData.source_account_id,
        destination_account_id: props.passedFormData.destination_account_id,
        edit_date: formattedDate,
        add_date: props.passedFormData.add_date,
        tag_id: props.passedFormData.tag_id,
        total_amount: props.passedFormData.total_amount,
        description: props.passedFormData.description,
        details: fillTagTable(props.passedFormData.details),
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
  if (details) {
    for (const detail of details) {
      if (detail.tag.parent) {
        pretty_name = detail.tag.parent.tag_name + " : " + detail.tag.tag_name;
      } else {
        pretty_name = detail.tag.tag_name;
      }
      let tag_row = {
        tag_id: detail.tag.id,
        tag_amt: parseFloat(Math.abs(detail.detail_amt)).toFixed(2),
        tag_pretty_name: pretty_name,
      };
      table.push(tag_row);
    }
  }

  return table;
};

/**
 * `checkFormComplete` Validates form completion.
 * @returns {formComplete} - Sets to True when form is validated.
 */
const checkFormComplete = () => {
  if (
    verifyBaseRequired() == true &&
    verifyTagTotal() == true &&
    verifyTransactionType() == true &&
    verifyPaycheck() == true
  ) {
    formComplete.value = true;
  } else {
    formComplete.value = false;
  }
};

/**
 * `verifyBaseRequired` Verifies base requirements for form completeion
 * @returns {boolean}- True if base requirements met
 */
const verifyBaseRequired = () => {
  if (
    formData.value.transaction_type_id !== null &&
    formData.value.transaction_type_id !== "" &&
    formData.value.status_id !== null &&
    formData.value.status_id !== "" &&
    formData.value.description !== "" &&
    formData.value.description !== null &&
    amount.value !== "" &&
    amount.value !== null &&
    formData.value.source_account_id !== "" &&
    formData.value.source_account_id !== null
  ) {
    return true;
  } else {
    return false;
  }
};

/**
 * `verifyTransactionType` Verifies destination_account filled if this is transfer
 * @returns {boolean}- True if transfer and destination_account filled out
 */
const verifyTransactionType = () => {
  if (formData.value.transaction_type_id == 3) {
    if (
      formData.value.destination_account_id !== null &&
      formData.value.destination_account_id !== ""
    ) {
      return true;
    } else {
      return false;
    }
  } else {
    return true;
  }
};

/**
 * `verifyPaycheck` Verifies paycheck info is filled out if this is a paycheck
 * @returns {boolean}- True if all paycheck fields are filled and totals = gross
 */
const verifyPaycheck = () => {
  let payfields = false;
  let paytotal = false;
  let paychecksum = 0;
  if (isPaycheck.value) {
    if (paycheck.value.dca) {
      paychecksum += parseFloat(paycheck.value.dca);
    }
    if (paycheck.value.four_fifty_seven_b) {
      paychecksum += parseFloat(paycheck.value.four_fifty_seven_b);
    }
    if (paycheck.value.fsa) {
      paychecksum += parseFloat(paycheck.value.fsa);
    }
    if (paycheck.value.health) {
      paychecksum += parseFloat(paycheck.value.health);
    }
    if (amount.value) {
      paychecksum += parseFloat(amount.value);
    }
    if (paycheck.value.pension) {
      paychecksum += parseFloat(paycheck.value.pension);
    }
    if (paycheck.value.taxes) {
      paychecksum += parseFloat(paycheck.value.taxes);
    }
    if (paycheck.value.union_dues) {
      paychecksum += parseFloat(paycheck.value.union_dues);
    }
    if (
      paycheck.value.dca !== null &&
      paycheck.value.dca !== "" &&
      paycheck.value.four_fifty_seven_b !== null &&
      paycheck.value.four_fifty_seven_b !== "" &&
      paycheck.value.fsa !== null &&
      paycheck.value.fsa !== "" &&
      paycheck.value.gross !== null &&
      paycheck.value.gross !== "" &&
      paycheck.value.health !== null &&
      paycheck.value.health !== "" &&
      amount.value !== null &&
      amount.value !== "" &&
      paycheck.value.payee_id !== null &&
      paycheck.value.payee_id !== "" &&
      paycheck.value.pension !== null &&
      paycheck.value.pension !== "" &&
      paycheck.value.taxes !== null &&
      paycheck.value.taxes !== "" &&
      paycheck.value.union_dues !== null &&
      paycheck.value.union_dues !== ""
    ) {
      payfields = true;
    } else {
      payfields = false;
    }
    if (paycheck.value.gross === paychecksum.toFixed(2)) {
      paytotal = true;
      paycheckTotalsMatch.value = true;
    } else {
      paytotal = false;
      paycheckTotalsMatch.value = false;
    }
  } else {
    payfields = true;
    paytotal = true;
  }
  if (payfields && paytotal) {
    return true;
  } else {
    return false;
  }
};

/**
 * `submitForm` Submits the formData and creates/edits transaction.
 */
const submitForm = async () => {
  if (formData.value.transaction_type_id == 2) {
    formData.value.total_amount = amount.value;
  } else {
    formData.value.total_amount = -amount.value;
  }
  if (isPaycheck.value) {
    paycheck.value.net = amount.value;
    formData.value.paycheck = paycheck.value;
  }
  if (props.isEdit == false) {
    await addTransaction(formData.value);
  } else {
    console.log("edit");
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
  emit("updateDialog", false);
};

/**
 * `tagColor` Sets the tag color based on tag type.
 * @param {int} typeID - The tag type ID.
 * @return {color} - The color of the tag.
 */
const tagColor = typeID => {
  if (typeID == 1) {
    return "red";
  } else if (typeID == 2) {
    return "green";
  } else if (typeID == 3) {
    return "grey";
  }
};

/**
 * `reformatNumberToMoney` Formats an amount to currency.
 */
const reformatNumberToMoney = () => {
  if (amount.value) {
    amount.value = parseFloat(amount.value).toFixed(2);
  }
  if (paycheck.value.dca) {
    paycheck.value.dca = parseFloat(paycheck.value.dca).toFixed(2);
  }
  if (paycheck.value.four_fifty_seven_b) {
    paycheck.value.four_fifty_seven_b = parseFloat(
      paycheck.value.four_fifty_seven_b,
    ).toFixed(2);
  }
  if (paycheck.value.fsa) {
    paycheck.value.fsa = parseFloat(paycheck.value.fsa).toFixed(2);
  }
  if (paycheck.value.gross) {
    paycheck.value.gross = parseFloat(paycheck.value.gross).toFixed(2);
  }
  if (paycheck.value.health) {
    paycheck.value.health = parseFloat(paycheck.value.health).toFixed(2);
  }
  if (paycheck.value.pension) {
    paycheck.value.pension = parseFloat(paycheck.value.pension).toFixed(2);
  }
  if (paycheck.value.taxes) {
    paycheck.value.taxes = parseFloat(paycheck.value.taxes).toFixed(2);
  }
  if (paycheck.value.union_dues) {
    paycheck.value.union_dues = parseFloat(paycheck.value.union_dues).toFixed(
      2,
    );
  }
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
  checkFormComplete();
};

/**
 * `checkTagComplete` Checks if tag and amount are selected to add to table.
 */
const checkTagComplete = () => {
  if (
    tagAmount.value !== null &&
    tagAmount.value !== "" &&
    tagToAdd.value !== null &&
    tagToAdd.value !== ""
  ) {
    tagComplete.value = true;
  } else {
    tagComplete.value = false;
  }
};

/**
 * `clickTagAdd` Adds a tag to the tag table.
 */
const clickTagAdd = () => {
  let pretty_name = "";
  if (tagToAdd.value.parent) {
    pretty_name =
      tagToAdd.value.parent.tag_name + " : " + tagToAdd.value.tag_name;
  } else {
    pretty_name = tagToAdd.value.tag_name;
  }
  let tag_row = {
    tag_id: tagToAdd.value.id,
    tag_amt: parseFloat(Math.abs(tagAmount.value)).toFixed(2),
    tag_pretty_name: pretty_name,
  };
  formData.value.details.push(tag_row);
  details_table.value.reset();
  checkFormComplete();
};

/**
 * `clickTagRemove` Removes a tag from the tag table.
 */
const clickTagRemove = () => {
  if (selected.value) {
    for (const tag of selected.value) {
      formData.value.details = formData.value.details.filter(
        item => item.tag_id !== tag,
      );
    }
  }
  checkFormComplete();
};

/**
 * `verifyTagTotal` Verifies the total of tags equals total amount.
 * @returns - Returns True if totals match
 */
const verifyTagTotal = () => {
  let tagtotal = 0;
  if (formData.value.details) {
    formData.value.details.forEach(tag => {
      tagtotal += parseFloat(tag.tag_amt);
    });
  }
  if (tagtotal == amount.value) {
    return true;
  } else {
    return false;
  }
};

// Lifecycle hook...

onMounted(() => {
  // Perform actions on mount
  watchPassedFormData();
});
</script>
