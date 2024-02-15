<template>
  <v-card variant="outlined" :elevation="4" class="bg-white">
    <template v-slot:append>
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
      <span class="text-subtitle-2 text-accent">Upcoming Transactions</span>
    </template>
    <template v-slot:text>
      <vue3-datatable
        :rows="transactions"
        :columns="columns"
        :loading="isLoading"
        :totalRows="transactions ? transactions.length : 0"
        :isServerMode="false"
        pageSize="10"
        :hasCheckbox="false"
        :stickyHeader="true"
        noDataContent="No transactions"
        ref="trans_table"
        height="405px"
        skin="bh-table-striped bh-table-compact"
        :pageSizeOptions="[10]"
        :showPageSize="false"
        paginationInfo="Showing {0} to {1} of {2} transactions"
        class="alt-pagination"
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
            >${{ row.value.pretty_total }}</span
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
          <div v-for="tag in row.value.tags" :key="tag">
            <v-icon
              icon="mdi-tag"
              :color="row.value.status.id == 1 ? 'grey' : 'black'"
            ></v-icon>
            <span
              :class="
                row.value.status.id == 1
                  ? 'font-italic text-grey'
                  : 'font-weight-bold text-black'
              "
              >{{ tag }}</span
            >
          </div>
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
import { useTransactions } from "@/composables/transactionsComposable";
import Vue3Datatable from "@bhplugin/vue3-datatable";
import "@bhplugin/vue3-datatable/dist/style.css";
import { ref } from "vue";

const { isLoading, transactions } = useTransactions();
const columns = ref([
  { field: "transaction_date", title: "Date", type: "date", width: "120px" },
  { field: "pretty_total", title: "Amount", type: "number", width: "100px" },
  { field: "description", title: "Description" },
  { field: "tags", title: "Tag(s)" },
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
</script>
<style>
.alt-pagination .bh-pagination .bh-page-item {
  background-color: #06966a;
  color: white;
}
</style>
