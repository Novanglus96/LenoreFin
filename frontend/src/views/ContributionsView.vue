<template>
  <v-container>
    <v-row class="pa-1 ga-1" no-gutters>
      <v-col class="rounded text-center"> <ContributionsWidget /></v-col
    ></v-row>
    <v-row class="pa-1 ga-1" no-gutters
      ><v-col class="rounded text-center"><ContributionRulesWidget /></v-col
    ></v-row>
  </v-container>
</template>
<script setup>
import ContributionsWidget from "@/components/ContributionsWidget.vue";
import ContributionRulesWidget from "@/components/ContributionRulesWidget.vue";
</script>
