<template>
  <v-card variant="outlined" :elevation="4" class="bg-white ma-0 pa-0 ga-0">
    <v-card-text>
      <vue3-datatable
        :rows="props.transactions ? props.transactions : null"
        :columns="columns"
        :loading="isLoading"
        :totalRows="props.transactions ? props.transactions.length : 0"
        :isServerMode="false"
        pageSize="10"
        :hasCheckbox="false"
        :stickyHeader="true"
        noDataContent="No transactions"
        ref="tag_trans_table"
        height="405px"
        skin="bh-table-striped bh-table-compact"
        :pageSizeOptions="[10]"
        :showPageSize="false"
        paginationInfo="Showing {0} to {1} of {2} transactions"
        class="alt-pagination"
        ><!--height="280px"-->
        <template #transaction_date="row">
          {{ row.value.transaction_date }}
        </template>
        <template #total_amount="row">
          <span
            :class="row.value.total_amount < 0 ? 'text-red' : 'text-green'"
            >{{ formatCurrency(row.value.total_amount) }}</span
          >
        </template>
        <template #tag_total="row">
          <span :class="row.value.tag_total < 0 ? 'text-red' : 'text-green'">{{
            formatCurrency(row.value.tag_total)
          }}</span>
        </template>
        <template #description="row">
          {{ row.value.description }}
        </template>
        <template #memo="row">
          {{ row.memo }}
        </template>
        <template #pretty_account="row">
          {{ row.value.pretty_account }}
        </template>
      </vue3-datatable>
    </v-card-text>
  </v-card>
</template>
<script setup>
import { defineProps, ref } from "vue";
import Vue3Datatable from "@bhplugin/vue3-datatable";
import "@bhplugin/vue3-datatable/dist/style.css";

const props = defineProps({
  transactions: Object,
});

const columns = ref([
  {
    field: "transaction_date",
    title: "Date",
    type: "date",
    width: "120px",
  },
  {
    field: "total_amount",
    title: "Trans Amount",
    type: "number",
    width: "100px",
  },
  { field: "tag_total", title: "Tag Amount", type: "number", width: "100px" },
  { field: "description", title: "Description" },
  { field: "memo", title: "Memo" },
  { field: "pretty_account", title: "Account" },
]);

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
</style>
