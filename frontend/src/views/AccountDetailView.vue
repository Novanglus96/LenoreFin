<template>
  <div>
    <v-row class="pa-1 ga-1" no-gutters>
      <v-col class="rounded">
        <AccountHeaderWidget
          :key="account_id"
          :account="[parseFloat(account_id)]"
          v-if="!isMobile"
        />
        <AccountHeaderWidgetMobile
          :key="account_id"
          :account="[parseFloat(account_id)]"
          v-else
        />
      </v-col>
    </v-row>
    <v-row class="pa-1 ga-1" no-gutters>
      <v-col class="rounded text-center">
        <AccountForecastWidget
          :key="account_id + ':' + timeframe"
          :start_integer="14"
          :end_integer="timeframe"
          :account="[account_id]"
          @change-time="clickChangeTime"
          v-if="!isMobile"
        />
        <AccountForecastWidgetMobile
          :key="account_id + ':' + timeframe"
          :start_integer="14"
          :end_integer="timeframe"
          :account="[account_id]"
          @change-time="clickChangeTime"
          v-else
        />
      </v-col>
    </v-row>
    <v-row class="pa-1 ga-1 rounded" no-gutters>
      <v-col class="rounded">
        <AccountTransactionsWidget
          :key="account_id"
          :account="parseFloat(account_id)"
          v-if="!isMobile"
        />
        <AccountTransactionsWidgetMobile
          :key="account_id"
          :account="parseFloat(account_id)"
          v-else
        />
      </v-col>
    </v-row>
  </div>
</template>
<script setup>
import AccountForecastWidget from "@/components/AccountForecastWidget.vue";
import AccountForecastWidgetMobile from "@/components/AccountForecastWidgetMobile.vue";
import AccountTransactionsWidget from "@/components/AccountTransactionsWidget.vue";
import AccountTransactionsWidgetMobile from "@/components/AccountTransactionsWidgetMobile.vue";
import AccountHeaderWidget from "@/components/AccountHeaderWidget.vue";
import AccountHeaderWidgetMobile from "@/components/AccountHeaderWidgetMobile.vue";
import { useRoute } from "vue-router";
import { ref, watch } from "vue";
import { useTransactionsStore } from "@/stores/transactions";
import { useDisplay } from "vuetify";

const { smAndDown } = useDisplay();
const isMobile = smAndDown;

const transactions_store = useTransactionsStore();
const route = useRoute();
const account_id = ref(route.params.accountID);
const timeframe = ref(90);

watch(
  () => route.params.accountID,
  newAccountID => {
    // Update the account_id ref with the new value
    account_id.value = newAccountID;
    transactions_store.pageinfo.account_id = newAccountID;
    transactions_store.pageinfo.forecast = false;
  },
);

const clickChangeTime = value => {
  timeframe.value = value;
};
</script>
