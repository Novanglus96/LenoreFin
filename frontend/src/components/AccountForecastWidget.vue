<template>
  <v-card variant="outlined" :elevation="4" class="bg-surface">
    <v-card-title class="text-left">
      <span
        class="text-subtitle-2 text-primary"
        v-if="props.start_integer == 0"
      >
        Forecast ({{ timeFrame.title }})
      </span>
      <span class="text-subtitle-2 text-primary" v-else>
        Cash Flow (Last 14 Days + {{ timeFrame.title }})
      </span>
      <v-menu location="right">
        <template v-slot:activator="{ props }">
          <v-btn
            icon="mdi-cog"
            flat
            size="small"
            v-bind="props"
            :disabled="isActive"
            variant="plain"
          ></v-btn>
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
    </v-card-title>
    <v-card-text>
      <v-progress-circular
        color="primary"
        indeterminate
        :size="300"
        :width="12"
        v-if="isActive"
      >
        Loading...
      </v-progress-circular>
      <Line
        :data="safeChartData"
        :options="options"
        v-if="!isActive && safeChartData"
        ref="Forecast"
        aria-label="Account Forecast"
      >
        Unable to load forecast
      </Line>
    </v-card-text>
  </v-card>
</template>
<script setup>
  import { ref, defineProps, defineEmits, computed, markRaw } from "vue";
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
  import { useDisplay } from "vuetify";

  const { smAndDown } = useDisplay();

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
    chips,
  );
  const isActive = computed(
    () => !(isLoading.value === false && isFetching.value === false),
  );

  const POSITIVE_COLOR = '#4caf50';
  const NEGATIVE_COLOR = '#f44336';

  const safeChartData = computed(() => {
    const raw = account_forecast.value;
    if (!raw) return null;
    return markRaw({
      labels: Array.from(raw.labels ?? []),
      datasets: (raw.datasets ?? []).map(ds => markRaw({
        ...ds,
        data: Array.from(ds.data ?? []),
        segment: {
          borderColor: ctx => ctx.p0.parsed.y >= 0 ? POSITIVE_COLOR : NEGATIVE_COLOR,
          backgroundColor: ctx => ctx.p0.parsed.y >= 0 ? 'rgba(76,175,80,0.3)' : 'rgba(244,67,54,0.3)',
        },
        pointBackgroundColor: ctx => (ctx.parsed?.y ?? 0) < 0 ? NEGATIVE_COLOR : POSITIVE_COLOR,
        pointBorderColor: ctx => (ctx.parsed?.y ?? 0) < 0 ? NEGATIVE_COLOR : POSITIVE_COLOR,
      })),
    });
  });
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
    aspectRatio: smAndDown.value ? "1" : "5",
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
          labelColor: function (context) {
            const color = context.parsed.y >= 0 ? '#4caf50' : '#f44336';
            return { borderColor: color, backgroundColor: color };
          },
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
