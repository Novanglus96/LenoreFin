<template>
  <v-dialog
    persistent
    :fullscreen="smAndDown"
    :width="smAndDown ? undefined : '1200'"
  >
    <v-card>
      <v-card-title>
        <span class="text-h5">Add Multiple Transactions</span>
      </v-card-title>

      <v-card-text>
        <form @submit.prevent="submit">
          <!-- Batch-wide settings. These apply to every row; only the fields
               that genuinely vary row to row live in the grid below. -->
          <v-row dense align="center">
            <v-col :cols="smAndDown ? 12 : 4">
              <v-autocomplete
                label="Source Account*"
                :items="accounts"
                variant="outlined"
                :loading="accounts_isLoading"
                item-title="account_name"
                item-value="id"
                v-model="source_account_id"
                :error-messages="
                  attempted && !source_account_id
                    ? 'Source account is required.'
                    : ''
                "
                density="compact"
                hide-details="auto"
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
            <v-col :cols="smAndDown ? 12 : 3">
              <v-autocomplete
                label="Status*"
                :items="transaction_statuses"
                variant="outlined"
                :loading="transaction_statuses_isLoading"
                item-title="transaction_status"
                item-value="id"
                v-model="status_id"
                :error-messages="
                  attempted && !status_id ? 'Status is required.' : ''
                "
                density="compact"
                hide-details="auto"
              ></v-autocomplete>
            </v-col>
            <v-col :cols="smAndDown ? 12 : 5">
              <span class="text-caption text-medium-emphasis">
                Applies to every row. New rows start on
                {{ default_date }}.
              </span>
            </v-col>
          </v-row>

          <v-divider class="my-3"></v-divider>

          <!-- Column headings, desktop only. On mobile each field carries its
               own label instead, since the rows stack. -->
          <v-row dense v-if="!smAndDown" class="text-caption text-medium-emphasis">
            <v-col cols="2">Date*</v-col>
            <v-col cols="2">Type*</v-col>
            <v-col cols="2">Amount*</v-col>
            <v-col cols="3">Description*</v-col>
            <v-col cols="2">Tag</v-col>
            <v-col cols="1"></v-col>
          </v-row>

          <v-sheet
            v-for="(row, index) in rows"
            :key="row.key"
            :border="smAndDown"
            :rounded="smAndDown"
            :class="smAndDown ? 'pa-2 mb-3' : 'mb-1'"
            color="surface"
          >
            <div
              v-if="smAndDown"
              class="text-caption text-medium-emphasis mb-1"
            >
              Transaction {{ index + 1 }}
            </div>
            <v-row dense align="start">
              <v-col :cols="smAndDown ? 12 : 2">
                <VueDatePicker
                  v-model="row.transaction_date"
                  timezone="America/New_York"
                  model-type="yyyy-MM-dd"
                  :enable-time-picker="false"
                  auto-apply
                  format="yyyy-MM-dd"
                  :state="rowError(index, 'transaction_date') ? false : null"
                ></VueDatePicker>
                <span
                  v-if="rowError(index, 'transaction_date')"
                  class="text-error text-caption"
                >
                  {{ rowError(index, "transaction_date") }}
                </span>
              </v-col>
              <v-col :cols="smAndDown ? 12 : 2">
                <v-select
                  :label="smAndDown ? 'Type*' : undefined"
                  :items="transaction_types"
                  variant="outlined"
                  :loading="transaction_types_isLoading"
                  item-title="transaction_type"
                  item-value="id"
                  v-model="row.transaction_type_id"
                  :error-messages="rowError(index, 'transaction_type_id')"
                  density="compact"
                  hide-details="auto"
                  @update:model-value="typeChanged(row)"
                ></v-select>
              </v-col>
              <v-col :cols="smAndDown ? 12 : 2">
                <v-text-field
                  v-model="row.amount"
                  :label="smAndDown ? 'Amount*' : undefined"
                  variant="outlined"
                  :error-messages="rowError(index, 'amount')"
                  prefix="$"
                  type="number"
                  step="1.00"
                  density="compact"
                  hide-details="auto"
                  @blur="formatAmount(row)"
                ></v-text-field>
              </v-col>
              <v-col :cols="smAndDown ? 12 : 3">
                <v-combobox
                  v-model="row.description"
                  :items="descriptionOptions"
                  :label="smAndDown ? 'Description*' : undefined"
                  clearable
                  hide-no-data
                  hide-selected
                  :loading="description_history_isLoading"
                  variant="outlined"
                  :error-messages="rowError(index, 'description')"
                  density="compact"
                  hide-details="auto"
                  auto-select-first="exact"
                ></v-combobox>
              </v-col>
              <v-col :cols="smAndDown ? 12 : 2">
                <v-autocomplete
                  clearable
                  :label="smAndDown ? 'Tag' : undefined"
                  :items="tagsForRow(row)"
                  variant="outlined"
                  :loading="tags_isLoading"
                  item-title="tag_name"
                  item-value="id"
                  v-model="row.tag_id"
                  density="compact"
                  hide-details="auto"
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
                          :icon="
                            item.raw.is_system ? 'mdi-tag' : 'mdi-tag-outline'
                          "
                          :color="tagColor(item.raw.tag_type?.id)"
                        ></v-icon>
                      </template>
                    </v-list-item>
                  </template>
                </v-autocomplete>
              </v-col>
              <v-col
                :cols="smAndDown ? 12 : 1"
                class="d-flex align-center justify-end"
              >
                <v-tooltip text="Duplicate Row" location="top">
                  <template v-slot:activator="{ props }">
                    <v-btn
                      icon="mdi-content-duplicate"
                      variant="text"
                      size="small"
                      v-bind="props"
                      @click="duplicateRow(index)"
                    ></v-btn>
                  </template>
                </v-tooltip>
                <v-tooltip text="Remove Row" location="top">
                  <template v-slot:activator="{ props }">
                    <v-btn
                      icon="mdi-close"
                      variant="text"
                      size="small"
                      color="error"
                      v-bind="props"
                      :disabled="rows.length === 1"
                      @click="removeRow(index)"
                    ></v-btn>
                  </template>
                </v-tooltip>
              </v-col>
            </v-row>
            <!-- Transfers need a destination, so it only appears on the rows
                 that are actually transfers. -->
            <v-row dense v-if="row.transaction_type_id === 3">
              <v-col :cols="smAndDown ? 12 : 4" :offset="smAndDown ? 0 : 2">
                <v-autocomplete
                  clearable
                  label="Destination Account*"
                  :items="accounts"
                  variant="outlined"
                  :loading="accounts_isLoading"
                  item-title="account_name"
                  item-value="id"
                  v-model="row.destination_account_id"
                  :error-messages="rowError(index, 'destination_account_id')"
                  density="compact"
                  hide-details="auto"
                  class="mt-1"
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
          </v-sheet>

          <v-row dense align="center" class="mt-2">
            <v-col cols="auto">
              <v-btn
                prepend-icon="mdi-plus"
                variant="outlined"
                size="small"
                @click="addRow"
              >
                Add Row
              </v-btn>
            </v-col>
            <v-spacer></v-spacer>
            <v-col cols="auto">
              <span class="text-subtitle-2">
                Total:
                <span :class="batchTotal < 0 ? 'text-error' : 'text-success'">
                  {{ formatCurrency(batchTotal) }}
                </span>
              </span>
            </v-col>
          </v-row>

          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" variant="text" @click="closeDialog">
              Close
            </v-btn>
            <v-btn
              color="primary"
              variant="text"
              type="submit"
              :disabled="!isOnline"
            >
              Add {{ rows.length }}
            </v-btn>
          </v-card-actions>
        </form>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>
<script setup>
  import { ref, computed, defineEmits, defineProps, watch } from "vue";
  import { useDisplay } from "vuetify";
  import * as yup from "yup";
  import VueDatePicker from "@vuepic/vue-datepicker";
  import "@vuepic/vue-datepicker/dist/main.css";
  import { useAccounts } from "@/composables/accountsComposable";
  import { useTransactionTypes } from "@/composables/transactionTypesComposable";
  import { useTransactionStatuses } from "@/composables/transactionStatusesComposable";
  import { useTransactions } from "@/composables/transactionsComposable";
  import { useTags } from "@/composables/tagsComposable";
  import { useDescriptionHistory } from "@/composables/descriptionHistoryComposable";
  import { useOnlineStatus } from "@/composables/useOnlineStatus";

  const { isOnline } = useOnlineStatus();
  const { smAndDown } = useDisplay();

  const props = defineProps({
    account_id: { type: Number, default: null },
  });
  const emit = defineEmits(["updateDialog"]);

  const { accounts, isLoading: accounts_isLoading } = useAccounts();
  const { transaction_types, isLoading: transaction_types_isLoading } =
    useTransactionTypes();
  const { transaction_statuses, isLoading: transaction_statuses_isLoading } =
    useTransactionStatuses();
  const { tags, isLoading: tags_isLoading } = useTags();
  const { descriptionHistory, isLoading: description_history_isLoading } =
    useDescriptionHistory();
  const { addTransactions } = useTransactions();

  const today = new Date();
  const default_date = `${today.getFullYear()}-${String(
    today.getMonth() + 1,
  ).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;

  // Errors stay hidden until the first submit so a freshly opened form isn't
  // a wall of red.
  const attempted = ref(false);
  const source_account_id = ref(props.account_id);
  const status_id = ref(1);

  let nextRowKey = 0;
  const blankRow = () => ({
    key: nextRowKey++,
    transaction_date: default_date,
    transaction_type_id: 1,
    amount: null,
    description: null,
    source_account_id: null,
    destination_account_id: null,
    tag_id: null,
  });

  const rows = ref([blankRow(), blankRow(), blankRow()]);

  watch(
    () => props.account_id,
    val => {
      if (val) source_account_id.value = val;
    },
  );

  const rowSchema = yup.object({
    transaction_date: yup
      .string()
      .nullable()
      .required("Date is required."),
    transaction_type_id: yup
      .number()
      .typeError("Type is required.")
      .required("Type is required."),
    amount: yup
      .number()
      .typeError("Amount is required.")
      .required("Amount is required.")
      .positive("Must be greater than zero."),
    description: yup
      .string()
      .nullable()
      .required("Description is required."),
    destination_account_id: yup.mixed().when("transaction_type_id", {
      is: 3,
      then: schema =>
        schema.required("Destination account is required for transfers."),
      otherwise: schema => schema.nullable().notRequired(),
    }),
  });

  // One error map per row, recomputed as the grid is edited.
  const rowErrors = computed(() =>
    rows.value.map(row => {
      try {
        rowSchema.validateSync(row, { abortEarly: false });
        return {};
      } catch (err) {
        const messages = {};
        for (const issue of err.inner ?? []) {
          if (issue.path && !messages[issue.path]) {
            messages[issue.path] = issue.message;
          }
        }
        return messages;
      }
    }),
  );

  const rowError = (index, field) =>
    attempted.value ? (rowErrors.value[index]?.[field] ?? "") : "";

  const isValid = computed(
    () =>
      rows.value.length > 0 &&
      !!source_account_id.value &&
      !!status_id.value &&
      rowErrors.value.every(errors => Object.keys(errors).length === 0),
  );

  const descriptionOptions = computed(() =>
    (descriptionHistory.value ?? []).map(item => item.description_pretty),
  );

  const batchTotal = computed(() =>
    rows.value.reduce((sum, row) => {
      const amount = parseFloat(row.amount);
      if (isNaN(amount)) return sum;
      return sum + (row.transaction_type_id === 2 ? amount : -amount);
    }, 0),
  );

  // Mirrors TagTable's filtering: expense rows see expense + shared tags,
  // income rows see income + shared, transfers see everything. tag_type is
  // nullable on TagOut, so an untyped tag stays visible rather than throwing.
  const tagsForRow = row => {
    const all = tags.value ?? [];
    if (row.transaction_type_id === 1) {
      return all.filter(t => !t.tag_type || [1, 3].includes(t.tag_type.id));
    }
    if (row.transaction_type_id === 2) {
      return all.filter(t => !t.tag_type || [2, 3].includes(t.tag_type.id));
    }
    return all;
  };

  const tagColor = typeID => {
    if (typeID == 1) return "error";
    if (typeID == 2) return "success";
    if (typeID == 3) return "info";
    return undefined;
  };

  // Switching type can invalidate the chosen tag and makes a destination
  // account meaningless, so clear both rather than submit a stale pair.
  const typeChanged = row => {
    row.destination_account_id = null;
    if (row.tag_id && !tagsForRow(row).some(t => t.id === row.tag_id)) {
      row.tag_id = null;
    }
  };

  const addRow = () => {
    rows.value.push(blankRow());
  };

  const duplicateRow = index => {
    rows.value.splice(index + 1, 0, {
      ...rows.value[index],
      key: nextRowKey++,
    });
  };

  const removeRow = index => {
    rows.value.splice(index, 1);
    if (rows.value.length === 0) rows.value.push(blankRow());
  };

  const formatAmount = row => {
    if (row.amount !== null && row.amount !== "") {
      row.amount = formatCurrencyNoSymbol(row.amount);
    }
  };

  const resetRows = () => {
    attempted.value = false;
    rows.value = [blankRow(), blankRow(), blankRow()];
  };

  const submit = () => {
    attempted.value = true;
    if (!isValid.value) return;

    const payload = rows.value.map(row => {
      const amount = Math.abs(parseFloat(row.amount));
      const tag = (tags.value ?? []).find(t => t.id === row.tag_id);
      return {
        transaction_date: row.transaction_date,
        transaction_type_id: row.transaction_type_id,
        status_id: status_id.value,
        total_amount: row.transaction_type_id === 2 ? amount : -amount,
        description: row.description,
        source_account_id: source_account_id.value,
        destination_account_id:
          row.transaction_type_id === 3 ? row.destination_account_id : null,
        memo: null,
        checkNumber: null,
        edit_date: default_date,
        add_date: default_date,
        // A batch row carries a single tag covering the whole amount, so
        // full_toggle keeps the detail in step if the amount is edited.
        details: tag
          ? [
              {
                tag_id: tag.id,
                tag_amt: amount.toFixed(2),
                tag_pretty_name: tag.tag_name,
                tag_full_toggle: true,
              },
            ]
          : [],
      };
    });

    addTransactions(payload);
    resetRows();
    emit("updateDialog", false);
  };

  const closeDialog = () => {
    resetRows();
    emit("updateDialog", false);
  };

  const formatCurrency = value =>
    new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);

  const formatCurrencyNoSymbol = value =>
    new Intl.NumberFormat("en-US", {
      style: "decimal",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
      useGrouping: false,
    }).format(value);
</script>
