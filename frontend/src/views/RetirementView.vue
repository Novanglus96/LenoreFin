<template>
  <div>
    <v-row class="pa-1 ga-1" no-gutters>
      <v-col class="rounded text-center">
        <RetirementForecastWidget v-if="!isMobile" />
        <RetirementForecastWidgetMobile v-if="isMobile" />
      </v-col>
    </v-row>
  </div>
</template>
<script setup>
import RetirementForecastWidget from "@/components/RetirementForecastWidget.vue";
import RetirementForecastWidgetMobile from "@/components/RetirementForecastWidgetMobile.vue";
import { useDisplay } from "vuetify";

const { smAndDown } = useDisplay();
const isMobile = smAndDown;
</script>
