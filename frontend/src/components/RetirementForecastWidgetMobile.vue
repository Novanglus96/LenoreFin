<template>
  <v-card variant="outlined" :elevation="4" class="bg-white">
    <template v-slot:append>
      <v-btn
        icon="mdi-cog"
        flat
        size="xs"
        :disabled="isActive"
        @click="showOptions = true"
      ></v-btn>
      <v-dialog width="300" v-model="showOptions">
        <v-card>
          <form @submit.prevent="submit">
            <v-card-title
              ><span class="text-secondary text-h6"
                >Choose Retirement Accounts</span
              ></v-card-title
            >
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
                ><template v-slot:item="{ props, item }">
                  <v-list-item
                    v-bind="props"
                    :title="item.raw.account_name"
                    :subtitle="item.raw.bank.bank_name"
                  >
                    <template v-slot:prepend>
                      <v-icon :icon="item.raw.account_type.icon"></v-icon>
                    </template>
                  </v-list-item> </template></v-autocomplete
            ></v-card-text>
            <v-card-actions
              ><v-spacer></v-spacer
              ><v-btn color="secondary" type="submit"
                >Save Changes</v-btn
              ></v-card-actions
            >
          </form>
        </v-card>
      </v-dialog>
    </template>
    <template v-slot:title>
      <span class="text-subtitle-2 text-secondary">Retirement Forecast</span>
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
        :data="retirement_forecast"
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
import { ref, computed, watch } from "vue";
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
import { useRetirementForecast } from "@/composables/retirementComposable";
import { useField, useForm } from "vee-validate";
import { useOptions } from "@/composables/optionsComposable";
import { useAccounts } from "@/composables/accountsComposable";

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
  aspectRatio: "1",
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
      display: true,
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

const submit = handleSubmit(values => {
  let data = {
    retirement_accounts: JSON.stringify(values.retirement_accounts),
  };
  editOptions(data);
  showOptions.value = false;
});
</script>
