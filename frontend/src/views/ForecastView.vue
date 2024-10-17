<template>
  <div>
    <v-row class="pa-1 ga-1" no-gutters>
      <v-col class="rounded">
        <ForecastHeaderWidget @update-account="updateAccount" />
      </v-col>
    </v-row>
    <v-row class="pa-1 ga-1" no-gutters>
      <v-col class="rounded text-center">
        <AccountForecastWidget
          :key="account_id + ':' + timeframe"
          :account="[account_id]"
          :start_integer="0"
          :end_integer="timeframe"
          v-if="account_id"
          @change-time="clickChangeTime"
        />
      </v-col>
    </v-row>
    <v-row class="pa-1 ga-1 rounded" no-gutters>
      <v-col class="rounded">
        <AccountTransactionsWidget
          :key="account_id + ':' + timeframe"
          :account="account_id"
          :maxdays="timeframe"
          :forecast="true"
          v-if="account_id"
        />
      </v-col>
    </v-row>
  </div>
</template>
<script setup>
import AccountForecastWidget from "@/components/AccountForecastWidget.vue";
import AccountTransactionsWidget from "@/components/AccountTransactionsWidget.vue";
import ForecastHeaderWidget from "@/components/ForecastHeaderWidget.vue";
import { ref } from "vue";
import { useTransactionsStore } from "@/stores/transactions";

const transactions_store = useTransactionsStore();
const account_id = ref(null);
const timeframe = ref(90);

const updateAccount = account => {
  account_id.value = account;
  transactions_store.pageinfo.account_id = account;
  transactions_store.pageinfo.forecast = true;
  transactions_store.pageinfo.page = 1;
  transactions_store.pageinfo.maxdays = 90;
  transactions_store.pageinfo.view_type = 1;
};

const clickChangeTime = value => {
  timeframe.value = value;
};
</script>
