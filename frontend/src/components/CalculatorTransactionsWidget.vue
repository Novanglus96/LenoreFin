<template>
  <v-card variant="outlined" :elevation="4" class="bg-white">
    <template v-slot:title>
      <span class="text-subtitle-2 text-secondary"
        >{{ calculator ? calculator.rule.name : null }} Transactions</span
      >
    </template>
    <template v-slot:text>
      <vue3-datatable
        :rows="calculator ? calculator.transactions : []"
        :columns="columns"
        :loading="calculator_isLoading"
        :totalRows="calculator ? calculator.transactions.length : 0"
        :isServerMode="false"
        pageSize="10"
        :hasCheckbox="true"
        noDataContent="No transactions"
        ref="trans_table"
        skin="bh-table-striped bh-table-compact"
        :pageSizeOptions="[10]"
        :showPageSize="false"
        paginationInfo="Showing {0} to {1} of {2} transactions"
        class="alt-pagination"
        @rowSelect="rowSelected"
        ><!--height="280px"-->
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
            >{{ formatCurrency(row.value.pretty_total) }}</span
          >
        </template>
        <template #details="row">
          <span
            :class="
              row.value.status.id == 1
                ? 'font-italic text-grey text-body-2'
                : 'font-weight-bold text-black text-body-2'
            "
            v-for="detail in row.value.details"
            :key="detail"
          >
            <v-icon
              icon="mdi-tag"
              size="x-small"
              :color="row.value.status.id == 1 ? 'grey' : 'black'"
              v-if="detail"
            ></v-icon>
            {{ detail.tag.tag_name }} :
            <span
              :class="getClassForMoney(detail.detail_amt, row.value.status.id)"
              >{{ formatCurrency(detail.detail_amt) }}</span
            >&nbsp;
          </span>
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
import Vue3Datatable from "@bhplugin/vue3-datatable";
import "@bhplugin/vue3-datatable/dist/style.css";
import { ref, defineProps, watch } from "vue";
import { useCalculator } from "@/composables/calculatorComposable";
import { usePlanningStore } from "@/stores/planning";

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
const selected = ref([]);
const trans_table = ref(null);

const { calculator, isLoading: calculator_isLoading } = useCalculator(
  local_rule_id.value,
  local_timeframe.value,
);

const columns = ref([
  { field: "transaction_date", title: "Date", type: "date", width: "120px" },
  { field: "pretty_total", title: "Total", type: "number", width: "100px" },
  { field: "details", title: "Tag Amounts", type: "number", width: "120px" },
  { field: "description", title: "Description" },
  { field: "pretty_account", title: "Account" },
]);

const rowSelected = () => {
  selected.value = trans_table.value.getSelectedRows();
  planningstore.calculator.selected_transactions = selected.value;
};

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
watch(props.ruleID, newValue => {
  local_rule_id.value = newValue;
});
watch(props.timeframe, newValue => {
  local_timeframe.value = newValue;
});
const formatCurrency = value => {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
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
