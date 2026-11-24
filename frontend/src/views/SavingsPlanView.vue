<template>
  <div>
    <v-row class="pa-1 ga-1" no-gutters>
      <v-col class="rounded">
        <SavingsPlanWidget @funding="id => (fundingAccountId = id)" />
      </v-col>
    </v-row>
    <v-row class="pa-1 ga-1" no-gutters>
      <v-col class="rounded">
        <WindfallWidget :funding-account-id="fundingAccountId" />
      </v-col>
    </v-row>
  </div>
</template>
<script setup>
  import { ref } from "vue";
  import SavingsPlanWidget from "@/components/SavingsPlanWidget.vue";
  import WindfallWidget from "@/components/WindfallWidget.vue";

  // A windfall lands in the funding account unless you say otherwise.
  const fundingAccountId = ref(null);
</script>
