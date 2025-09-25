<template>
  <v-row class="pa-1 ga-1" no-gutters>
    <v-col class="rounded text-center">
      <BudgetsWidget :widget="false" @budget-selected="budgetSelected" />
    </v-col>
  </v-row>
  <v-row class="pa-1 ga-1" no-gutters>
    <v-col class="rounded text-center">
      <BudgetForm
        :budget="localBudget ? localBudget.budget : null"
        :edit="true"
        :key="localBudget ? localBudget.budget.id : -1"
        v-if="!isMobile"
      />
      <BudgetFormMobile
        :budget="localBudget ? localBudget.budget : null"
        :edit="true"
        :key="localBudget ? localBudget.budget.id : -1"
        v-if="isMobile"
      />
    </v-col>
  </v-row>
  <v-row class="pa-1 ga-1" no-gutters>
    <v-col class="rounded">
      <TransactionTableWidget
        :key="localBudget ? localBudget.budget.id : -1"
        variant="budget"
        :data="localBudget ? localBudget : null"
        :loading="false"
        :fetching="false"
      />
    </v-col>
  </v-row>
</template>
<script setup>
  import { ref } from "vue";
  import BudgetsWidget from "@/components/BudgetsWidget.vue";
  import BudgetForm from "@/components/BudgetForm.vue";
  import BudgetFormMobile from "@/components/BudgetFormMobile.vue";
  import { useDisplay } from "vuetify";
  import TransactionTableWidget from "@/components/TransactionTableWidget.vue";

  const { smAndDown } = useDisplay();
  const isMobile = smAndDown;

  const localBudget = ref(null);

  const budgetSelected = budget => {
    localBudget.value = budget;
  };
</script>
