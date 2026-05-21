<template>
  <v-card variant="outlined" :elevation="4" class="bg-surface">
    <v-card-title class="text-left">
      <span class="text-subtitle-2 text-primary text-left">
        Retirement Forecast
      </span>
      <v-btn
        icon="mdi-cog"
        flat
        size="small"
        :disabled="isActive"
        @click="showOptions = true"
        variant="plain"
        v-if="authStore.isFullAccess"
      ></v-btn>
      <v-dialog width="300" v-model="showOptions">
        <v-card>
          <form @submit.prevent="submit">
            <v-card-title>
              <span class="text-primary text-h6">
                Choose Retirement Accounts
              </span>
            </v-card-title>
            <v-card-text>
              <v-autocomplete
                clearable
                chips
                multiple
                label="Account(s)"
                :items="accounts"
                variant="outlined"
                :loading="accounts_isLoading"
                item-title="account_name"
                item-value="id"
                v-model="retirement_accounts.value.value"
                density="compact"
                :error-messages="retirement_accounts.errorMessage.value"
              >
                <template v-slot:item="{ props, item }">
                  <v-list-item
                    v-bind="props"
                    :title="item.raw.account_name"
                    :subtitle="item.raw.bank.bank_name"
                  >
                    <template v-slot:prepend>
                      <v-icon :icon="item.raw.account_type.icon"></v-icon>
                    </template>
                  </v-list-item>
                </template>
              </v-autocomplete>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="primary" type="submit" :disabled="!isOnline">Save Changes</v-btn>
            </v-card-actions>
          </form>
        </v-card>
      </v-dialog>
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
        :height="350"
        :options="chartOptions"
        :series="chartSeries"
        aria-label="Retirement Forecast"
      />
    </v-card-text>

    <!-- Transaction List -->
    <v-card-text>
      <v-divider class="mb-3"></v-divider>
      <div class="text-subtitle-2 text-primary mb-2">Transactions</div>
      <v-data-table
        :headers="txnHeaders"
        :items="retirement_transactions ?? []"
        :loading="txnLoading"
        density="compact"
        striped="odd"
        :header-props="{ class: 'font-weight-bold bg-secondary' }"
        no-data-text="No transactions found"
        :items-per-page="TXN_PAGE_SIZE"
        v-model:page="txnPage"
      >
        <template v-slot:item.transaction_date="{ item }">
          {{ formatDate(item.transaction_date) }}
        </template>
        <template v-slot:item.total_amount="{ item }">
          {{ formatCurrency(item.total_amount) }}
        </template>
        <template v-slot:item.balance="{ item }">
          {{ item.balance != null ? formatCurrency(item.balance) : "—" }}
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>
<script setup>
  import { ref, computed, watch } from "vue";
  import ApexChart from "vue3-apexcharts";
  import { useAuthStore } from "@/stores/auth";
  import { useRetirementForecast, useRetirementTransactions } from "@/composables/retirementComposable";
  import { useField, useForm } from "vee-validate";
  import { useOptions } from "@/composables/optionsComposable";
  import { useAccounts } from "@/composables/accountsComposable";
  import { useOnlineStatus } from "@/composables/useOnlineStatus";

  const { isOnline } = useOnlineStatus();
  const authStore = useAuthStore();
  const { options: appOptions, editOptions } = useOptions();
  const { accounts, isLoading: accounts_isLoading } = useAccounts();
  const showOptions = ref(false);

  const { handleSubmit } = useForm({
    validationSchema: {
      retirement_accounts(value) {
        if (value && value.length > 0) return true;
        return "Must select at least 1 account.";
      },
    },
  });

  const retirement_accounts = useField("retirement_accounts");
  watch(
    appOptions,
    newOptions => {
      if (newOptions) {
        retirement_accounts.value.value = JSON.parse(newOptions.retirement_accounts);
      }
    },
    { immediate: true },
  );

  const { isLoading, retirement_forecast, isFetching } = useRetirementForecast();
  const { retirement_transactions, isLoading: txnLoading } = useRetirementTransactions();

  const isActive = computed(
    () => !(isLoading.value === false && isFetching.value === false),
  );

  const chartSeries = computed(() => {
    const raw = retirement_forecast.value;
    if (!raw?.datasets?.length) return [];
    return raw.datasets.map(ds => ({
      name: ds.label ?? "Balance",
      data: (raw.labels ?? []).map((label, i) => ({
        x: label,
        y: ds.data?.[i] != null ? Number(ds.data[i]) : null,
      })),
    }));
  });

  const chartOptions = computed(() => {
    const raw = retirement_forecast.value;
    const seriesColors = (raw?.datasets ?? []).map(ds => ds.borderColor ?? "#4caf50");

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
      colors: seriesColors,
      dataLabels: { enabled: false },
      stroke: { curve: "smooth", width: 2 },
      fill: {
        type: "gradient",
        gradient: {
          type: "vertical",
          colorStops: seriesColors.map(color => [
            { offset: 0, color, opacity: 0.4 },
            { offset: 100, color, opacity: 0.05 },
          ]),
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
      },
      xaxis: {
        type: "category",
        tickAmount: 8,
        labels: {
          rotate: -45,
          style: { fontSize: "10px" },
        },
        tooltip: { enabled: false },
      },
      yaxis: {
        labels: {
          formatter: val =>
            val != null ? "$" + Math.round(val).toLocaleString("en-US") : "",
        },
      },
      tooltip: {
        shared: false,
        custom: function ({ series, seriesIndex, dataPointIndex, w }) {
          const val = series[seriesIndex]?.[dataPointIndex];
          const color = seriesColors[seriesIndex] ?? "#4caf50";
          const xLabel = w.config.series[seriesIndex]?.data?.[dataPointIndex]?.x ?? "";
          const seriesName = w.config.series[seriesIndex]?.name ?? "";
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
              <span style="font-size:11px;color:#aaa;">${seriesName}</span>
              <span style="font-weight:600;color:${color};font-size:12px;">${formatted}</span>
            </div>
          </div>`;
        },
      },
      legend: { show: true },
    };
  });

  const TXN_PAGE_SIZE = 15;
  const txnPage = ref(1);

  watch(
    retirement_transactions,
    txns => {
      if (!txns || txns.length === 0) return;
      const today = new Date().toISOString().slice(0, 10);
      const idx = txns.findIndex(t => t.transaction_date >= today);
      const target = idx >= 0 ? idx : txns.length - 1;
      txnPage.value = Math.floor(target / TXN_PAGE_SIZE) + 1;
    },
    { immediate: true },
  );

  const txnHeaders = [
    { title: "Date", key: "transaction_date" },
    { title: "Account", key: "account_name" },
    { title: "Description", key: "description" },
    { title: "Type", key: "transaction_type_name" },
    { title: "Amount", key: "total_amount", align: "end" },
    { title: "Balance", key: "balance", align: "end" },
  ];

  function formatDate(d) {
    return new Date(d + "T00:00:00").toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  }

  function formatCurrency(val) {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(val);
  }

  const submit = handleSubmit(values => {
    editOptions({ retirement_accounts: JSON.stringify(values.retirement_accounts) });
    showOptions.value = false;
  });
</script>
