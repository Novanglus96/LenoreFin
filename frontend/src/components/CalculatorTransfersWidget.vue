<template>
  <v-card variant="outlined" :elevation="4" class="bg-white">
    <template v-slot:append>
      <v-tooltip text="Add Transfer" location="top">
        <template v-slot:activator="{ props }">
          <v-btn
            icon="mdi-cash-fast"
            flat
            variant="plain"
            v-bind="props"
            @click="addTransfer"
            :disabled="
              planningstore.calculator.selected_transactions.length == 0
                ? true
                : false
            "
          ></v-btn>
        </template>
      </v-tooltip>

      <CalculatorTransactionForm
        v-model="calculatorAddTransactionDialog"
        @update-dialog="updateCalculatorAddTransactionDialog"
        :isEdit="false"
        :key="0"
        :passedFormData="newTransferData"
      />
    </template>
    <template v-slot:title>
      <span class="text-subtitle-2 text-secondary"
        >{{ calculator ? calculator.rule.name : null }} Transfers</span
      >
    </template>
    <template v-slot:text>
      <vue3-datatable
        :rows="calculator ? calculator.transfers : []"
        :columns="columns"
        :loading="calculator_isLoading"
        :totalRows="calculator ? calculator.transfers.length : 0"
        :isServerMode="false"
        pageSize="3"
        :hasCheckbox="false"
        :stickyHeader="true"
        firstArrow="First"
        lastArrow="Last"
        previousArrow="Prev"
        nextArrow="Next"
        :showNumbersCount="3"
        noDataContent="No transfers"
        search=""
        ref="transfers_table"
        height="236px"
        skin="bh-table-striped bh-table-compact"
        :pageSizeOptions="[3]"
        :showPageSize="false"
        paginationInfo="Showing {0} to {1} of {2} transfers"
        class="alt-pagination"
      >
        <template #pretty_total="row">
          <span :class="getClassForMoney(row.value.pretty_total)">{{
            formatCurrency(row.value.pretty_total)
          }}</span>
        </template>
        <template #memo="row">
          <span :style="{ whiteSpace: 'pre-line' }" class="text-body-2">{{
            row.value.memo
          }}</span>
        </template>
        <template #actions="data">
          <div>
            <v-btn
              icon="mdi-pencil"
              flat
              variant="plain"
              @click="editTransfer(data.value)"
              :disabled="
                planningstore.calculator.selected_transactions.length == 0 ||
                data.value.id < 0
                  ? true
                  : false
              "
            ></v-btn>
          </div>
        </template>
      </vue3-datatable>
      <CalculatorTransactionForm
        v-model="calculatorEditTransactionDialog"
        @update-dialog="updateCalculatorEditTransactionDialog"
        :isEdit="true"
        :key="1"
        :passedFormData="selectedTransaction"
        :newTotal="newTotal"
        :newMemo="newMemo"
    /></template>
  </v-card>
</template>
<script setup>
import { ref, defineProps, watch } from "vue";
import Vue3Datatable from "@bhplugin/vue3-datatable";
import "@bhplugin/vue3-datatable/dist/style.css";
import { useCalculator } from "@/composables/calculatorComposable";
import { usePlanningStore } from "@/stores/planning";
import CalculatorTransactionForm from "./CalculatorTransactionForm.vue";

const planningstore = usePlanningStore();

const props = defineProps({
  ruleID: {
    type: Number,
  },
  timeframe: {
    type: Number,
  },
});

const local_rule_id = ref(props.ruleID);
const local_timeframe = ref(props.timeframe);
const calculatorAddTransactionDialog = ref(false);
const calculatorEditTransactionDialog = ref(false);
const selectedTransaction = ref(null);
const newMemo = ref(null);
const newTotal = ref(null);

const { calculator, isLoading: calculator_isLoading } = useCalculator(
  local_rule_id.value,
  local_timeframe.value,
);

const newTransferData = ref(null);
const columns = ref([
  { field: "id", title: "ID", isUnique: true, hide: true },
  { field: "transaction_date", title: "Date", type: "date", width: "120px" },
  {
    field: "pretty_total",
    title: "Amount",
    type: "number",
    width: "100px",
  },
  { field: "description", title: "Description" },
  { field: "memo", title: "Memo" },
  { field: "actions", title: "Actions" },
]);

watch(props.ruleID, newValue => {
  local_rule_id.value = newValue;
});
watch(props.timeframe, newValue => {
  local_timeframe.value = newValue;
});
const getClassForMoney = amount => {
  let color = "";
  let font = "";

  font = "font-weight-bold";
  if (amount < 0) {
    color = "text-red";
  } else {
    color = "text-green";
  }

  return color + " " + font;
};

const updateCalculatorAddTransactionDialog = value => {
  calculatorAddTransactionDialog.value = value;
};

const updateCalculatorEditTransactionDialog = value => {
  calculatorEditTransactionDialog.value = value;
};

// Date variables...
const today = new Date();
const year = today.getFullYear();
const month = String(today.getMonth() + 1).padStart(2, "0");
const day = String(today.getDate()).padStart(2, "0");
const formattedDate = `${year}-${month}-${day}`;

const addTransfer = () => {
  calculatorAddTransactionDialog.value = true;
  let memo = "";
  let description = calculator.value.rule.name + " Transfer";
  let totalAmount = 0;
  for (const transaction of planningstore.calculator.selected_transactions) {
    totalAmount = addDecimals(totalAmount, parseFloat(transaction.tag_total));
    if (
      parseFloat(transaction.tag_total) != parseFloat(transaction.total_amount)
    ) {
      memo +=
        Intl.NumberFormat("en-US", {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        }).format(Math.abs(transaction.tag_total)) +
        " " +
        transaction.description +
        " (Split)\n";
    } else {
      memo +=
        Intl.NumberFormat("en-US", {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        }).format(Math.abs(transaction.tag_total)) +
        " " +
        transaction.description +
        "\n";
    }
  }
  memo = memo.trimEnd();
  newTransferData.value = {
    transaction_date: formattedDate,
    total_amount: totalAmount,
    status_id: 1,
    memo: memo,
    description: description,
    edit_date: formattedDate,
    add_date: formattedDate,
    transaction_type_id: 3,
    paycheck_id: null,
    details: [
      {
        tag_amt: totalAmount,
        tag_pretty_name: "Transfer",
        tag_id: 34,
        tag_full_toggle: true,
      },
    ],
    source_account_id: calculator.value.rule.source_account_id,
    destination_account_id: calculator.value.rule.destination_account_id,
  };
};
const editTransfer = trans => {
  selectedTransaction.value = trans;
  let memo = "";
  let totalAmount = 0;
  for (const transaction of planningstore.calculator.selected_transactions) {
    totalAmount = addDecimals(totalAmount, parseFloat(transaction.tag_total));
    if (
      parseFloat(transaction.tag_total) != parseFloat(transaction.total_amount)
    ) {
      memo +=
        transaction.tag_total + " " + transaction.description + " (Split)\n";
    } else {
      memo += transaction.tag_total + " " + transaction.description + "\n";
    }
  }
  memo = memo.trimEnd();
  newTotal.value = totalAmount;
  newMemo.value = memo;
  calculatorEditTransactionDialog.value = true;
};
const formatCurrency = value => {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
};

function addDecimals(num1, num2, precision = 2) {
  const factor = Math.pow(10, precision);
  return Math.round((num1 + num2) * factor) / factor;
}
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
</style>
