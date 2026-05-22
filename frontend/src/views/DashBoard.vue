<template>
  <div>
    <GraphAreaWidget />
    <v-row class="pa-1 ga-1 rounded" no-gutters>
      <v-col class="rounded"><BudgetsWidget :widget="true" /></v-col>
    </v-row>
    <v-row class="pa-1 ga-1 rounded" no-gutters>
      <v-col class="rounded">
        <RemindersWidget variant="upcoming" />
      </v-col>
    </v-row>
    <v-row class="pa-1 ga-1 rounded" no-gutters>
      <v-col class="rounded">
        <TransactionTableWidget
          :key="1"
          variant="upcoming"
          :data="transactions"
          :loading="isLoading"
          :fetching="isFetching"
        />
      </v-col>
    </v-row>
  </div>
</template>
<script setup>
  import GraphAreaWidget from "@/components/GraphAreaWidget.vue";
  import RemindersWidget from "@/components/RemindersWidget.vue";
  import TransactionTableWidget from "@/components/TransactionTableWidget.vue";
  import BudgetsWidget from "@/components/BudgetsWidget.vue";
  import { onMounted } from "vue";
  import { useTransactions } from "@/composables/transactionsComposable";
  import { useTransactionsStore } from "@/stores/transactions";

  const transactions_store = useTransactionsStore();

  // Reset pageinfo to dashboard defaults every time the dashboard mounts.
  // AccountDetailView mutates pageinfo when you visit an account; without this
  // reset, navigating back via the browser back button leaves the wrong
  // account_id in the query key and the dashboard shows a blank/wrong state.
  onMounted(() => {
    transactions_store.pageinfo.account_id = null;
    transactions_store.pageinfo.forecast = true;
    transactions_store.pageinfo.view_type = 2;
    transactions_store.pageinfo.page = 1;
    transactions_store.pageinfo.maxdays = 14;
  });

  const { isLoading, transactions, isFetching } = useTransactions();
</script>
<style scoped>
  .custom-height {
    height: 340px;
    /* Adjust the height as needed */
    overflow-y: hidden;
    /* Add this if you want a vertical scrollbar for overflow */
  }
</style>
