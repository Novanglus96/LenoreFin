<template>
  <div>
    <v-row class="pa-1 ga-1 rounded" no-gutters>
      <v-col class="rounded">
        <v-card
          variant="outlined"
          :elevation="4"
          class="bg-surface"
          v-if="!isLoading && tag_transactions"
        >
          <v-card-title>
            <span class="text-subtitle-2 text-primary">Tag Totals</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row dense>
                <v-col>
                  <ApexChart
                    type="bar"
                    :height="250"
                    :options="chartOptions"
                    :series="chartSeries"
                    aria-label="Tag Totals"
                  />
                </v-col>
              </v-row>
              <v-row>
                <v-col class="text-right">
                  <span class="text-subtitle-2" style="color: #034a45;">
                    {{ tag_transactions.year1 }} Avg:
                    {{ formatCurrency(tag_transactions.year1_avg) }}
                  </span>
                </v-col>
                <v-col class="text-left">
                  <span class="text-subtitle-2" style="color: #88b3b0;">
                    {{ tag_transactions.year2 }} Avg:
                    {{ formatCurrency(tag_transactions.year2_avg) }}
                  </span>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
        </v-card>
        <v-skeleton-loader type="card" v-else></v-skeleton-loader>
      </v-col>
    </v-row>
    <v-row class="pa-1 ga-1 rounded" no-gutters>
      <v-col class="rounded">
        <TransactionTableWidget
          :key="props.tagID"
          variant="tag"
          :data="tag_transactions"
          :loading="isLoading"
          :fetching="isFetching"
        />
      </v-col>
    </v-row>
  </div>
</template>
<script setup>
  import { defineProps, computed } from "vue";
  import ApexChart from "vue3-apexcharts";
  import { useGraphTransactions } from "@/composables/tagsComposable";
  import TransactionTableWidget from "./TransactionTableWidget.vue";

  const props = defineProps({
    tagID: {
      type: Number,
    },
  });

  const { tag_transactions, isLoading, isFetching } = useGraphTransactions(
    props.tagID,
  );

  const chartSeries = computed(() => {
    const raw = tag_transactions.value?.data;
    if (!raw?.datasets?.length) return [];
    return raw.datasets.map(ds => ({
      name: ds.label ?? "",
      data: (ds.data ?? []).map(Number),
    }));
  });

  const chartOptions = computed(() => {
    const raw = tag_transactions.value?.data;
    const YEAR_COLORS = ["#034a45", "#88b3b0"];
    const seriesColors = (raw?.datasets ?? []).map((_, i) => YEAR_COLORS[i % YEAR_COLORS.length]);
    const year1Avg = tag_transactions.value?.year1_avg ?? 0;
    const year2Avg = tag_transactions.value?.year2_avg ?? 0;

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
