<template>
  <div>
    <v-row class="pa-1 ga-1" no-gutters>
      <v-col class="rounded text-center">
        <PieGraphWidget :key="1" :widget="1" />
      </v-col>
      <v-col class="rounded text-center">
        <PieGraphWidget :key="2" :widget="2" />
      </v-col>
      <v-col class="rounded text-center">
        <PieGraphWidget :key="3" :widget="3" />
      </v-col>
    </v-row>
    <v-row class="pa-1 ga-1 rounded" no-gutters>
      <v-col class="rounded"> <RemindersWidget /> </v-col>
    </v-row>
    <v-row class="pa-1 ga-1 rounded" no-gutters>
      <v-col class="rounded"> <UpcomingTransactionsWidget /> </v-col>
    </v-row>
  </div>
</template>
<script setup>
import PieGraphWidget from "@/components/PieGraphWidget.vue";
import RemindersWidget from "@/components/RemindersWidget.vue";
import UpcomingTransactionsWidget from "@/components/UpcomingTransactionsWidget.vue";
</script>
<style scoped>
.custom-height {
  height: 340px;
  /* Adjust the height as needed */
  overflow-y: hidden;
  /* Add this if you want a vertical scrollbar for overflow */
}
</style>
