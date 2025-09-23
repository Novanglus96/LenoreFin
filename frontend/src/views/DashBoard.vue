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
  import { useTransactions } from "@/composables/transactionsComposable";

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
