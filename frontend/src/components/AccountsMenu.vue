<template>
  <div>
    <v-list density="compact" nav>
      <v-list-item
        prepend-icon="mdi-plus-circle"
        base-color="secondary"
        :to="add_account_link"
      >
        <v-list-item-title>Add Account</v-list-item-title>
      </v-list-item>
    </v-list>
    <v-list density="compact" nav>
      <v-list-subheader color="secondary"
        ><v-icon icon="mdi-checkbook"></v-icon> CHECKING</v-list-subheader
      >
      <v-list-item
        title="No Accounts"
        v-if="checking_accounts && checking_accounts.length == 0"
      ></v-list-item>
      <v-list-item
        v-for="(account, i) in checking_accounts"
        :key="i"
        color="accent"
        @click="setAccount(account.id, False)"
        v-else
      >
        <v-list-item-title>{{ account.account_name }} </v-list-item-title>
        <v-list-item-subtitle
          ><span
            :class="
              account.balance >= 0
                ? 'text-green font-weight-bold'
                : 'text-red font-weight-bold'
            "
            >{{ formatCurrency(account.balance) }}</span
          ></v-list-item-subtitle
        >
      </v-list-item>
    </v-list>
    <v-divider></v-divider>
    <v-list density="compact" nav>
      <v-list-subheader color="secondary"
        ><v-icon icon="mdi-piggy-bank"></v-icon> SAVINGS</v-list-subheader
      >
      <v-list-item
        title="No Accounts"
        v-if="savings_accounts && savings_accounts.length == 0"
      ></v-list-item>
      <v-list-item
        v-for="(account, i) in savings_accounts"
        :key="i"
        color="accent"
        @click="setAccount(account.id, False)"
        v-else
      >
        <v-list-item-title>{{ account.account_name }} </v-list-item-title>
        <v-list-item-subtitle
          ><span
            :class="
              account.balance >= 0
                ? 'text-green font-weight-bold'
                : 'text-red font-weight-bold'
            "
            >{{ formatCurrency(account.balance) }}</span
          ></v-list-item-subtitle
        >
      </v-list-item>
    </v-list>
    <v-divider></v-divider>
    <v-list density="compact" nav>
      <v-list-subheader color="secondary"
        ><v-icon icon="mdi-credit-card"></v-icon> CREDIT CARD</v-list-subheader
      >
      <v-list-item
        title="No Accounts"
        v-if="cc_accounts && cc_accounts.length == 0"
      ></v-list-item>
      <v-list-item
        v-for="(account, i) in cc_accounts"
        :key="i"
        color="accent"
        @click="setAccount(account.id, False)"
        v-else
      >
        <v-list-item-title>{{ account.account_name }} </v-list-item-title>
        <v-list-item-subtitle
          ><span
            :class="
              account.balance >= 0
                ? 'text-green font-weight-bold'
                : 'text-red font-weight-bold'
            "
            >{{ formatCurrency(account.balance) }}</span
          ></v-list-item-subtitle
        >
      </v-list-item>
    </v-list>
    <v-divider></v-divider>
    <v-list density="compact" nav>
      <v-list-subheader color="secondary"
        ><v-icon icon="mdi-finance"></v-icon> INVESTMENT</v-list-subheader
      >
      <v-list-item
        title="No Accounts"
        v-if="investment_accounts && investment_accounts.length == 0"
      ></v-list-item>
      <v-list-item
        v-for="(account, i) in investment_accounts"
        :key="i"
        color="accent"
        @click="setAccount(account.id, False)"
        v-else
      >
        <v-list-item-title>{{ account.account_name }} </v-list-item-title>
        <v-list-item-subtitle
          ><span
            :class="
              account.balance >= 0
                ? 'text-green font-weight-bold'
                : 'text-red font-weight-bold'
            "
            >{{ formatCurrency(account.balance) }}</span
          ></v-list-item-subtitle
        >
      </v-list-item>
    </v-list>
    <v-divider></v-divider>
    <v-list density="compact" nav>
      <v-list-subheader color="secondary"
        ><v-icon icon="mdi-car-back"></v-icon> LOAN</v-list-subheader
      >
      <v-list-item
        title="No Accounts"
        v-if="loan_accounts && loan_accounts.length == 0"
      ></v-list-item>
      <v-list-item
        v-for="(account, i) in loan_accounts"
        :key="i"
        color="accent"
        @click="setAccount(account.id, False)"
        v-else
      >
        <v-list-item-title>{{ account.account_name }} </v-list-item-title>
        <v-list-item-subtitle
          ><span
            :class="
              account.balance >= 0
                ? 'text-green font-weight-bold'
                : 'text-red font-weight-bold'
            "
            >{{ formatCurrency(account.balance) }}</span
          ></v-list-item-subtitle
        >
      </v-list-item>
    </v-list>
    <v-divider></v-divider>
    <v-list density="compact" nav>
      <v-list-group
        collapse-icon="mdi-chevron-down"
        expand-icon="mdi-chevron-up"
        v-model="groupActive"
      >
        <template v-slot:activator="{ props, isActive }">
          <v-list-subheader color="secondary" v-bind="props"
            ><v-icon icon="mdi-bank-off"></v-icon> INACTIVE<v-icon
              :icon="isActive ? 'mdi-chevron-up' : 'mdi-chevron-down'"
            ></v-icon></v-list-subheader
        ></template>
        <v-list-item
          title="No Accounts"
          v-if="inactive_accounts && inactive_accounts.length == 0"
        ></v-list-item>
        <v-list-item
          v-for="(account, i) in inactive_accounts"
          :key="i"
          color="accent"
          @click="setAccount(account.id, False)"
          v-else
        >
          <v-list-item-title
            ><span class="font-italic">{{ account.account_name }}</span>
          </v-list-item-title>
        </v-list-item>
      </v-list-group>
    </v-list>
  </div>
</template>
<script setup>
import { useAccounts } from "@/composables/accountsComposable";
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useTransactionsStore } from "@/stores/transactions";

const transactions_store = useTransactionsStore();
const router = useRouter();
const groupActive = ref(false);

const setAccount = (account, forecast) => {
  transactions_store.pageinfo.account_id = account;
  transactions_store.pageinfo.forecast = forecast;
  transactions_store.pageinfo.page = 1;
  transactions_store.pageinfo.maxdays = 14;
  transactions_store.pageinfo.view_type = 1;
  router.push("/accounts/" + account);
};

const {
  checking_accounts,
  cc_accounts,
  savings_accounts,
  investment_accounts,
  loan_accounts,
  inactive_accounts,
} = useAccounts();
const add_account_link = ref("/accounts/add");
const formatCurrency = value => {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
};
</script>
