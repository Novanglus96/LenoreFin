<template>
  <div>
    <v-row class="pa-1 ga-1 rounded" no-gutters>
      <v-col class="rounded">
        <v-card v-if="!isLoading">
          <v-card-title>{{ props.graphName }}</v-card-title>
          <v-card-text>
            <v-container>
              <v-row dense>
                <v-col>
                  <Bar :data="props.data.data" :options="options" />
                </v-col>
              </v-row>
              <v-row>
                <v-col class="text-right"
                  ><span class="text-subtitle-2"
                    >{{ props.data.year1 }} Avg: ${{
                      props.data.year1_avg
                    }}</span
                  ></v-col
                >
                <v-col class="text-left"
                  ><span class="text-subtitle-2"
                    >{{ props.data.year2 }} Avg: ${{
                      props.data.year2_avg
                    }}</span
                  ></v-col
                >
              </v-row>
            </v-container>
          </v-card-text>
        </v-card>
        <v-skeleton-loader type="card" v-else></v-skeleton-loader>
      </v-col>
    </v-row>
  </div>
</template>
<script setup>
import { ref, computed, defineProps } from "vue";
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from "chart.js";
import { Bar } from "vue-chartjs";
import annotationPlugin from "chartjs-plugin-annotation";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  annotationPlugin,
);
const props = defineProps({
  data: Object,
  graphName: {
    type: String,
  },
});
const this_year_avg = computed(() => (props.data ? props.data.year1_avg : 0));
const show_year1 = computed(() => (props.data.year1_avg !== 0 ? true : false));
const last_year_avg = computed(() => (props.data ? props.data.year2_avg : 0));
const show_year2 = computed(() => (props.data.year2_avg !== 0 ? true : false));
const options = ref({
  responsive: true,
  maintainAspectRatio: true,
  aspectRatio: "7",
  plugins: {
    annotation: {
      annotations: [
        {
          type: "line",
          display: show_year1,
          mode: "horizontal",
          scaleID: "y",
          value: this_year_avg,
          borderColor: "#034a45",
          borderWidth: 1,
          borderDash: [3, 3],
        },
        {
          type: "line",
          display: show_year2,
          mode: "horizontal",
          scaleID: "y",
          value: last_year_avg,
          borderColor: "#88b3b0",
          borderWidth: 1,
          borderDash: [3, 3],
        },
      ],
    },
    tooltip: {
      enabled: true,
      callbacks: {
        label: function (context) {
          let label = context.dataset.label || "";
          if (label) {
            label += ": ";
          }
          if (context.parsed.y !== null) {
            label += new Intl.NumberFormat("en-US", {
              style: "currency",
              currency: "USD",
            }).format(context.parsed.y);
          }
          return label;
        },
      },
    },
  },
  scales: {
    y: {
      ticks: {
        // Include a dollar sign in the ticks
        callback: function (value) {
          return "$" + value;
        },
      },
    },
  },
});
</script>
