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
              <v-btn color="primary" type="submit">Save Changes</v-btn>
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
      <Line
        :data="retirement_forecast"
        :options="chartOptions"
        v-if="!isActive"
        ref="Forecast"
        aria-label="Account Forecast"
      >
        Unable to load forecast
      </Line>
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
  import { useAuthStore } from "@/stores/auth";
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
  import { useRetirementForecast, useRetirementTransactions } from "@/composables/retirementComposable";
  import { useField, useForm } from "vee-validate";
  import { useOptions } from "@/composables/optionsComposable";
  import { useAccounts } from "@/composables/accountsComposable";

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
        retirement_accounts.value.value = JSON.parse(
          newOptions.retirement_accounts,
        );
      }
    },
    { immediate: true },
  );

  const { isLoading, retirement_forecast, isFetching } = useRetirementForecast();
  const { retirement_transactions, isLoading: txnLoading } = useRetirementTransactions();

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

  const chartOptions = ref({
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
            if (label) label += ": ";
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
        display: true,
      },
    },
    scales: {
      y: {
        ticks: {
          callback: function (value) {
            return "$" + value;
          },
        },
      },
    },
  });

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
    let data = {
      retirement_accounts: JSON.stringify(values.retirement_accounts),
    };
    editOptions(data);
    showOptions.value = false;
  });
</script>
