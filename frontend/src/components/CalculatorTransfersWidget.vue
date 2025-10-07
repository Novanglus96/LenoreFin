<template>
  <v-card variant="outlined" :elevation="4" class="bg-surface">
    <v-card-title class="text-left">
      <span class="text-subtitle-2 text-primary">
        {{ calculator ? calculator.rule.name : null }} Transfers
      </span>
      <v-tooltip text="Add Transfer" location="top">
        <template v-slot:activator="{ props }">
          <v-btn
            icon="mdi-cash-fast"
            flat
            variant="plain"
            v-bind="props"
            @click="addTransfer"
            :disabled="
              planningstore.calculator.selected_transactions.length == 0 ||
              selectedTransfer.length != 0
                ? true
                : false
            "
            size="small"
            color="success"
          ></v-btn>
        </template>
      </v-tooltip>
      <v-tooltip text="Edit Transfer" location="top">
        <template v-slot:activator="{ props }">
          <v-btn
            icon="mdi-cash-edit"
            flat
            variant="plain"
            v-bind="props"
            @click="editTransfer"
            :disabled="
              planningstore.calculator.selected_transactions.length > 0 &&
              selectedTransfer.length > 0
                ? false
                : true
            "
            size="small"
            color="warning"
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
    </v-card-title>
    <v-card-text class="ma-0 pa-0 ga-0">
      <v-data-table
        :headers="displayHeaders"
        :items="calculator ? calculator.transfers : []"
        :items-length="calculator ? calculator.transfers.length : 0"
        :loading="calculator_isLoading"
        item-value="id"
        v-model:items-per-page="itemsPerPage"
        :items-per-page-options="[
          {
            value: 3,
            title: 3,
          },
        ]"
        items-per-page-text="Transfers per page"
        no-data-text="No transfers!"
        loading-text="Loading transfers..."
        disable-sort
        :show-select="true"
        fixed-footer
        striped="odd"
        density="compact"
        width="100%"
        return-object
        v-model="selectedTransfer"
        select-strategy="single"
        v-model:page="page"
        :header-props="{ class: 'font-weight-bold bg-secondary' }"
        :row-props="getRowProps"
        v-if="props.ruleID"
        class="bg-background"
      >
        <template
          v-slot:item.data-table-select="{
            internalItem,
            isSelected,
            toggleSelect,
          }"
        >
          <v-checkbox-btn
            :model-value="isSelected(internalItem)"
            @update:model-value="toggleSelect(internalItem)"
            :disabled="!isSelectable(internalItem.raw)"
          ></v-checkbox-btn>
        </template>
        <template v-slot:bottom>
          <div class="text-center pt-2">
            <v-pagination v-model="page" :length="pageCount"></v-pagination>
          </div>
        </template>
        <template v-slot:[`header.transaction_date`] v-if="mdAndUp">
          <div class="text-center">Date</div>
        </template>
        <template v-slot:[`header.pretty_total`] v-if="mdAndUp">
          <div class="text-center">Amount</div>
        </template>
        <template v-slot:[`item.transaction_date`]="{ item }" v-if="mdAndUp">
          <div class="text-center">
            {{ formatDate(item.transaction_date, true) }}
          </div>
        </template>
        <template v-slot:[`item.pretty_total`]="{ item }" v-if="mdAndUp">
          <div class="text-center">
            <span :class="getClassForMoney(item.pretty_total)">
              {{ formatCurrency(item.pretty_total) }}
            </span>
          </div>
        </template>
        <template v-slot:[`item.memo`]="{ item }" v-if="mdAndUp">
          <span class="text-caption text-pre-wrap">{{ item.memo }}</span>
        </template>
        <!-- Mobile View -->
        <template v-slot:[`item.mobile`]="{ item }">
          <v-container class="ma-0 pa-0 ga-0">
            <v-row dense class="ma-0 pa-0 ga-0">
              <v-col class="ma-0 pa-0 ga-0 text-center" cols="4">
                {{ formatDate(item.transaction_date, true) }}
              </v-col>
              <v-col
                class="ma-0 pa-0 ga-0 text-truncatte font-weight-bold"
                cols="8"
              >
                {{ item.description }}
              </v-col>
            </v-row>
            <v-row dense class="ma-0 pa-0 ga-0">
              <v-col class="ma-0 pa-0 ga-0 text-center" cols="4">
                <span :class="getClassForMoney(item.pretty_total)">
                  {{ formatCurrency(item.pretty_total) }}
                </span>
              </v-col>
              <v-col class="ma-0 pa-0 ga-0" cols="8">
                <span class="text-caption text-pre-wrap">{{ item.memo }}</span>
              </v-col>
            </v-row>
          </v-container>
        </template>
      </v-data-table>
      <CalculatorTransactionForm
        v-model="calculatorEditTransactionDialog"
        @update-dialog="updateCalculatorEditTransactionDialog"
        :isEdit="true"
        :key="1"
        :passedFormData="selectedTransfer[0]"
        :newTotal="newTotal"
        :newMemo="newMemo"
      />
    </v-card-text>
  </v-card>
</template>
<script setup>
  import { ref, defineProps, watch, computed } from "vue";
  import { useCalculator } from "@/composables/calculatorComposable";
  import { usePlanningStore } from "@/stores/planning";
  import CalculatorTransactionForm from "./CalculatorTransactionForm.vue";
  import { useDisplay } from "vuetify";

  const selectedTransfer = ref([]);
  const { mdAndUp } = useDisplay();

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
  const newMemo = ref(null);
  const newTotal = ref(null);

  const { calculator, isLoading: calculator_isLoading } = useCalculator(
    local_rule_id.value,
    local_timeframe.value,
  );
  const page = ref(1);
  const itemsPerPage = ref(3);
  const pageCount = computed(() =>
    calculator.value && itemsPerPage.value
      ? Math.ceil(calculator.value.transfers.length / itemsPerPage.value)
      : 1,
  );

  const newTransferData = ref(null);

  const headers = ref([
    { title: "Date", key: "transaction_date", width: "80px" },
    { title: "Amount", key: "pretty_total", width: "100px" },
    { title: "Description", key: "description" },
    { title: "Memo", key: "memo" },
  ]);
  const displayHeaders = computed(() => {
    if (mdAndUp.value) {
      return headers.value;
    }
    // For small screens, use your single mobile column
    return [{ title: "", key: "mobile" }];
  });

  watch(props.ruleID, newValue => {
    local_rule_id.value = newValue;
  });
  watch(props.timeframe, newValue => {
    local_timeframe.value = newValue;
  });
  const getClassForMoney = amount => {
    let color = "";

    if (amount < 0) {
      color = "text-error";
    } else {
      color = "text-success";
    }

    return color;
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
        parseFloat(transaction.tag_total) !=
        parseFloat(transaction.total_amount)
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
  const editTransfer = () => {
    let memo = "";
    let totalAmount = 0;
    for (const transaction of planningstore.calculator.selected_transactions) {
      totalAmount = addDecimals(totalAmount, parseFloat(transaction.tag_total));
      if (
        parseFloat(transaction.tag_total) !=
        parseFloat(transaction.total_amount)
      ) {
        memo +=
          formatCurrency(transaction.tag_total) +
          " " +
          transaction.description +
          " (Split)\n";
      } else {
        memo +=
          formatCurrency(transaction.tag_total) +
          " " +
          transaction.description +
          "\n";
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
  const isSelectable = item =>
    item && planningstore.calculator.selected_transactions.length != 0;

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
  function getRowProps({ item }) {
    let rowformat = "text-body-2";
    const isSelected = selectedTransfer.value.some(sel => sel.id === item.id);
    if (isSelected) {
      rowformat += " bg-primary-lighten-3";
    }
    return {
      class: rowformat,
    };
  }
</script>
