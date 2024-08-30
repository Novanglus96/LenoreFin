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
            @click="importFileDialog = true"
          ></v-btn>
        </template>
      </v-tooltip>
      <FileImportForm
        v-model="importFileDialog"
        @update-dialog="updateImportFileDialog"
      />
    </template>
    <template v-slot:title>
      <span class="text-subtitle-2 text-secondary">Transfers</span>
    </template>
    <template v-slot:text>
      <vue3-datatable
        :rows="rule_transfers ? rule_transfers : []"
        :columns="columns"
        :loading="isLoading"
        :totalRows="rule_transfers ? rule_transfers.length : 0"
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
        <template #transaction_total="data">
          <span>${{ data.value.transaction_total }}</span>
        </template>
        <template #actions="data">
          <div>
            <v-btn
              icon="mdi-pencil"
              flat
              variant="plain"
              @click="editTransfer(data.value.id)"
            ></v-btn>
          </div>
        </template> </vue3-datatable
    ></template>
  </v-card>
</template>
<script setup>
import { ref } from "vue";
import Vue3Datatable from "@bhplugin/vue3-datatable";
import "@bhplugin/vue3-datatable/dist/style.css";

const columns = ref([
  { field: "id", title: "ID", isUnique: true, hide: true },
  { field: "transaction_date", title: "Date", type: "date", width: "120px" },
  {
    field: "transaction_total",
    title: "Amount",
    type: "number",
    width: "100px",
  },
  { field: "description", title: "Description" },
  { field: "memo", title: "Memo" },
  { field: "actions", title: "Actions" },
]);
const rule_transfers = ref([
  {
    id: 1,
    transaction_date: "2024-08-01",
    transaction_total: 100,
    description: "Some transfer",
    memo: "40 Target 60 Wawa",
  },
  {
    id: 2,
    transaction_date: "2024-08-01",
    transaction_total: 200,
    description: "Some transfer # 2",
    memo: "140 Target 60 Wawa",
  },
  {
    id: 3,
    transaction_date: "2024-08-01",
    transaction_total: 300,
    description: "Some transfer # 3",
    memo: "240 Target 60 Wawa",
  },
  {
    id: 4,
    transaction_date: "2024-08-01",
    transaction_total: 400,
    description: "Some transfer # 4",
    memo: "340 Target 60 Wawa",
  },
  {
    id: 5,
    transaction_date: "2024-08-01",
    transaction_total: 500,
    description: "Some transfer # 5",
    memo: "440 Target 60 Wawa",
  },
]);
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
