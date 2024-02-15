<template>
  <div>
    <v-row class="pa-1 ga-1 rounded" no-gutters>
      <v-col class="rounded">
        <v-card v-if="!isLoading">
          <v-card-title>This Month</v-card-title>
          <v-card-text>
            <v-container>
              <v-row dense>
                <v-col cols="1" class="text-right font-weight-bold">
                  Total:
                </v-col>
                <v-col>
                  <span
                    :class="{
                      'text-red': tag_transactions.total_amt < 0,
                      'text-green': tag_transactions.total_amt > 0,
                      'text-black': tag_transactions.total_amt === 0,
                    }"
                    >${{ tag_transactions.total_amt }}</span
                  >
                </v-col>
              </v-row>
              <v-row dense>
                <v-col cols="1" class="text-right font-weight-bold">
                  Average:
                </v-col>
                <v-col>
                  <span
                    :class="{
                      'text-red': tag_transactions.total_amt < 0,
                      'text-green': tag_transactions.total_amt > 0,
                      'text-black': tag_transactions.total_amt === 0,
                    }"
                    >${{ tag_transactions.average_amt }}</span
                  >
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
        </v-card>
        <v-skeleton-loader type="card" v-else></v-skeleton-loader>
      </v-col>
    </v-row>
    <v-row class="pa-1 ga-1 rounded" no-gutters>
      <v-col class="rounded">
        <v-card v-if="!isLoading">
          <v-card-title>Transactions</v-card-title>
          <v-card-text>
            <vue3-datatable
              :rows="tag_transactions.details"
              :columns="columns"
              :loading="isLoading"
              :totalRows="
                tag_transactions.details ? tag_transactions.details.length : 0
              "
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
              <template #tag_amount="row">
                <span
                  :class="row.value.tag_amount < 0 ? 'text-red' : 'text-green'"
                  >${{ row.value.tag_amount }}</span
                >
              </template>
              <template #transaction_description="row">
                {{ row.value.transaction_description }}
              </template>
              <template #transaction_memo="row">
                {{ row.transaction_memo }}
              </template>
              <template #transaction_pretty_account="row">
                {{ row.value.transaction_pretty_account }}
              </template>
            </vue3-datatable>
          </v-card-text>
        </v-card>
        <v-skeleton-loader type="card" v-else></v-skeleton-loader>
      </v-col>
    </v-row>
  </div>
</template>
<script setup>
import { defineProps, ref } from "vue";
import { useGraphTransactions } from "@/composables/tagsComposable";
import Vue3Datatable from "@bhplugin/vue3-datatable";
import "@bhplugin/vue3-datatable/dist/style.css";

const props = defineProps({
  tagID: {
    type: Number,
  },
});

const columns = ref([
  { field: "transaction_date", title: "Date", type: "date", width: "120px" },
  { field: "tag_amount", title: "Amount", type: "number", width: "100px" },
  { field: "transaction_description", title: "Description" },
  { field: "transaction_memo", title: "Memo" },
  { field: "transaction_pretty_account", title: "Account" },
]);
const { tag_transactions, isLoading } = useGraphTransactions(props.tagID, 0);
</script>
