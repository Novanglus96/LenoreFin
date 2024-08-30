<template>
  <v-container>
    <v-row class="pa-1 ga-1" no-gutters>
      <v-col class="rounded text-center" cols="4">
        <CalculatorRulesWidget />
      </v-col>
      <v-col class="rounded text-center">
        <v-card variant="outlined" :elevation="4" class="bg-white">
          <v-card-title></v-card-title>
          <v-card-text
            ><v-autocomplete
              label="Timeframe*"
              :items="timeframe"
              variant="outlined"
              item-title="name"
              item-value="days"
              v-model="selectedTimeframe"
              chips
            ></v-autocomplete>
            <CalculatorTransfersWidget />
            <CalculatorTransactionsWidget />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
<script setup>
import CalculatorRulesWidget from "../components/CalculatorRulesWidget.vue";
import CalculatorTransfersWidget from "../components/CalculatorTransfersWidget.vue";
import CalculatorTransactionsWidget from "../components/CalculatorTransactionsWidget.vue";

import { ref } from "vue";

const timeframe = ref([
  {
    name: "Today",
    days: 0,
  },
  {
    name: "+1 Day",
    days: 1,
  },
  {
    name: "+2 Days",
    days: 2,
  },
  {
    name: "+3 Days",
    days: 3,
  },
]);

const selectedTimeframe = ref(0);
</script>
