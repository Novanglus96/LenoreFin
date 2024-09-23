<template>
  <v-container>
    <v-row class="pa-1 ga-1" no-gutters>
      <v-col class="rounded text-center" cols="4">
        <CalculatorRulesWidget
          :rules="calculation_rules"
          :isLoading="calculation_rules_isLoading"
          @rule-selected="ruleSelected"
        />
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
            <CalculatorTransfersWidget
              :transfers="calculator ? calculator.transfers : []"
              :isLoading="calculator_isLoading"
              :key="selected_rule"
              :ruleID="selected_rule"
              :timeframe="selectedTimeframe"
            />
            <CalculatorTransactionsWidget
              :transactions="calculator ? calculator.transactions : []"
              :isLoading="calculator_isLoading"
              :key="selected_rule"
              :ruleID="selected_rule"
              :timeframe="selectedTimeframe"
            />
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
import { useCalculationRule } from "@/composables/calculatorComposable";

const selected_rule = ref(null);
const selectedTimeframe = ref(0);

const { calculation_rules, isLoading: calculation_rules_isLoading } =
  useCalculationRule();
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

const ruleSelected = rule_id => {
  selected_rule.value = rule_id;
};
</script>
