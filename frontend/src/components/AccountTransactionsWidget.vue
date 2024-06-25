<template>
  <v-card variant="outlined" :elevation="4" class="bg-white">
    <template v-slot:append>
      <v-tooltip text="File Import" location="top">
        <template v-slot:activator="{ props }">
          <v-btn
            icon="mdi-file-import"
            flat
            variant="plain"
            v-bind="props"
            @click="importFileDialog = true"
          ></v-btn>
        </template>
      </v-tooltip>
      <FileImportForm
        v-model="importFileDialog"
        @update-dialog="updateImportFileDialog"
      />
      <v-menu location="start">
        <template v-slot:activator="{ props }">
          <v-btn icon="mdi-cog" flat size="xs" v-bind="props"> </v-btn>
        </template>
        <v-card width="100">
          <v-card-text>Test</v-card-text>
        </v-card>
      </v-menu>
    </template>
    <template v-slot:title>
      <span class="text-subtitle-2 text-secondary">Transactions</span>
    </template>
    <template v-slot:text>
      <v-tooltip text="Clear Transaction(s)" location="top">
        <template v-slot:activator="{ props }">
          <v-btn
            icon="mdi-invoice-text-clock"
            flat
            :disabled="selected && selected.length === 0"
            variant="plain"
            @click="clickClearTransaction(selected)"
            v-bind="props"
          ></v-btn>
        </template>
      </v-tooltip>
      <v-tooltip text="Edit Transaction" location="top">
        <template v-slot:activator="{ props }">
          <v-btn
            icon="mdi-invoice-text-edit"
            flat
            :disabled="
              (selected && selected.length === 0) || selected.length > 1
            "
            variant="plain"
            @click="transactionEditFormDialog = true"
            v-bind="props"
          ></v-btn>
        </template>
      </v-tooltip>
      <TransactionForm
        v-model="transactionEditFormDialog"
        @add-transaction="clickAddTransaction"
        @edit-transaction="clickEditTransaction"
        :isEdit="true"
        @update-dialog="updateEditDialog"
        :passedFormData="editTransaction"
      />

      <v-tooltip text="Remove Transaction(s)" location="top">
        <template v-slot:activator="{ props }">
          <v-btn
            icon="mdi-invoice-remove"
            flat
            :disabled="selected && selected.length === 0"
            variant="plain"
            color="error"
            v-bind="props"
            @click="showDeleteDialog = true"
          ></v-btn>
        </template>
      </v-tooltip>
      <v-dialog width="500" v-model="showDeleteDialog">
        <v-card title="Dialog">
          <v-card-text>
            Are you sure you want to delete these
            {{ selected.length }} transactions? <br /><span
              class="text-red text-subtitle-2 font-italic"
              >* Reminder transactions will not be deleted.</span
            >
          </v-card-text>

          <v-card-actions>
            <v-spacer></v-spacer>

            <v-btn
              text="Confirm"
              @click="
                clickRemoveTransaction(selected);
                showDeleteDialog = false;
              "
            ></v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
      <v-tooltip text="Add New Transaction" location="top">
        <template v-slot:activator="{ props }">
          <v-btn
            icon="mdi-invoice-plus"
            flat
            variant="plain"
            color="success"
            @click="transactionAddFormDialog = true"
            v-bind="props"
          ></v-btn>
        </template>
      </v-tooltip>
      <TransactionForm
        v-model="transactionAddFormDialog"
        @add-transaction="clickAddTransaction"
        @edit-transaction="clickEditTransaction"
        :isEdit="false"
        @update-dialog="updateAddDialog"
        :account_id="props.account"
        :passedFormData="blankForm"
      />
      <vue3-datatable
        :rows="transactions ? transactions.transactions : []"
        :columns="columns"
        :loading="isLoading"
        :totalRows="transactions ? transactions.total_records : 0"
        :isServerMode="true"
        :pageSize="transactions_store.pageinfo.page_size"
        :hasCheckbox="true"
        :stickyHeader="true"
        noDataContent="No transactions"
        search=""
        @rowSelect="rowSelected"
        ref="trans_table"
        height="810px"
        skin="bh-table-striped bh-table-compact"
        :pageSizeOptions="[60]"
        :showPageSize="false"
        paginationInfo="Showing {0} to {1} of {2} transactions"
        class="alt-pagination"
        @change="pageChanged"
        ><!--height="280px"-->
        <template #status.transaction_status="row">
          <v-tooltip text="Pending" location="top">
            <template v-slot:activator="{ props }">
              <v-icon
                icon="mdi-circle-medium"
                color="grey"
                v-if="row.value.status.id == 1"
                v-bind="props"
              ></v-icon>
            </template>
          </v-tooltip>
          <v-tooltip text="Cleared" location="top">
            <template v-slot:activator="{ props }">
              <v-icon
                icon="mdi-check-bold"
                color="green"
                v-if="row.value.status.id == 2"
                v-bind="props"
              ></v-icon>
            </template>
          </v-tooltip>
          <v-tooltip text="Reconciled" location="top">
            <template v-slot:activator="{ props }">
              <v-icon
                icon="mdi-alpha-r-circle-outline"
                color="green"
                v-if="row.value.status.id == 3"
                v-bind="props"
              ></v-icon>
            </template>
          </v-tooltip>
          <v-tooltip text="Reminder" location="top">
            <template v-slot:activator="{ props }">
              <v-icon
                icon="mdi-bell"
                v-if="row.value.reminder"
                color="amber"
                v-bind="props"
              ></v-icon>
            </template>
          </v-tooltip>
          <v-tooltip text="Paycheck" location="top">
            <template v-slot:activator="{ props }">
              <v-icon
                icon="mdi-checkbook"
                v-if="row.value.paycheck"
                color="amber"
                v-bind="props"
              ></v-icon>
            </template>
          </v-tooltip>
        </template>
        <template #transaction_date="row">
          <span
            :class="
              row.value.status.id == 1
                ? 'font-italic text-grey'
                : 'font-weight-bold text-black'
            "
            >{{ row.value.transaction_date }}</span
          >
        </template>
        <template #pretty_total="row">
          <span
            :class="
              getClassForMoney(row.value.pretty_total, row.value.status.id)
            "
            >${{ row.value.pretty_total }}</span
          >
        </template>
        <template #balance="row">
          <span
            :class="getClassForMoney(row.value.balance, row.value.status.id)"
            >${{ row.value.balance }}</span
          >
        </template>
        <template #description="row">
          <span
            :class="
              row.value.status.id == 1
                ? 'font-italic text-grey'
                : 'font-weight-bold text-black'
            "
            >{{ row.value.description }}</span
          >
        </template>
        <template #tags="row">
          <span
            :class="
              row.value.status.id == 1
                ? 'font-italic text-grey'
                : 'font-weight-bold text-black'
            "
            v-for="tag in row.value.tags"
            :key="tag"
          >
            <v-icon
              icon="mdi-tag"
              :color="row.value.status.id == 1 ? 'grey' : 'black'"
            ></v-icon>
            {{ tag }}&nbsp;
          </span>
        </template>
        <template #pretty_account="row">
          <span
            :class="
              row.value.status.id == 1
                ? 'font-italic text-grey'
                : 'font-weight-bold text-black'
            "
            >{{ row.value.pretty_account }}</span
          >
        </template>
      </vue3-datatable>
    </template>
  </v-card>
</template>
<script setup>
import { ref, defineProps, defineEmits } from "vue";
import { useTransactions } from "@/composables/transactionsComposable";
import TransactionForm from "@/components/TransactionForm";
import FileImportForm from "@/components/FileImportForm";
import Vue3Datatable from "@bhplugin/vue3-datatable";
import "@bhplugin/vue3-datatable/dist/style.css";
import { useTransactionsStore } from "@/stores/transactions";

const transactions_store = useTransactionsStore();
const today = new Date();
const year = today.getFullYear();
const month = String(today.getMonth() + 1).padStart(2, "0");
const day = String(today.getDate()).padStart(2, "0");
const formattedDate = `${year}-${month}-${day}`;
const showDeleteDialog = ref(false);
const transactionAddFormDialog = ref(false);
const importFileDialog = ref(false);
const transactionEditFormDialog = ref(false);
const props = defineProps({
  account: Number,
  maxdays: { type: Number, default: 14 },
  forecast: { type: Boolean, default: false },
});
const emit = defineEmits([
  "addTransaction",
  "removeTransaction",
  "editTransaction",
  "clearTransaction",
]);

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

const { isLoading, transactions, removeTransaction, clearTransaction } =
  useTransactions();

const pageChanged = data => {
  transactions_store.pageinfo.page = data.current_page;
};

const selected = ref([]);
const columns = ref([
  { field: "id", title: "ID", isUnique: true, hide: true },
  { field: "status.transaction_status", title: "", width: "70px" },
  { field: "transaction_date", title: "Date", type: "date", width: "120px" },
  { field: "pretty_total", title: "Amount", type: "number", width: "100px" },
  { field: "balance", title: "Balance", width: "100px" },
  { field: "description", title: "Description" },
  { field: "tags", title: "Tag(s)", width: "200px" },
  { field: "pretty_account", title: "Account" },
]);
const getClassForMoney = (amount, status) => {
  let color = "";
  let font = "";

  if (status == 1) {
    font = "font-italic";
    if (amount < 0) {
      color = "text-red-lighten-1";
    } else {
      color = "text-green-lighten-1";
    }
  } else {
    font = "font-weight-bold";
    if (amount < 0) {
      color = "text-red";
    } else {
      color = "text-green";
    }
  }

  return color + " " + font;
};
const rowSelected = () => {
  selected.value = [];
  let selectedrows = trans_table.value.getSelectedRows();
  for (const selectedrow of selectedrows) {
    selected.value.push(selectedrow.id);
    editTransaction.value = selectedrow;
  }
};
const trans_table = ref(null);

const clickAddTransaction = async () => {
  emit("addTransaction", props.account);
};

const clickRemoveTransaction = async transactions => {
  transactions.forEach(transaction => {
    removeTransaction(transaction);
    selected.value = [];
  });
  trans_table.value.clearSelectedRows();
};

const clickClearTransaction = async transactions => {
  transactions.forEach(transaction => {
    clearTransaction(transaction);
    selected.value = [];
  });
  trans_table.value.clearSelectedRows();
};

const clickEditTransaction = async transaction_id => {
  emit("editTransaction", transaction_id);
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
</script>
<style>
.alt-pagination .bh-pagination .bh-page-item {
  background-color: #06966a;
  color: white;
}
</style>
