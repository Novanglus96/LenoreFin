<template>
  <v-card variant="outlined" :elevation="4" class="bg-white">
    <template v-slot:title>
      <span class="text-subtitle-2 text-secondary">Budgets</span>
    </template>
    <template v-slot:text>
      <v-slide-group
        v-model="model"
        class="pa-4"
        center-active
        show-arrows
        v-if="isLoading"
      >
        <v-slide-group-item
          ><v-skeleton-loader
            type="card"
            height="200"
            width="150"
          ></v-skeleton-loader
        ></v-slide-group-item>
      </v-slide-group>
      <v-slide-group
        v-model="model"
        class="pa-4"
        center-active
        show-arrows
        v-else
      >
        <v-slide-group-item v-for="budget in budgets" :key="budget.id">
          <v-card class="ma-4 text-center" height="200"
            ><v-card-text
              ><div class="text-subtitle-2 text-center font-weight-bold">
                {{ budget.budget.name }}
              </div>
              <v-progress-circular
                :model-value="budget.used_percentage"
                :size="100"
                :width="12"
                :color="graphColor(budget.used_percentage)"
                >{{
                  formatCurrency(
                    parseFloat(budget.budget.amount) +
                      parseFloat(budget.budget.roll_over_amt)-
                      parseFloat(Math.abs(budget.used_total)),
                  )
                }}</v-progress-circular
              >
              <div class="text-subtitle-2 text-center">
                Budget:
                {{
                  formatCurrency(
                    parseFloat(budget.budget.amount) +
                      parseFloat(budget.budget.roll_over_amt) ,
                  )
                }}
                <span
                  :class="
                    budget.budget.roll_over_amt < 0 ? 'text-red' : 'text-green'
                  "
                  v-if="budget.budget.roll_over"
                  >({{ formatCurrency(budget.budget.roll_over_amt) }})</span
                >
              </div>
              <div class="text-subtitle-2 text-center">
                Used: {{ formatCurrency(Math.abs(budget.used_total)) }}
              </div></v-card-text
            >
          </v-card>
        </v-slide-group-item>
      </v-slide-group>
    </template>
  </v-card>
</template>
<script setup>
import { useBudgets } from "@/composables/budgetsComposable";

const { budgets, isLoading } = useBudgets();

const formatCurrency = value => {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
};
const graphColor = value => {
  if (value <= 50) {
    return "success";
  }
  if (value > 50 && value <= 75) {
    return "warning";
  }
  if (value > 75) {
    return "error";
  }
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
