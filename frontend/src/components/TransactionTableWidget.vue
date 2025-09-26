<template>
  <v-card variant="outlined" :elevation="4" class="bg-white">
    <v-card-title>
      <span class="text-subtitle-2 text-secondary">
        {{ title[props.variant] }}
        <v-tooltip
          text="File Import"
          location="top"
          v-if="!smAndDown && props.variant === 'account'"
        >
          <template v-slot:activator="{ props }">
            <v-btn
              icon="mdi-file-import"
              flat
              variant="plain"
              v-bind="props"
              @click="importFileDialog = true"
              :disabled="isActive"
              color="grey"
            ></v-btn>
          </template>
        </v-tooltip>
        <FileImportForm
          v-model="importFileDialog"
          @update-dialog="updateImportFileDialog"
          v-if="!smAndDown"
        />
      </span>
    </v-card-title>
    <v-card-text class="ma-0 pa-0 ga-0">
      <!-- Large Display View -->
      <v-data-table-server
        :headers="displayHeaders"
        :items="localTransactions"
        :items-length="localTransactions.length"
        :loading="isActive"
        item-value="id"
        v-model:items-per-page="transactions_store.pageinfo.page_size"
        v-model:page="localPage"
        :items-per-page-options="[
          {
            value: transactions_store.pageinfo.page_size,
            title: transactions_store.pageinfo.page_size,
          },
        ]"
        items-per-page-text="Transactions per page"
        no-data-text="No transactions!"
        loading-text="Loading transactions..."
        disable-sort
        :show-select="props.variant === 'account'"
        fixed-footer
        striped="odd"
        density="compact"
        expand-on-click
        :hide-default-header="mdAndUp ? false : true"
        :hide-default-footer="props.variant === 'upcoming'"
        width="100%"
        @update:model-value="rowChanged"
        @update:options="pageTurned"
        return-object
        v-model="selected_all"
        :page="localPage"
        :row-props="getRowProps"
        :header-props="{ class: 'font-weight-bold' }"
      >
        <template
          v-slot:header.data-table-select="{
            allSelected,
            selectAll,
            someSelected,
          }"
        >
          <v-checkbox-btn
            :indeterminate="someSelected && !allSelected"
            :model-value="allSelected"
            color="secondary"
            @update:model-value="selectAll(!allSelected)"
          ></v-checkbox-btn>
        </template>

        <template
          v-slot:item.data-table-select="{
            internalItem,
            isSelected,
            toggleSelect,
          }"
        >
          <v-checkbox-btn
            :model-value="isSelected(internalItem)"
            color="secondary"
            @update:model-value="toggleSelect(internalItem)"
            :disabled="!isSelectable(internalItem.raw)"
          ></v-checkbox-btn>
        </template>
        <template v-slot:bottom v-if="props.variant != 'upcoming'">
          <div class="text-center pt-2">
            <v-pagination
              v-model="localPage"
              :length="localPageTotal"
            ></v-pagination>
          </div>
        </template>
        <template v-slot:[`header.pretty_total`] v-if="mdAndUp">
          <div class="font-weight-bold">
            {{
              props.variant === "tag" || props.variant === "budget"
                ? "Total Amt"
                : "Amount"
            }}
          </div>
        </template>
        <template
          v-slot:[`header.balance`]
          v-if="mdAndUp && props.variant != 'upcoming'"
        >
          <div class="font-weight-bold">
            {{
              props.variant === "tag" || props.variant === "budget"
                ? "Tag Amt"
                : "Balance"
            }}
          </div>
        </template>
        <template v-slot:[`item.status`]="{ item }" v-if="mdAndUp">
          <v-tooltip text="Pending" location="top">
            <template v-slot:activator="{ props }">
              <v-icon
                icon="mdi-circle-medium"
                color="grey"
                v-if="item.status.id == 1"
                v-bind="props"
              ></v-icon>
            </template>
          </v-tooltip>
          <v-tooltip text="Cleared" location="top">
            <template v-slot:activator="{ props }">
              <v-icon
                icon="mdi-check-bold"
                color="green"
                v-if="item.status.id == 2"
                v-bind="props"
              ></v-icon>
            </template>
          </v-tooltip>
          <v-tooltip text="Reconciled" location="top">
            <template v-slot:activator="{ props }">
              <v-icon
                icon="mdi-alpha-r-circle-outline"
                color="green"
                v-if="item.status.id == 3"
                v-bind="props"
              ></v-icon>
            </template>
          </v-tooltip>
          <v-tooltip text="Image(s)" location="top">
            <template v-slot:activator="{ props }">
              <v-icon
                icon="mdi-paperclip"
                v-if="item.attachments"
                color="grey"
                v-bind="props"
              ></v-icon>
            </template>
          </v-tooltip>
          <v-tooltip text="Forecast" location="top">
            <template v-slot:activator="{ props }">
              <v-icon
                icon="mdi-chart-box"
                v-if="item.simulated"
                color="grey"
                v-bind="props"
              ></v-icon>
            </template>
          </v-tooltip>
          <v-tooltip text="Reminder" location="top">
            <template v-slot:activator="{ props }">
              <v-icon
                icon="mdi-bell"
                v-if="item.simulated && item.id < 0 && item.id >= -10000"
                color="amber"
                v-bind="props"
              ></v-icon>
            </template>
          </v-tooltip>
          <v-tooltip text="Paycheck" location="top">
            <template v-slot:activator="{ props }">
              <v-icon
                icon="mdi-cash-multiple"
                v-if="item.paycheck"
                color="amber"
                v-bind="props"
              ></v-icon>
            </template>
          </v-tooltip>
          <v-tooltip text="Check" location="top">
            <template v-slot:activator="{ props }">
              <div class="icon-with-text" v-if="item.checkNumber">
                <v-icon
                  icon="mdi-checkbook"
                  color="amber"
                  v-bind="props"
                ></v-icon>
                <span
                  :class="
                    item.status.id == 1
                      ? 'font-italic text-grey icon-text'
                      : 'font-weight-bold text-black icon-text'
                  "
                >
                  #{{ item.checkNumber }}
                </span>
              </div>
            </template>
          </v-tooltip>
        </template>
        <template v-slot:[`item.pretty_total`]="{ item }" v-if="mdAndUp">
          <span :class="getClassForMoney(item.pretty_total, item.status.id)">
            {{ formatCurrency(item.pretty_total) }}
          </span>
        </template>
        <template
          v-slot:[`item.balance`]="{ item }"
          v-if="mdAndUp && props.variant != 'upcoming'"
        >
          <span
            :class="getClassForMoney(item.balance, item.status.id)"
            v-if="props.variant != 'budget'"
          >
            {{ formatCurrency(item.balance) }}
          </span>
          <span
            :class="getClassForMoney(item.tag_total, item.status.id)"
            v-else
          >
            {{ formatCurrency(item.tag_total) }}
          </span>
        </template>
        <template
          v-slot:[`item.tags`]="{ item }"
          v-if="mdAndUp && props.variant != 'tag'"
        >
          <span v-for="tag in item.tags" :key="tag">
            <v-icon
              icon="mdi-tag"
              size="x-small"
              :color="item.status.id == 1 ? 'grey' : 'black'"
            ></v-icon>
            {{ tag }}&nbsp;
          </span>
        </template>
        <!-- Mobile View -->
        <template v-slot:[`item.mobile`]="{ item }">
          <v-container class="ma-0 pa-0 ga-0">
            <v-row dense class="ma-0 pa-0 ga-0">
              <v-col class="ma-0 pa-0 ga-0 font-weight-bold" cols="1">
                <v-icon
                  icon="mdi-circle-medium"
                  color="grey"
                  v-if="item.status.id == 1"
                ></v-icon>
                <v-icon
                  icon="mdi-check-bold"
                  color="green"
                  v-if="item.status.id == 2"
                  v-bind="props"
                ></v-icon>
                <v-icon
                  icon="mdi-alpha-r-circle-outline"
                  color="green"
                  v-if="item.status.id == 3"
                  v-bind="props"
                ></v-icon>
              </v-col>
              <v-col class="ma-0 pa-0 ga-0" cols="3">
                {{ formatDate(item.transaction_date, true) }}
              </v-col>
              <v-col class="ma-0 pa-0 ga-0 text-right">
                <span
                  :class="getClassForMoney(item.pretty_total, item.status.id)"
                >
                  {{ formatCurrency(item.pretty_total) }}
                </span>
                <v-icon
                  icon="mdi-wallet-bifold"
                  size="x-small"
                  :color="item.status.id == 1 ? 'grey' : 'black'"
                  v-if="props.variant === 'tag' || props.variant === 'budget'"
                ></v-icon>
              </v-col>
              <v-col
                class="ma-0 pa-0 ga-0 text-right"
                v-if="props.variant != 'upcoming'"
              >
                <span
                  :class="getClassForMoney(item.balance, item.status.id)"
                  v-if="props.variant != 'budget'"
                >
                  {{ formatCurrency(item.balance) }}
                </span>
                <span
                  :class="getClassForMoney(item.tag_total, item.status.id)"
                  v-else
                >
                  {{ formatCurrency(item.tag_total) }}
                </span>
                <v-icon
                  icon="mdi-tag-hidden"
                  size="x-small"
                  :color="item.status.id == 1 ? 'grey' : 'black'"
                  v-if="props.variant === 'tag' || props.variant === 'budget'"
                ></v-icon>
              </v-col>
            </v-row>
            <v-row dense class="ma-0 pa-0 ga-0">
              <v-col class="ma-0 pa-0 ga-0 font-weight-bold text-truncate">
                {{ item.description }}
              </v-col>
            </v-row>
            <v-row dense class="ma-0 pa-0 ga-0">
              <v-col
                class="ma-0 pa-0 ga-0 text-secondary text-left font-weight-italic text-truncate"
              >
                <span
                  :class="
                    item.status.id == 1
                      ? 'text-secondary-lighten-2'
                      : 'text-secondary'
                  "
                >
                  {{ item.pretty_account }}
                </span>
              </v-col>
              <v-col class="ma-0 pa-0 ga-0" cols="1" v-if="item.attachments">
                <v-icon
                  icon="mdi-paperclip"
                  color="grey"
                  v-bind="props"
                ></v-icon>
              </v-col>
              <v-col class="ma-0 pa-0 ga-0" cols="1" v-if="item.simulated">
                <v-icon
                  icon="mdi-chart-box"
                  color="grey"
                  v-bind="props"
                ></v-icon>
              </v-col>
              <v-col
                class="ma-0 pa-0 ga-0"
                cols="1"
                v-if="item.simulated && item.id < 0 && item.id >= -10000"
              >
                <v-icon icon="mdi-bell" color="amber" v-bind="props"></v-icon>
              </v-col>
              <v-col class="ma-0 pa-0 ga-0" cols="1" v-if="item.paycheck">
                <v-icon icon="mdi-cash-multiple" color="amber"></v-icon>
              </v-col>
              <v-col class="ma-0 pa-0 ga-0" cols="1" v-if="item.checkNumber">
                <v-icon
                  icon="mdi-checkbook"
                  color="amber"
                  v-bind="props"
                ></v-icon>
              </v-col>
            </v-row>
            <v-row
              dense
              class="ma-0 pa-0 ga-0"
              v-if="props.variant != 'tag' && props.variant != 'budget'"
            >
              <v-col class="ma-0 pa-0 ga-0 text-center text-truncate">
                <span v-for="tag in item.tags" :key="tag">
                  <v-icon
                    icon="mdi-tag"
                    size="x-small"
                    :color="item.status.id == 1 ? 'grey' : 'black'"
                    v-if="tag"
                  ></v-icon>
                  <v-icon
                    icon="mdi-tag-hidden"
                    size="x-small"
                    :color="item.status.id == 1 ? 'grey' : 'black'"
                    v-else
                  ></v-icon>
                  {{ tag }}&nbsp;
                </span>
                <span v-if="item.tags.length === 0">
                  <v-icon
                    icon="mdi-tag-hidden"
                    size="x-small"
                    :color="item.status.id == 1 ? 'grey' : 'black'"
                  ></v-icon>
                </span>
              </v-col>
            </v-row>
          </v-container>
        </template>
        <template v-slot:top v-if="props.variant != 'upcoming'">
          <v-fab
            key="fab1"
            :app="true"
            color="success"
            location="right bottom"
            size="small"
            icon
            @click="transactionAddFormDialog = true"
            variant="elevated"
            v-if="selected_all.length === 0 && props.variant === 'account'"
          >
            <v-icon icon="mdi-invoice-plus"></v-icon>
          </v-fab>
          <TransactionForm
            v-model="transactionAddFormDialog"
            :isEdit="false"
            @update-dialog="updateAddDialog"
            :account_id="props.account"
            :passedFormData="blankForm"
          />
          <v-fab
            key="fab2"
            :app="true"
            :color="open ? '' : 'primary'"
            location="right bottom"
            size="small"
            icon
            :disabled="true"
            variant="plain"
          >
            <v-icon></v-icon>
            <v-speed-dial
              v-model="open"
              :location="menuLocation"
              :transition="transition"
              activator="parent"
              persistent
              :close-on-content-click="false"
            >
              <v-tooltip text="Uncheck All" location="left">
                <template v-slot:activator="{ props }">
                  <v-btn
                    icon="mdi-checkbox-multiple-marked-outline"
                    key="1"
                    color="warning"
                    @click="uncheck_all"
                    v-bind="props"
                  ></v-btn>
                </template>
              </v-tooltip>
              <v-tooltip text="Remove Transaction(s)" location="left">
                <template v-slot:activator="{ props }">
                  <v-btn
                    icon="mdi-invoice-remove"
                    :disabled="
                      (selected_transactions &&
                        selected_transactions.length === 0) ||
                      deleteDisable
                    "
                    color="error"
                    v-bind="props"
                    @click="showDeleteDialog = true"
                    key="2"
                  ></v-btn>
                </template>
              </v-tooltip>
              <v-dialog width="500" v-model="showDeleteDialog">
                <v-card title="Dialog">
                  <v-card-text>
                    Are you sure you want to delete these
                    {{ selected_transactions.length }} transactions?
                    <br />
                    <span class="text-red text-subtitle-2 font-italic">
                      * Reminder transactions will not be deleted.
                    </span>
                  </v-card-text>

                  <v-card-actions>
                    <v-spacer></v-spacer>

                    <v-btn
                      text="Confirm"
                      @click="
                        clickRemoveTransaction(selected_transactions);
                        showDeleteDialog = false;
                      "
                    ></v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>
              <v-tooltip text="Edit Transaction(s)" location="left">
                <template v-slot:activator="{ props }">
                  <v-btn
                    :icon="
                      selected_transactions.length > 1
                        ? 'mdi-calendar-edit'
                        : 'mdi-invoice-text-edit'
                    "
                    :disabled="
                      (selected_transactions &&
                        selected_transactions.length === 0) ||
                      editDisable
                    "
                    @click="displayEditForm"
                    v-bind="props"
                    key="3"
                  ></v-btn>
                </template>
              </v-tooltip>
              <TransactionForm
                v-model="transactionEditFormDialog"
                :isEdit="true"
                @update-dialog="updateEditDialog"
                :passedFormData="editTransaction"
              />
              <MultipleTransactionEditForm
                v-model="showMultipleTransactionEditDialog"
                @update-dialog="updateMultipleEditDialog"
                :transactionIds="editTransactions"
              />
              <v-tooltip text="Clear / Add Transaction(s)" location="left">
                <template v-slot:activator="{ props }">
                  <v-btn
                    icon="mdi-invoice-text-clock"
                    :disabled="clearDisable"
                    @click="
                      clickClearTransaction(
                        selected_transactions,
                        selected_reminders,
                      )
                    "
                    v-bind="props"
                    key="4"
                  ></v-btn>
                </template>
              </v-tooltip>
            </v-speed-dial>
          </v-fab>
        </template>
      </v-data-table-server>
    </v-card-text>
  </v-card>
</template>
<script setup>
  import { ref, defineProps, computed, watch } from "vue";
  import TransactionForm from "@/components/TransactionForm.vue";
  import FileImportForm from "@/components/FileImportForm.vue";
  import { useTransactionsStore } from "@/stores/transactions";
  import MultipleTransactionEditForm from "@/components/MultipleTransactionEditForm.vue";
  import { useDisplay } from "vuetify";
  import { useTransactions } from "@/composables/transactionsComposable";
  import { useReminders } from "@/composables/remindersComposable";

  const { removeTransaction, clearTransaction } = useTransactions();
  const { addReminderTransaction } = useReminders();
  const { smAndDown, mdAndUp } = useDisplay();
  const transactions_store = useTransactionsStore();
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, "0");
  const day = String(today.getDate()).padStart(2, "0");
  const formattedDate = `${year}-${month}-${day}`;
  const showDeleteDialog = ref(false);
  const showMultipleTransactionEditDialog = ref(false);
  const transactionAddFormDialog = ref(false);
  const importFileDialog = ref(false);
  const transactionEditFormDialog = ref(false);
  const deleteDisable = ref(true);
  const editDisable = ref(true);
  const clearDisable = ref(true);
  const editTransactions = ref([]);
  const open = ref(false);

  const props = defineProps({
    variant: { type: String, default: "account" },
    data: { type: Object },
    loading: { type: Boolean, default: true },
    fetching: { type: Boolean, default: true },
  });

  const localTransactions = ref(props.data ? props.data.transactions : []);
  const localLoading = ref(props.loading);
  const localFetching = ref(props.fetching);
  const localPage = ref(props.data ? props.data.current_page : 1);
  const localPageTotal = ref(props.data ? props.data.total_pages : 1);

  const title = computed(() => {
    return {
      account: "Transactions",
      tag: "Tag Transactions",
      upcoming: "Upcoming Transactions",
    };
  });

  watch(
    () => props.data,
    val => {
      localTransactions.value = val.transactions;
      localPage.value = val.current_page;
      localPageTotal.value = val.total_pages;
    },
  );

  watch(
    () => props.loading,
    val => {
      localLoading.value = val;
    },
  );

  watch(
    () => props.fetching,
    val => {
      localFetching.value = val;
    },
  );

  const blankForm = ref({
    id: 0,
    status: {
      id: 1,
    },
    transaction_type: {
      id: 1,
    },
    transaction_date: formattedDate,
    memo: "",
    source_account_id: parseInt(props.account),
    destination_account_id: null,
    edit_date: formattedDate,
    add_date: formattedDate,
    tag_id: 1,
    total_amount: 0,
  });
  const editTransaction = ref({
    id: 0,
    transaction_date: formattedDate,
    total_amount: 0,
    status: {
      id: 1,
      transaction_status: "Pending",
    },
    memo: "",
    description: null,
    edit_date: formattedDate,
    add_date: formattedDate,
    transaction_type: {
      id: 1,
      transaction_type: "Expense",
    },
    reminder: null,
    paycheck: null,
    balance: 0,
    pretty_account: null,
    tags: [],
    details: [],
    pretty_total: 0,
    source_account_id: 0,
    destination_account_id: null,
  });

  const displayEditForm = () => {
    if (selected_transactions.value.length === 1) {
      transactionEditFormDialog.value = true;
    } else {
      editTransactions.value = selected_transactions.value;
      showMultipleTransactionEditDialog.value = true;
    }
  };

  const isActive = computed(
    () => !(localLoading.value === false && localFetching.value === false),
  );

  const selected_transactions = ref([]);
  const selected_reminders = ref([]);
  const selected_all = ref([]);
  const isSelectable = item => item.id > -10000;

  const headers = ref([
    { title: "", key: "status", width: "115px" },
    { title: "Date", key: "transaction_date", width: "120px" },
    { title: "Amount", key: "pretty_total", width: "100px" },
    { title: "Balance", key: "balance", width: "100px" },
    { title: "Description", key: "description" },
    { title: "Tag(s)", key: "tags", width: "200px" },
    { title: "Account", key: "pretty_account" },
  ]);
  const displayHeaders = computed(() => {
    if (mdAndUp.value) {
      // If upcoming, filter out the "balance" header
      if (props.variant === "upcoming") {
        return headers.value.filter(h => h.key !== "balance");
      }
      if (props.variant === "tag" || props.variant === "budget") {
        return headers.value.filter(h => h.key !== "tags");
      }
      // Otherwise, return all headers
      return headers.value;
    }
    // For small screens, use your single mobile column
    return [{ title: "", key: "mobile" }];
  });
  const getClassForMoney = (amount, status) => {
    let color = "";

    if (status == 1) {
      if (amount < 0) {
        color = "text-red-lighten-1";
      } else {
        color = "text-green-lighten-1";
      }
    } else {
      if (amount < 0) {
        color = "text-red";
      } else {
        color = "text-green";
      }
    }

    return color;
  };
  const uncheck_all = () => {
    selected_transactions.value = [];
    selected_reminders.value = [];
    selected_all.value = [];
    open.value = false;
  };
  const rowChanged = newSelection => {
    selected_transactions.value = [];
    selected_reminders.value = [];
    for (const selectedrow of newSelection) {
      if (selectedrow.id > 0) {
        selected_transactions.value.push(selectedrow.id);
        editTransaction.value = selectedrow;
      } else {
        let reminder_trans_obj = {
          reminder_id: selectedrow.reminder_id,
          transaction_date: selectedrow.transaction_date,
        };
        selected_reminders.value.push(reminder_trans_obj);
      }
    }
    if (selected_reminders.value.length == 0) {
      deleteDisable.value = false;
      editDisable.value = false;
    } else {
      deleteDisable.value = true;
      editDisable.value = true;
    }
    if (
      selected_transactions.value.length > 0 ||
      selected_reminders.value.length > 0
    ) {
      clearDisable.value = false;
      open.value = true;
    } else {
      clearDisable.value = true;
      open.value = false;
    }
  };

  const clickRemoveTransaction = async transactions => {
    removeTransaction(transactions);
    selected_all.value = [];
  };

  const clickClearTransaction = async (transactions, reminderTransactions) => {
    clearTransaction(transactions);
    console.log("emitting clear transaction", transactions);
    open.value = false;
    selected_all.value = [];
    reminderTransactions.forEach(transaction => {
      addReminderTransaction(transaction);
      console.log("emitting add reminder transaction", transaction);
    });
    selected_transactions.value = [];
    selected_reminders.value = [];
    clearDisable.value = true;
  };

  const updateAddDialog = () => {
    transactionAddFormDialog.value = false;
  };

  const updateImportFileDialog = () => {
    importFileDialog.value = false;
  };

  const updateEditDialog = () => {
    transactionEditFormDialog.value = false;
  };
  const updateMultipleEditDialog = () => {
    showMultipleTransactionEditDialog.value = false;
  };
  const formatCurrency = value => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };
  const formatDate = (input, padDay = false) => {
    // Normalize input to a Date object
    const date = input instanceof Date ? input : new Date(input);

    if (isNaN(date)) {
      console.warn("Invalid date:", input);
      return "";
    }

    const month = date.toLocaleString("en-US", { month: "short" }); // 'Sep'
    const day = date.getDate(); // 16

    return `${month}-${padDay ? String(day).padStart(2, "0") : day}`;
  };

  function pageTurned({ page }) {
    transactions_store.pageinfo.page = page;
  }
  function getStatusFormat(status) {
    if (status == 1) {
      return "font-italic text-grey text-body-2";
    } else {
      return "font-weight-bold text-black text-body-2";
    }
  }
  function getRowProps({ item }) {
    let rowformat = getStatusFormat(item.status.id);
    if (item.status.id == 1 && props.variant === "account") {
      rowformat += " bg-grey-lighten-4";
    }
    return {
      class: rowformat,
    };
  }
</script>
<style scoped>
  .icon-with-text {
    position: relative;
    display: inline-block;
  }

  .icon-text {
    position: absolute;
    top: 0;
    right: 1;
    color: black;
    padding: 4px 1px;
    font-size: 0.7rem;
  }

  .floating-button-group {
    position: fixed;
    bottom: 82px;
    right: 12px;
    display: flex;
    flex-direction: column;
    gap: 1px;
    z-index: 1000; /* Ensure it appears above most content */
  }
  /* Change selected row background */
  /* reach into child component DOM with :deep */
</style>
