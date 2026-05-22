<template>
  <div>
    <v-row class="pa-1 ga-1 rounded" no-gutters>
      <v-col class="rounded">
        <v-card
          variant="outlined"
          :elevation="4"
          class="bg-surface"
          v-if="!props.isLoading"
        >
          <v-card-text>
            <v-container>
              <v-row dense>
                <v-col>
                  <ApexChart
                    type="bar"
                    :height="smAndDown ? 300 : 180"
                    :options="chartOptions"
                    :series="chartSeries"
                    :aria-label="props.graphName"
                  />
                </v-col>
              </v-row>
              <v-row>
                <v-col class="text-right">
                  <span class="text-subtitle-2 font-weight-bold" style="color: #034a45;">
                    {{ props.data.year1 }} Avg:
                    {{ formatCurrency(props.data.year1_avg) }}
                  </span>
                </v-col>
                <v-col class="text-left">
                  <span class="text-subtitle-2 font-weight-bold" style="color: #88b3b0;">
                    {{ props.data.year2 }} Avg:
                    {{ formatCurrency(props.data.year2_avg) }}
                  </span>
                </v-col>
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
  import { computed, defineProps } from "vue";
  import ApexChart from "vue3-apexcharts";
  import { useDisplay } from "vuetify";

  const { smAndDown } = useDisplay();

  const props = defineProps({
    data: Object,
    graphName: {
      type: String,
    },
    isLoading: Boolean,
  });

  const chartSeries = computed(() => {
    const raw = props.data?.data;
    if (!raw?.datasets?.length) return [];
    return raw.datasets.map(ds => ({
      name: ds.label ?? "",
      data: (ds.data ?? []).map(Number),
    }));
  });

  const chartOptions = computed(() => {
    const raw = props.data?.data;
    const YEAR_COLORS = ["#034a45", "#88b3b0"];
    const seriesColors = (raw?.datasets ?? []).map((_, i) => YEAR_COLORS[i % YEAR_COLORS.length]);
    const year1Avg = props.data?.year1_avg ?? 0;
    const year2Avg = props.data?.year2_avg ?? 0;

    const avgAnnotations = [];
    if (year1Avg !== 0) avgAnnotations.push({ y: year1Avg, borderColor: "#034a45", borderWidth: 1, strokeDashArray: 3 });
    if (year2Avg !== 0) avgAnnotations.push({ y: year2Avg, borderColor: "#88b3b0", borderWidth: 1, strokeDashArray: 3 });

    return {
      chart: {
        type: "bar",
        toolbar: { show: false },
        animations: { enabled: false },
      },
      colors: seriesColors,
      plotOptions: {
        bar: { columnWidth: "60%", borderRadius: 2 },
      },
      dataLabels: { enabled: false },
      xaxis: {
        categories: raw?.labels ?? [],
        labels: { style: { fontSize: "10px" } },
        tooltip: { enabled: false },
      },
      yaxis: {
        labels: {
          formatter: val => val != null ? "$" + Math.round(val).toLocaleString("en-US") : "",
        },
      },
      annotations: { yaxis: avgAnnotations },
      tooltip: {
        shared: false,
        custom: function ({ series, seriesIndex, dataPointIndex, w }) {
          const val = series[seriesIndex]?.[dataPointIndex];
          const color = seriesColors[seriesIndex] ?? "#034a45";
          const seriesName = w.config.series[seriesIndex]?.name ?? "";
          const xLabel = w.globals.labels?.[dataPointIndex] ?? "";
          const formatted =
            val != null
              ? new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(val)
              : "N/A";
          return `<div style="padding:8px 10px;font-family:inherit;">
            <div style="color:#888;font-size:11px;margin-bottom:4px;">${xLabel}</div>
            <div style="display:flex;align-items:center;gap:6px;">
              <span style="display:inline-block;width:9px;height:9px;border-radius:50%;background:${color};flex-shrink:0;"></span>
              <span style="font-size:11px;color:#aaa;">${seriesName}</span>
              <span style="font-weight:600;color:${color};font-size:12px;">${formatted}</span>
            </div>
          </div>`;
        },
      },
      legend: { show: true },
    };
  });

  const formatCurrency = value => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };
</script>
