<template>
  <div>
    <v-row class="pa-1 ga-1" no-gutters>
      <v-col class="rounded">
        <ContributionsWidget />
      </v-col>
    </v-row>
    <v-row class="pa-1 ga-1" no-gutters>
      <v-col class="rounded">
        <ContributionRulesWidget />
      </v-col>
    </v-row>
  </div>
</template>
<script setup>
  import ContributionsWidget from "@/components/ContributionsWidget.vue";
  import ContributionRulesWidget from "@/components/ContributionRulesWidget.vue";
</script>
