<template>
  <v-dialog :fullscreen="smAndDown" :width="smAndDown ? '100%' : 500">
    <v-card>
      <v-card-title>Rewards</v-card-title>
      <v-card-subtitle>Last 5 months</v-card-subtitle>
      <v-card-text>
        <v-sheet border rounded class="bg-primary">
          <v-container>
            <v-row dense>
              <v-col>
                <span class="font-weight-bold">This Year</span>
                <v-sparkline
                  :model-value="props.currentAmounts"
                  color="rgba(222, 184, 135, .7)"
                  :height="smAndDown ? 225 : 100"
                  padding="25"
                  stroke-linecap="round"
                  fill
                  label-size="12"
                  auto-draw
                  auto-line-width
                  min="0"
                  :max="graphHeight"
                >
                  <template v-slot:label="item">${{ item.value }}</template>
                </v-sparkline>
              </v-col>
            </v-row>
            <v-row dense>
              <v-col>
                <span class="font-weight-bold">Last Year</span>
                <v-sparkline
                  :model-value="props.lastAmounts"
                  color="rgba(217, 93, 59, .7)"
                  :height="smAndDown ? 225 : 100"
                  padding="25"
                  stroke-linecap="round"
                  fill
                  label-size="12"
                  auto-draw
                  auto-line-width
                  min="0"
                  :max="graphHeight"
                >
                  <template v-slot:label="item">${{ item.value }}</template>
                </v-sparkline>
              </v-col>
            </v-row>
          </v-container>
        </v-sheet>
      </v-card-text>
      <v-card-actions>
        <v-btn @click="closeForm">Close</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
<script setup>
  import { defineProps, defineEmits, computed } from "vue";
  import { useDisplay } from "vuetify";

  const { smAndDown } = useDisplay();
  const props = defineProps({
    currentAmounts: {
      type: Array,
      default: () => [0, 91.12, 0, 95.67, 98.5],
    },
    lastAmounts: {
      type: Array,
      default: () => [0, 91.12, 0, 95.67, 98.5],
    },
  });
  const emit = defineEmits(["updateDialog"]);

  const closeForm = () => {
    emit("updateDialog", false);
  };

  const graphHeight = computed(() => {
    const currentMax = Math.ceil(Math.max(...props.currentAmounts));
    const lastMax = Math.ceil(Math.max(...props.lastAmounts));
    if (currentMax > lastMax) {
      return currentMax;
    } else {
      return lastMax;
    }
  });
</script>
