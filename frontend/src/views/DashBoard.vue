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
      <v-col class="rounded"> <BudgetsWidget :widget="true" /> </v-col>
    </v-row>
    <v-row class="pa-1 ga-1 rounded" no-gutters>
      <v-col class="rounded">
        <RemindersWidget v-if="!isMobile" />
        <RemindersWidgetMobile v-if="isMobile"
      /></v-col>
    </v-row>
    <v-row class="pa-1 ga-1 rounded" no-gutters>
      <v-col class="rounded">
        <UpcomingTransactionsWidget
          key="upcoming"
          view_type="Upcoming Transactions"
          v-if="!isMobile"
        />
        <UpcomingTransactionsWidgetMobile
          key="upcoming"
          view_type="Upcoming Transactions"
          v-if="isMobile"
        />
      </v-col>
    </v-row>
  </div>
</template>
<script setup>
import PieGraphWidget from "@/components/PieGraphWidget.vue";
import RemindersWidget from "@/components/RemindersWidget.vue";
import RemindersWidgetMobile from "@/components/RemindersWidgetMobile.vue";
import UpcomingTransactionsWidget from "@/components/UpcomingTransactionsWidget.vue";
import UpcomingTransactionsWidgetMobile from "@/components/UpcomingTransactionsWidgetMobile.vue";
import BudgetsWidget from "@/components/BudgetsWidget.vue";
import { useDisplay } from "vuetify";

const { smAndDown } = useDisplay();
const isMobile = smAndDown;
</script>
<style scoped>
.custom-height {
  height: 340px;
  /* Adjust the height as needed */
  overflow-y: hidden;
  /* Add this if you want a vertical scrollbar for overflow */
}
</style>
