<template>
  <div>
    <template v-for="widget in visibleWidgets" :key="widget.id">
      <GraphAreaWidget v-if="widget.id === 'graphs'" />
      <v-row
        v-else-if="widget.id === 'budgets'"
        class="pa-1 ga-1 rounded"
        no-gutters
      >
        <v-col class="rounded"><BudgetsWidget :widget="true" /></v-col>
      </v-row>
      <FavoriteAccountsWidget v-else-if="widget.id === 'account_balances'" />
      <v-row
        v-else-if="widget.id === 'reminders'"
        class="pa-1 ga-1 rounded"
        no-gutters
      >
        <v-col class="rounded">
          <RemindersWidget variant="upcoming" />
        </v-col>
      </v-row>
      <v-row
        v-else-if="widget.id === 'transactions'"
        class="pa-1 ga-1 rounded"
        no-gutters
      >
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
    </template>
  </div>
</template>
<script setup>
  import { computed, onMounted } from "vue";
  import GraphAreaWidget from "@/components/GraphAreaWidget.vue";
  import RemindersWidget from "@/components/RemindersWidget.vue";
  import TransactionTableWidget from "@/components/TransactionTableWidget.vue";
  import BudgetsWidget from "@/components/BudgetsWidget.vue";
  import FavoriteAccountsWidget from "@/components/FavoriteAccountsWidget.vue";
  import { useTransactions } from "@/composables/transactionsComposable";
  import { useTransactionsStore } from "@/stores/transactions";
  import { useDashboardConfig } from "@/composables/dashboardComposable";

  const transactions_store = useTransactionsStore();

  onMounted(() => {
    transactions_store.pageinfo.account_id = null;
    transactions_store.pageinfo.forecast = true;
    transactions_store.pageinfo.view_type = 2;
    transactions_store.pageinfo.page = 1;
    transactions_store.pageinfo.maxdays = 14;
  });

  const { isLoading, transactions, isFetching } = useTransactions();
  const { dashboardConfig, DEFAULT_LAYOUT } = useDashboardConfig();

  const visibleWidgets = computed(() =>
    (dashboardConfig.value?.layout ?? DEFAULT_LAYOUT).filter(w => w.visible),
  );
</script>
