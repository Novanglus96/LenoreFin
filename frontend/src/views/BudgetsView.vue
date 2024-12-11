<template>
  <v-container>
    <v-row class="pa-1 ga-1" no-gutters>
      <v-col class="rounded text-center"
        ><BudgetsWidget
          :widget="false"
          @budget-selected="budgetSelected" /></v-col
    ></v-row>
    <v-row class="pa-1 ga-1" no-gutters>
      <v-col class="rounded text-center"
        ><BudgetForm
          :budget="localBudget ? localBudget.budget : null"
          :edit="true"
          :key="localBudget ? localBudget.budget.id : -1"
          v-if="!isMobile" />
        <BudgetFormMobile
          :budget="localBudget ? localBudget.budget : null"
          :edit="true"
          :key="localBudget ? localBudget.budget.id : -1"
          v-if="isMobile" /></v-col
    ></v-row>
    <v-row class="pa-1 ga-1" no-gutters>
      <v-col class="rounded"
        ><BudgetTransactions
          :transactions="localBudget ? localBudget.transactions : null"
          :key="localBudget ? localBudget.budget.id : -1"
          v-if="!isMobile" />
        <BudgetTransactionsMobile
          :transactions="localBudget ? localBudget.transactions : null"
          :key="localBudget ? localBudget.budget.id : -1"
          v-if="isMobile" /></v-col
    ></v-row>
  </v-container>
</template>
<script setup>
import { ref } from "vue";
import BudgetsWidget from "@/components/BudgetsWidget.vue";
import BudgetForm from "@/components/BudgetForm.vue";
import BudgetFormMobile from "@/components/BudgetFormMobile.vue";
import BudgetTransactions from "@/components/BudgetTransactions.vue";
import BudgetTransactionsMobile from "@/components/BudgetTransactionsMobile.vue";
import { useDisplay } from "vuetify";

const { smAndDown } = useDisplay();
const isMobile = smAndDown;

const localBudget = ref(null);

const budgetSelected = budget => {
  localBudget.value = budget;
};
</script>
