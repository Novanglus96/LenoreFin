<template>
  <div>
    <v-list density="compact" nav>
      <v-list-item
        prepend-icon="mdi-plus-circle"
        base-color="secondary"
        :to="add_account_link"
      >
        <v-list-item-title
          ><span :class="isMobile ? 'text-h6' : ''"
            >Add Account</span
          ></v-list-item-title
        >
      </v-list-item>
    </v-list>
    <v-list density="compact" nav>
      <v-list-group
        collapse-icon="mdi-chevron-up"
        expand-icon="mdi-chevron-down"
        v-model="groupActive"
        value="checking"
      >
        <template v-slot:activator="{ props }">
          <v-list-item color="secondary" base-color="secondary" v-bind="props">
            <template v-slot:prepend
              ><v-icon
                icon="mdi-checkbook"
                :size="!isMobile ? 'medium' : 'x-large'"
              ></v-icon
            ></template>
            <v-list-item-title>
              <span :class="isMobile ? 'text-h6' : ''"
                >CHECKING</span
              ></v-list-item-title
            ><v-list-item-subtitle
              ><span :class="isMobile ? 'text-subtitle-1' : ''"
                >{{ checking_accounts ? checking_accounts.length : 0 }}
                {{
                  checking_accounts && checking_accounts.length == 1
                    ? "account"
                    : "accounts"
                }}</span
              ></v-list-item-subtitle
            ></v-list-item
          ></template
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
          <v-list-item-title
            ><span
              :class="isMobile ? 'text-subtitle-1 font-weight-bold' : ''"
              >{{ account.account_name }}</span
            ></v-list-item-title
          >
          <v-list-item-subtitle
            ><span
              :class="
                account.balance >= 0
                  ? 'text-green font-weight-bold'
                  : 'text-red font-weight-bold'
              "
            >
              <NumberFlow
                :value="account.balance"
                :format="{ style: 'currency', currency: 'USD' }" /></span
          ></v-list-item-subtitle>
        </v-list-item>
      </v-list-group>
      <v-divider></v-divider>
      <v-list-group
        collapse-icon="mdi-chevron-up"
        expand-icon="mdi-chevron-down"
        v-model="groupActive"
        value="savings"
      >
        <template v-slot:activator="{ props }">
          <v-list-item color="secondary" base-color="secondary" v-bind="props">
            <template v-slot:prepend
              ><v-icon
                icon="mdi-piggy-bank"
                :size="!isMobile ? 'medium' : 'x-large'"
              ></v-icon
            ></template>
            <v-list-item-title
              ><span :class="isMobile ? 'text-h6' : ''"
                >SAVINGS</span
              ></v-list-item-title
            ><v-list-item-subtitle
              ><span :class="isMobile ? 'text-subtitle-1' : ''"
                >{{ savings_accounts ? savings_accounts.length : 0 }}
                {{
                  savings_accounts && savings_accounts.length == 1
                    ? "account"
                    : "accounts"
                }}</span
              ></v-list-item-subtitle
            ></v-list-item
          ></template
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
          <v-list-item-title
            ><span
              :class="isMobile ? 'text-subtitle-1 font-weight-bold' : ''"
              >{{ account.account_name }}</span
            ></v-list-item-title
          >
          <v-list-item-subtitle
            ><span
              :class="
                account.balance >= 0
                  ? 'text-green font-weight-bold'
                  : 'text-red font-weight-bold'
              "
              ><NumberFlow
                :value="account.balance"
                :format="{ style: 'currency', currency: 'USD' }" /></span
          ></v-list-item-subtitle>
        </v-list-item>
      </v-list-group>
      <v-divider></v-divider>
      <v-list-group
        collapse-icon="mdi-chevron-up"
        expand-icon="mdi-chevron-down"
        v-model="groupActive"
        value="cc"
      >
        <template v-slot:activator="{ props }">
          <v-list-item color="secondary" base-color="secondary" v-bind="props">
            <template v-slot:prepend
              ><v-icon
                icon="mdi-credit-card"
                :size="!isMobile ? 'medium' : 'x-large'"
              ></v-icon
            ></template>
            <v-list-item-title
              ><span :class="isMobile ? 'text-h6' : ''"
                >CREDIT CARD</span
              ></v-list-item-title
            ><v-list-item-subtitle
              ><span :class="isMobile ? 'text-subtitle-1' : ''"
                >{{ cc_accounts ? cc_accounts.length : 0 }}
                {{
                  cc_accounts && cc_accounts.length == 1
                    ? "account"
                    : "accounts"
                }}</span
              ></v-list-item-subtitle
            ></v-list-item
          ></template
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
          <v-list-item-title
            ><span
              :class="isMobile ? 'text-subtitle-1 font-weight-bold' : ''"
              >{{ account.account_name }}</span
            >
          </v-list-item-title>
          <v-list-item-subtitle
            ><span
              :class="
                account.balance >= 0
                  ? 'text-green font-weight-bold'
                  : 'text-red font-weight-bold'
              "
              ><NumberFlow
                :value="account.balance"
                :format="{ style: 'currency', currency: 'USD' }" /></span
          ></v-list-item-subtitle>
        </v-list-item>
      </v-list-group>
      <v-divider></v-divider>
      <v-list-group
        collapse-icon="mdi-chevron-up"
        expand-icon="mdi-chevron-down"
        v-model="groupActive"
        value="investment"
      >
        <template v-slot:activator="{ props }">
          <v-list-item color="secondary" base-color="secondary" v-bind="props">
            <template v-slot:prepend
              ><v-icon
                icon="mdi-finance"
                :size="!isMobile ? 'medium' : 'x-large'"
              ></v-icon
            ></template>
            <v-list-item-title
              ><span :class="isMobile ? 'text-h6' : ''"
                >INVESTMENT</span
              ></v-list-item-title
            ><v-list-item-subtitle
              ><span :class="isMobile ? 'text-subtitle-1' : ''"
                >{{ investment_accounts ? investment_accounts.length : 0 }}
                {{
                  investment_accounts && investment_accounts.length == 1
                    ? "account"
                    : "accounts"
                }}</span
              ></v-list-item-subtitle
            ></v-list-item
          ></template
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
          <v-list-item-title
            ><span
              :class="isMobile ? 'text-subtitle-1 font-weight-bold' : ''"
              >{{ account.account_name }}</span
            >
          </v-list-item-title>
          <v-list-item-subtitle
            ><span
              :class="
                account.balance >= 0
                  ? 'text-green font-weight-bold'
                  : 'text-red font-weight-bold'
              "
              ><NumberFlow
                :value="account.balance"
                :format="{ style: 'currency', currency: 'USD' }" /></span
          ></v-list-item-subtitle>
        </v-list-item>
      </v-list-group>
      <v-divider></v-divider>
      <v-list-group
        collapse-icon="mdi-chevron-up"
        expand-icon="mdi-chevron-down"
        v-model="groupActive"
        value="loan"
      >
        <template v-slot:activator="{ props }">
          <v-list-item color="secondary" base-color="secondary" v-bind="props">
            <template v-slot:prepend
              ><v-icon
                icon="mdi-car-back"
                :size="!isMobile ? 'medium' : 'x-large'"
              ></v-icon
            ></template>
            <v-list-item-title
              ><span :class="isMobile ? 'text-h6' : ''"
                >LOAN</span
              ></v-list-item-title
            ><v-list-item-subtitle
              ><span :class="isMobile ? 'text-subtitle-1' : ''"
                >{{ loan_accounts ? loan_accounts.length : 0 }}
                {{
                  loan_accounts && loan_accounts.length == 1
                    ? "account"
                    : "accounts"
                }}</span
              ></v-list-item-subtitle
            ></v-list-item
          ></template
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
          <v-list-item-title
            ><span
              :class="isMobile ? 'text-subtitle-1 font-weight-bold' : ''"
              >{{ account.account_name }}</span
            >
          </v-list-item-title>
          <v-list-item-subtitle
            ><span
              :class="
                account.balance >= 0
                  ? 'text-green font-weight-bold'
                  : 'text-red font-weight-bold'
              "
              ><NumberFlow
                :value="account.balance"
                :format="{ style: 'currency', currency: 'USD' }" /></span
          ></v-list-item-subtitle>
        </v-list-item>
      </v-list-group>
      <v-divider></v-divider>
      <v-list-group
        collapse-icon="mdi-chevron-up"
        expand-icon="mdi-chevron-down"
        v-model="groupActive"
        value="inactive"
      >
        <template v-slot:activator="{ props }">
          <v-list-item color="secondary" base-color="secondary" v-bind="props">
            <template v-slot:prepend
              ><v-icon
                icon="mdi-bank-off"
                :size="!isMobile ? 'medium' : 'x-large'"
              ></v-icon
            ></template>
            <v-list-item-title
              ><span :class="isMobile ? 'text-h6' : ''"
                >INACTIVE</span
              ></v-list-item-title
            ><v-list-item-subtitle
              ><span :class="isMobile ? 'text-subtitle-1' : ''"
                >{{ inactive_accounts ? inactive_accounts.length : 0 }}
                {{
                  inactive_accounts && inactive_accounts.length == 1
                    ? "account"
                    : "accounts"
                }}</span
              ></v-list-item-subtitle
            ></v-list-item
          ></template
        >
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
            ><span class="font-italic"
              ><span
                :class="isMobile ? 'text-subtitle-1 font-weight-bold' : ''"
                >{{ account.account_name }}</span
              ></span
            >
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
import NumberFlow from "@number-flow/vue";
import { useDisplay } from "vuetify";

const { smAndDown } = useDisplay();
const isMobile = smAndDown;

const transactions_store = useTransactionsStore();
const router = useRouter();
const groupActive = ref(null);

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
</script>
