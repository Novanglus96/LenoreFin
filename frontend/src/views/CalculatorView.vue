<template>
  <div>
    <v-row class="ma-1 pa-0 ga-0">
      <!-- Left column, spans full height -->
      <v-col cols="12" class="d-flex flex-column ma-0 pa-0 ga-0" md="4">
        <div class="bg-primary flex-grow-1">
          <CalculatorRulesWidget
            :rules="calculation_rules"
            :isLoading="calculation_rules_isLoading"
            @rule-selected="ruleSelected"
          />
        </div>
      </v-col>

      <!-- Right side with stacked cols -->
      <v-col cols="12" md="8">
        <v-row>
          <v-col cols="12" class="ma-0 pa-0 ga-0">
            <v-card variant="outlined" :elevation="4" class="bg-surface">
              <v-card-title></v-card-title>
              <v-card-text>
                <v-autocomplete
                  label="Timeframe*"
                  :items="timeframe"
                  variant="outlined"
                  item-title="name"
                  item-value="days"
                  v-model="selectedTimeframe"
                  chips
                ></v-autocomplete>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" class="ma-0 pa-0 ga-0">
            <CalculatorTransfersWidget
              :transfers="calculator ? calculator.transfers : []"
              :isLoading="calculator_isLoading"
              :key="selected_rule"
              :ruleID="selected_rule"
              :timeframe="selectedTimeframe"
            />
          </v-col>
          <v-col cols="12" class="ma-0 pa-0 ga-0">
            <CalculatorTransactionsWidget
              :transactions="calculator ? calculator.transactions : []"
              :isLoading="calculator_isLoading"
              :key="selected_rule"
              :ruleID="selected_rule"
              :timeframe="selectedTimeframe"
            />
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </div>
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
