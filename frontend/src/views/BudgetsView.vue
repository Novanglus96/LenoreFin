<template>
  <v-container>
    <v-row class="pa-1 ga-1" no-gutters>
      <v-col class="rounded text-center"
        ><BudgetsWidget :widget="false" /></v-col
    ></v-row>
  </v-container>
</template>
<script setup>
import BudgetsWidget from "@/components/BudgetsWidget.vue";
</script>
