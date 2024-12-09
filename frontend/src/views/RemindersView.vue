<template>
  <div>
    <v-row class="pa-1 ga-1" no-gutters>
      <v-col class="rounded">
        <ReminderHeaderWidget />
      </v-col>
    </v-row>
    <v-row class="pa-1 ga-1 rounded" no-gutters>
      <v-col class="rounded">
        <RemindersWidget :allowEdit="true" v-if="!isMobile"/>
        <RemindersWidgetMobile :allowEdit="true" v-else/>
      </v-col>
    </v-row>
  </div>
</template>
<script setup>
import RemindersWidget from "@/components/RemindersWidget.vue";
import ReminderHeaderWidget from "@/components/ReminderHeaderWidget.vue";
import RemindersWidgetMobile from "@/components/RemindersWidgetMobile.vue";
import { useDisplay } from "vuetify";

const { smAndDown } = useDisplay();
const isMobile = smAndDown;
</script>
