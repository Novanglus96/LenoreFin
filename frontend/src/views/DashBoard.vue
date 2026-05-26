<template>
  <div>
    <div class="d-flex justify-end px-1 pt-1">
      <v-btn
        icon="mdi-view-dashboard-edit"
        size="small"
        variant="text"
        color="primary"
        @click="editorOpen = true"
      />
    </div>
    <template v-for="widget in visibleWidgets" :key="widget.id">
      <GraphAreaWidget v-if="widget.id === 'graphs'" />
      <v-row
        v-else-if="widget.id === 'budgets'"
        class="pa-1 ga-1 rounded"
        no-gutters
      >
        <v-col class="rounded"><BudgetsWidget :widget="true" /></v-col>
      </v-row>
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
    <DashboardEditor v-model="editorOpen" />
  </div>
</template>
<script setup>
  import { ref, computed, onMounted } from "vue";
  import GraphAreaWidget from "@/components/GraphAreaWidget.vue";
  import RemindersWidget from "@/components/RemindersWidget.vue";
  import TransactionTableWidget from "@/components/TransactionTableWidget.vue";
  import BudgetsWidget from "@/components/BudgetsWidget.vue";
  import DashboardEditor from "@/components/DashboardEditor.vue";
  import { useTransactions } from "@/composables/transactionsComposable";
  import { useTransactionsStore } from "@/stores/transactions";
  import { useDashboardConfig } from "@/composables/dashboardComposable";

  const transactions_store = useTransactionsStore();
  const editorOpen = ref(false);

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
