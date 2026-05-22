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
      <v-tooltip location="bottom" text="Highlight lowest balance after today">
        <template v-slot:activator="{ props: tipProps }">
          <v-btn
            :icon="showMinHighlight ? 'mdi-flag' : 'mdi-flag-outline'"
            flat
            size="small"
            :color="showMinHighlight ? 'error' : undefined"
            variant="plain"
            :disabled="isActive"
            v-bind="tipProps"
            @click="toggleMinHighlight"
          ></v-btn>
        </template>
      </v-tooltip>
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
      <ApexChart
        v-if="!isActive && chartSeries.length"
        type="area"
        :height="smAndDown ? 400 : 350"
        :options="chartOptions"
        :series="chartSeries"
        aria-label="Account Forecast"
      />
    </v-card-text>
  </v-card>
</template>
<script setup>
  import { ref, defineProps, defineEmits, computed } from "vue";
  import ApexChart from "vue3-apexcharts";
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

  const lsKey = `forecast_min_highlight_${props.account?.[0] ?? "default"}`;
  const showMinHighlight = ref(localStorage.getItem(lsKey) === "true");
  function toggleMinHighlight() {
    showMinHighlight.value = !showMinHighlight.value;
    localStorage.setItem(lsKey, showMinHighlight.value);
  }

  const { isLoading, account_forecast, isFetching } = useAccountForecasts(
    props.account,
    props.start_integer,
    chips,
  );

  const isActive = computed(
    () => !(isLoading.value === false && isFetching.value === false),
  );

  const POSITIVE_COLOR = "#4caf50";
  const NEGATIVE_COLOR = "#f44336";

  const chartSeries = computed(() => {
    const raw = account_forecast.value;
    if (!raw?.datasets?.length) return [];
    return raw.datasets.map(ds => ({
      name: ds.label ?? "Balance",
      data: (raw.labels ?? []).map((label, i) => ({
        x: label,
        y: ds.data?.[i] != null ? Number(ds.data[i]) : null,
      })),
    }));
  });

  const minPostTodayPoint = computed(() => {
    if (!showMinHighlight.value) return null;
    const raw = account_forecast.value;
    if (!raw?.labels?.length || !raw?.datasets?.[0]?.data?.length) return null;

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const labels = raw.labels;
    const data = raw.datasets[0].data;

    let minVal = Infinity;
    let minLabel = null;

    labels.forEach((label, i) => {
      // Labels are formatted as e.g. "May 21, '26" — parse by replacing abbreviated year
      const d = new Date(label.replace(/'/g, "20"));
      if (d >= today && data[i] != null) {
        const val = Number(data[i]);
        if (val < minVal) {
          minVal = val;
          minLabel = label;
        }
      }
    });

    return minLabel !== null ? { x: minLabel, y: minVal } : null;
  });

  const chartOptions = computed(() => {
    const raw = account_forecast.value;
    const allValues = (raw?.datasets ?? [])
      .flatMap(ds => ds.data ?? [])
      .map(Number)
      .filter(v => !isNaN(v));

    const max = Math.max(0, ...allValues);
    const min = Math.min(0, ...allValues);
    const range = max - min || 1;
    const zeroPercent = Math.min(99, Math.max(1, Math.round((max / range) * 100)));

    const hasPositive = max > 0;
    const hasNegative = min < 0;
    const colorStops = hasPositive && hasNegative
      ? [
          { offset: 0, color: POSITIVE_COLOR, opacity: 0.4 },
          { offset: zeroPercent, color: POSITIVE_COLOR, opacity: 0.05 },
          { offset: zeroPercent, color: NEGATIVE_COLOR, opacity: 0.05 },
          { offset: 100, color: NEGATIVE_COLOR, opacity: 0.4 },
        ]
      : hasNegative
        ? [{ offset: 0, color: NEGATIVE_COLOR, opacity: 0.4 }, { offset: 100, color: NEGATIVE_COLOR, opacity: 0.1 }]
        : [{ offset: 0, color: POSITIVE_COLOR, opacity: 0.4 }, { offset: 100, color: POSITIVE_COLOR, opacity: 0.1 }];

    const todayLabel = new Date().toLocaleDateString("en-US", {
      year: "2-digit",
      month: "short",
      day: "2-digit",
    });

    return {
      chart: {
        type: "area",
        toolbar: { show: false },
        zoom: { enabled: false },
        animations: { enabled: false },
      },
      colors: [hasNegative && !hasPositive ? NEGATIVE_COLOR : POSITIVE_COLOR],
      dataLabels: { enabled: false },
      stroke: { curve: "smooth", width: 2 },
      fill: {
        type: "gradient",
        gradient: {
          type: "vertical",
          colorStops: raw.datasets.map(() => colorStops),
        },
      },
      markers: { size: 0 },
      annotations: {
        xaxis: [{
          x: todayLabel,
          borderColor: "#999",
          borderWidth: 1,
          strokeDashArray: 4,
          label: {
            text: "Today",
            orientation: "vertical",
            position: "top",
            style: {
              fontSize: "11px",
              background: "transparent",
              color: "#999",
            },
          },
        }],
        yaxis: [{
          y: 0,
          borderColor: "#555",
          borderWidth: 1,
          strokeDashArray: 0,
        }],
        points: minPostTodayPoint.value ? [{
          x: minPostTodayPoint.value.x,
          y: minPostTodayPoint.value.y,
          marker: {
            size: 6,
            fillColor: "#f44336",
            strokeColor: "#fff",
            strokeWidth: 2,
          },
          label: {
            text: new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(minPostTodayPoint.value.y),
            borderColor: "#f44336",
            offsetY: -12,
            style: {
              color: "#fff",
              background: "#f44336",
              fontSize: "10px",
              padding: { top: 3, bottom: 3, left: 5, right: 5 },
            },
          },
        }] : [],
      },
      xaxis: {
        type: "category",
        tickAmount: smAndDown.value ? 4 : 8,
        labels: {
          rotate: -45,
          style: { fontSize: "10px" },
        },
        tooltip: { enabled: false },
      },
      yaxis: {
        labels: {
          formatter: val =>
            val != null
              ? "$" + Math.round(val).toLocaleString("en-US")
              : "",
        },
      },
      tooltip: {
        shared: false,
        custom: function ({ series, seriesIndex, dataPointIndex, w }) {
          const val = series[seriesIndex]?.[dataPointIndex];
          const color = (val ?? 0) >= 0 ? POSITIVE_COLOR : NEGATIVE_COLOR;
          const xLabel = w.config.series[seriesIndex]?.data?.[dataPointIndex]?.x ?? "";
          const formatted =
            val != null
              ? new Intl.NumberFormat("en-US", {
                  style: "currency",
                  currency: "USD",
                }).format(val)
              : "N/A";
          return `<div style="padding:8px 10px;font-family:inherit;">
            <div style="color:#888;font-size:11px;margin-bottom:4px;">${xLabel}</div>
            <div style="display:flex;align-items:center;gap:6px;">
              <span style="display:inline-block;width:9px;height:9px;border-radius:50%;background:${color};flex-shrink:0;"></span>

              <span style="font-weight:600;color:${color};font-size:12px;">${formatted}</span>
            </div>
          </div>`;
        },
      },
      legend: { show: false },
    };
  });

  const clickChangeTime = () => {
    emit("changeTime", chips.value);
  };

  const timeFrame = mainstore.time_frames.find(
    frame => frame.days === props.end_integer,
  );
</script>
