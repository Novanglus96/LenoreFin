<template>
  <v-container>
    <v-row class="pa-1 ga-1" no-gutters>
      <v-col class="rounded">
        <ContributionsWidget v-if="!isMobile" /><ContributionsWidgetMobile
          v-if="isMobile" /></v-col
    ></v-row>
    <v-row class="pa-1 ga-1" no-gutters
      ><v-col class="rounded"
        ><ContributionRulesWidget
          v-if="!isMobile" /><ContributionRulesWidgetMobile
          v-if="isMobile" /></v-col
    ></v-row>
  </v-container>
</template>
<script setup>
import ContributionsWidget from "@/components/ContributionsWidget.vue";
import ContributionsWidgetMobile from "@/components/ContributionsWidgetMobile.vue";
import ContributionRulesWidget from "@/components/ContributionRulesWidget.vue";
import ContributionRulesWidgetMobile from "@/components/ContributionRulesWidgetMobile.vue";
import { useDisplay } from "vuetify";

const { smAndDown } = useDisplay();
const isMobile = smAndDown;
</script>
