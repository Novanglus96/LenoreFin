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
      <v-tooltip location="bottom" text="Show trend line">
        <template v-slot:activator="{ props: tipProps }">
          <v-btn
            icon="mdi-trending-up"
            flat
            size="small"
            :color="showTrendLine ? 'primary' : undefined"
            variant="plain"
            :disabled="isActive"
            v-bind="tipProps"
            @click="toggleTrendLine"
          ></v-btn>
        </template>
      </v-tooltip>
      <v-tooltip location="bottom" text="Show 1st of month balance">
        <template v-slot:activator="{ props: tipProps }">
          <v-btn
            icon="mdi-currency-usd"
            flat
            size="small"
            :color="showMonthFlag ? 'primary' : undefined"
            variant="plain"
            :disabled="isActive"
            v-bind="tipProps"
            @click="toggleMonthFlag"
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

  const lsTrendKey = `forecast_trend_line_${props.account?.[0] ?? "default"}`;
  const showTrendLine = ref(localStorage.getItem(lsTrendKey) === "true");
  function toggleTrendLine() {
    showTrendLine.value = !showTrendLine.value;
    localStorage.setItem(lsTrendKey, showTrendLine.value);
  }

  const lsMonthFlagKey = `forecast_month_flag_${props.account?.[0] ?? "default"}`;
  const showMonthFlag = ref(localStorage.getItem(lsMonthFlagKey) === "true");
  function toggleMonthFlag() {
    showMonthFlag.value = !showMonthFlag.value;
    localStorage.setItem(lsMonthFlagKey, showMonthFlag.value);
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
  const TREND_COLOR = "#888888";

  function computeTrendLine(labels, data) {
    const points = data
      .map((v, i) => ({ i, v: v != null ? Number(v) : null }))
      .filter(p => p.v != null);
    if (points.length < 2) return null;
    const n = points.length;
    const sumX = points.reduce((a, p) => a + p.i, 0);
    const sumY = points.reduce((a, p) => a + p.v, 0);
    const sumXY = points.reduce((a, p) => a + p.i * p.v, 0);
    const sumX2 = points.reduce((a, p) => a + p.i * p.i, 0);
    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;
    return labels.map((label, i) => ({
      x: label,
      y: Math.round(slope * i + intercept),
    }));
  }

  const chartSeries = computed(() => {
    const raw = account_forecast.value;
    if (!raw?.datasets?.length) return [];

    const baseSeries = raw.datasets.map(ds => ({
      name: ds.label ?? "Balance",
      data: (raw.labels ?? []).map((label, i) => ({
        x: label,
        y: ds.data?.[i] != null ? Number(ds.data[i]) : null,
      })),
    }));

    if (!showTrendLine.value) return baseSeries;

    const trendData = computeTrendLine(
      raw.labels ?? [],
      raw.datasets[0].data ?? [],
    );
    if (!trendData) return baseSeries;

    return [...baseSeries, { name: "Trend", data: trendData }];
  });

  const hasTrend = computed(
    () =>
      showTrendLine.value &&
      chartSeries.value.length > (account_forecast.value?.datasets?.length ?? 0),
  );

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
      if (d > today && data[i] != null) {
        const val = Number(data[i]);
        if (val < minVal) {
          minVal = val;
          minLabel = label;
        }
      }
    });

    return minLabel !== null ? { x: minLabel, y: minVal } : null;
  });

  const monthFirstPoint = computed(() => {
    if (!showMonthFlag.value) return null;
    const raw = account_forecast.value;
    if (!raw?.labels?.length || !raw?.datasets?.[0]?.data?.length) return null;

    const today = new Date();
    const firstOfNextMonth = new Date(today.getFullYear(), today.getMonth() + 1, 1);

    const labels = raw.labels;
    const data = raw.datasets[0].data;

    for (let i = 0; i < labels.length; i++) {
      const d = new Date(labels[i].replace(/'/g, "20"));
      if (
        d.getFullYear() === firstOfNextMonth.getFullYear() &&
        d.getMonth() === firstOfNextMonth.getMonth() &&
        d.getDate() === 1 &&
        data[i] != null
      ) {
        return { x: labels[i], y: Number(data[i]) };
      }
    }
    return null;
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
    const forecastColor = hasNegative && !hasPositive ? NEGATIVE_COLOR : POSITIVE_COLOR;

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

    const trend = hasTrend.value;
    const datasetCount = raw?.datasets?.length ?? 1;

    return {
      chart: {
        type: "area",
        toolbar: { show: false },
        zoom: { enabled: false },
        animations: { enabled: false },
      },
      colors: [
        ...Array(datasetCount).fill(forecastColor),
        ...(trend ? [TREND_COLOR] : []),
      ],
      dataLabels: { enabled: false },
      stroke: {
        curve: trend
          ? [...Array(datasetCount).fill("smooth"), "straight"]
          : "smooth",
        width: trend
          ? [...Array(datasetCount).fill(2), 1.5]
          : 2,
        dashArray: trend
          ? [...Array(datasetCount).fill(0), 5]
          : 0,
      },
      fill: {
        type: trend
          ? [...Array(datasetCount).fill("gradient"), "solid"]
          : "gradient",
        gradient: {
          type: "vertical",
          colorStops: raw.datasets.map(() => colorStops),
        },
        opacity: trend
          ? [...Array(datasetCount).fill(1), 0]
          : 1,
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
        points: [
          ...(minPostTodayPoint.value ? [{
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
          }] : []),
          ...(monthFirstPoint.value ? [{
            x: monthFirstPoint.value.x,
            y: monthFirstPoint.value.y,
            marker: {
              size: 6,
              fillColor: "#06966a",
              strokeColor: "#fff",
              strokeWidth: 2,
            },
            label: {
              text: new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(monthFirstPoint.value.y),
              borderColor: "#06966a",
              offsetY: -12,
              style: {
                color: "#fff",
                background: "#06966a",
                fontSize: "10px",
                padding: { top: 3, bottom: 3, left: 5, right: 5 },
              },
            },
          }] : []),
        ],
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
        min: min,
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
          if (trend && seriesIndex === w.config.series.length - 1) {
            const val = series[seriesIndex]?.[dataPointIndex];
            const xLabel = w.config.series[seriesIndex]?.data?.[dataPointIndex]?.x ?? "";
            const formatted = val != null
              ? new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(val)
              : "N/A";
            return `<div style="padding:8px 10px;font-family:inherit;">
              <div style="color:#888;font-size:11px;margin-bottom:4px;">${xLabel}</div>
              <div style="display:flex;align-items:center;gap:6px;">
                <span style="display:inline-block;width:9px;height:9px;border-radius:50%;background:${TREND_COLOR};flex-shrink:0;"></span>
                <span style="color:#888;font-size:11px;">Trend</span>
                <span style="font-weight:600;color:${TREND_COLOR};font-size:12px;">${formatted}</span>
              </div>
            </div>`;
          }
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
