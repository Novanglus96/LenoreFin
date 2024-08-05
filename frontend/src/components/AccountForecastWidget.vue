<template>
  <v-card variant="outlined" :elevation="4" class="bg-white">
    <template v-slot:append>
      <v-menu location="start">
        <template v-slot:activator="{ props }">
          <v-btn
            icon="mdi-cog"
            flat
            size="xs"
            v-bind="props"
            :disabled="isActive"
          >
          </v-btn>
        </template>
        <v-card width="300">
          <v-card-text>
            <h2 class="text-h6 mb-2">Time Frame</h2>

            <v-chip-group
              v-model="chips"
              column
              @update:model-value="clickChangeTime()"
            >
              <v-chip
                filter
                variant="outlined"
                v-for="item in mainstore.time_frames"
                :key="item.days"
                :value="item.days"
              >
                {{ item.title }}
              </v-chip>
            </v-chip-group>
          </v-card-text>
        </v-card>
      </v-menu>
    </template>
    <template v-slot:title>
      <span
        class="text-subtitle-2 text-secondary"
        v-if="props.start_integer == 0"
        >Forecast ({{ timeFrame.title }})</span
      >
      <span class="text-subtitle-2 text-secondary" v-else
        >Cash Flow (Last 14 Days + {{ timeFrame.title }})</span
      >
    </template>
    <template v-slot:text>
      <v-progress-circular
        color="secondary"
        indeterminate
        :size="300"
        :width="12"
        v-if="isActive"
        >Loading...</v-progress-circular
      >
      <Line
        :data="account_forecast"
        :options="options"
        v-if="!isActive"
        ref="Forecast"
        aria-label="Account Forecast"
        >Unable to load forecast</Line
      >
    </template>
  </v-card>
</template>
<script setup>
import { ref, defineProps, defineEmits, computed } from "vue";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import { Line } from "vue-chartjs";
import annotationPlugin from "chartjs-plugin-annotation";
import { useAccountForecasts } from "@/composables/forecastsComposable";
import { useMainStore } from "@/stores/main";

const mainstore = useMainStore();
const props = defineProps({
  account: Array,
  start_integer: { type: Number, default: 14 },
  end_integer: { type: Number, default: 90 },
});
const emit = defineEmits(["changeTime"]);
const chips = ref(props.end_integer);
const { isLoading, account_forecast, isFetching } = useAccountForecasts(
  props.account,
  props.start_integer,
  props.end_integer,
);
const isActive = computed(
  () => !(isLoading.value === false && isFetching.value === false),
);
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  annotationPlugin,
);

const options = ref({
  responsive: true,
  maintainAspectRatio: true,
  aspectRatio: "5",
  plugins: {
    annotation: {
      annotations: {
        line1: {
          type: "line",
          mode: "vertical",
          scaleID: "x",
          value: new Date().toLocaleDateString("en-US", {
            year: "2-digit",
            month: "short",
            day: "2-digit",
          }),
          borderColor: "grey",
          borderWidth: 1,
          borderDash: [2, 2],
          label: {
            content: "Today",
            display: true,
            position: "start",
            rotation: -90,
            padding: 3,
            opacity: 0.5,
          },
        },
        line2: {
          type: "line",
          mode: "horizontal",
          scaleID: "y",
          value: 0,
          borderColor: "black",
          borderWidth: 1,
        },
      },
    },
    tooltip: {
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
    legend: {
      display: false,
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

const clickChangeTime = () => {
  emit("changeTime", chips.value);
};

const timeFrame = mainstore.time_frames.find(
  frame => frame.days === props.end_integer,
);
</script>
