<template>
  <div>
    <v-row class="pa-1 ga-1" no-gutters>
      <v-col class="rounded">
        <SavingsPlanWidget />
      </v-col>
    </v-row>
    <v-row class="pa-1 ga-1" no-gutters>
      <v-col class="rounded">
        <BucketsWidget />
      </v-col>
    </v-row>
    <v-row class="pa-1 ga-1" no-gutters>
      <v-col class="rounded">
        <WindfallRulesWidget />
      </v-col>
    </v-row>
  </div>
</template>
<script setup>
  import SavingsPlanWidget from "@/components/SavingsPlanWidget.vue";
  import BucketsWidget from "@/components/BucketsWidget.vue";
  import WindfallRulesWidget from "@/components/WindfallRulesWidget.vue";
</script>
