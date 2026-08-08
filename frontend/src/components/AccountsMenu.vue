<template>
  <div class="accounts-menu">
    <v-list
      density="compact"
      nav
      :bg-color="smAndDown ? 'background' : 'surface'"
    >
      <v-list-item
        prepend-icon="mdi-plus-circle"
        base-color="primary"
        :to="add_account_link"
        v-if="authStore.isFullAccess"
        :disabled="!isOnline"
      >
        <v-list-item-title>
          <span :class="isMobile ? 'text-h6' : ''">Add Account</span>
        </v-list-item-title>
      </v-list-item>
    </v-list>
    <v-list
      density="compact"
      nav
      :bg-color="smAndDown ? 'background' : 'surface'"
      v-model:opened="openedGroups"
    >
      <!-- Favorites section -->
      <v-list-group
        collapse-icon="mdi-chevron-up"
        expand-icon="mdi-chevron-down"

        value="favorites"
        v-if="favoriteAccounts.length > 0"
      >
        <template v-slot:activator="{ props }">
          <v-list-item color="amber" base-color="amber" v-bind="props">
            <template v-slot:prepend>
              <v-icon
                icon="mdi-star"
                :size="!isMobile ? 'default' : 'x-large'"
              ></v-icon>
            </template>
            <v-list-item-title>
              <span :class="isMobile ? 'text-h6' : ''">FAVORITES</span>
            </v-list-item-title>
            <v-list-item-subtitle>
              <span :class="isMobile ? 'text-subtitle-1' : ''">
                {{ favoriteAccounts.length }}
                {{ favoriteAccounts.length == 1 ? "account" : "accounts" }}
              </span>
            </v-list-item-subtitle>
          </v-list-item>
        </template>
        <v-list-item
          v-for="(account, i) in favoriteAccounts"
          :key="i"
          color="accent"
          @click="setAccount(account.id, False)"
        >
          <template v-slot:prepend>
            <BankLogo :logo-url="account.bank?.logo_url" :size="20" class="mr-1" />
          </template>
          <v-list-item-title>
            <span :class="isMobile ? 'text-subtitle-1 font-weight-bold' : ''">{{ account.account_name }}</span>
            <v-tooltip v-if="account.is_parent_account" text="Combined account" location="top">
              <template v-slot:activator="{ props }">
                <v-icon icon="mdi-layers" color="secondary" size="x-small" class="ml-1" v-bind="props" />
              </template>
            </v-tooltip>
          </v-list-item-title>
          <v-list-item-subtitle>
            <span
              :class="
                account.balance >= 0
                  ? 'text-success font-weight-bold'
                  : 'text-error font-weight-bold'
              "
            >
              <NumberFlow
                :value="account.balance"
                :format="{ style: 'currency', currency: 'USD' }"
              />
            </span>
          </v-list-item-subtitle>
        </v-list-item>
      </v-list-group>
      <v-divider v-if="favoriteAccounts.length > 0"></v-divider>
      <v-list-group
        collapse-icon="mdi-chevron-up"
        expand-icon="mdi-chevron-down"

        value="checking"
      >
        <template v-slot:activator="{ props }">
          <v-list-item color="primary" base-color="primary" v-bind="props">
            <template v-slot:prepend>
              <v-icon
                icon="mdi-checkbook"
                :size="!isMobile ? 'default' : 'x-large'"
              ></v-icon>
            </template>
            <v-list-item-title>
              <span :class="isMobile ? 'text-h6' : ''">CHECKING</span>
            </v-list-item-title>
            <v-list-item-subtitle>
              <span :class="isMobile ? 'text-subtitle-1' : ''">
                {{ checking_accounts ? checking_accounts.length : 0 }}
                {{
                  checking_accounts && checking_accounts.length == 1
                    ? "account"
                    : "accounts"
                }}
              </span>
            </v-list-item-subtitle>
          </v-list-item>
        </template>
        <v-list-item
          title="No Accounts"
          v-if="checking_accounts && checking_accounts.length == 0"
        ></v-list-item>
        <v-list-item
          v-for="(account, i) in sortForMenu(checking_accounts)"
          :key="i"
          color="accent"
          @click="setAccount(account.id, False)"
          v-else
          :style="account.parent_account_id ? { '--child-indent': '44px' } : {}"
        >
          <template v-slot:prepend>
            <BankLogo :logo-url="account.bank?.logo_url" :size="20" class="mr-1" />
          </template>
          <v-list-item-title>
            <span :class="isMobile ? 'text-subtitle-1 font-weight-bold' : ''">{{ account.account_name }}</span>
            <v-tooltip v-if="account.is_parent_account" text="Combined account" location="top">
              <template v-slot:activator="{ props }">
                <v-icon icon="mdi-layers" color="secondary" size="x-small" class="ml-1" v-bind="props" />
              </template>
            </v-tooltip>
          </v-list-item-title>
          <v-list-item-subtitle>
            <span
              :class="
                account.balance >= 0
                  ? 'text-success font-weight-bold'
                  : 'text-error font-weight-bold'
              "
            >
              <NumberFlow
                :value="account.balance"
                :format="{ style: 'currency', currency: 'USD' }"
              />
            </span>
          </v-list-item-subtitle>
        </v-list-item>
      </v-list-group>
      <v-divider></v-divider>
      <v-list-group
        collapse-icon="mdi-chevron-up"
        expand-icon="mdi-chevron-down"

        value="savings"
      >
        <template v-slot:activator="{ props }">
          <v-list-item color="primary" base-color="primary" v-bind="props">
            <template v-slot:prepend>
              <v-icon
                icon="mdi-piggy-bank"
                :size="!isMobile ? 'default' : 'x-large'"
              ></v-icon>
            </template>
            <v-list-item-title>
              <span :class="isMobile ? 'text-h6' : ''">SAVINGS</span>
            </v-list-item-title>
            <v-list-item-subtitle>
              <span :class="isMobile ? 'text-subtitle-1' : ''">
                {{ savings_accounts ? savings_accounts.length : 0 }}
                {{
                  savings_accounts && savings_accounts.length == 1
                    ? "account"
                    : "accounts"
                }}
              </span>
            </v-list-item-subtitle>
          </v-list-item>
        </template>
        <v-list-item
          title="No Accounts"
          v-if="savings_accounts && savings_accounts.length == 0"
        ></v-list-item>
        <v-list-item
          v-for="(account, i) in sortForMenu(savings_accounts)"
          :key="i"
          color="accent"
          @click="setAccount(account.id, False)"
          v-else
          :style="account.parent_account_id ? { '--child-indent': '44px' } : {}"
        >
          <template v-slot:prepend>
            <BankLogo :logo-url="account.bank?.logo_url" :size="20" class="mr-1" />
          </template>
          <v-list-item-title>
            <span :class="isMobile ? 'text-subtitle-1 font-weight-bold' : ''">{{ account.account_name }}</span>
            <v-tooltip v-if="account.is_parent_account" text="Combined account" location="top">
              <template v-slot:activator="{ props }">
                <v-icon icon="mdi-layers" color="secondary" size="x-small" class="ml-1" v-bind="props" />
              </template>
            </v-tooltip>
          </v-list-item-title>
          <v-list-item-subtitle>
            <span
              :class="
                account.balance >= 0
                  ? 'text-success font-weight-bold'
                  : 'text-error font-weight-bold'
              "
            >
              <NumberFlow
                :value="account.balance"
                :format="{ style: 'currency', currency: 'USD' }"
              />
            </span>
          </v-list-item-subtitle>
        </v-list-item>
      </v-list-group>
      <v-divider></v-divider>
      <v-list-group
        collapse-icon="mdi-chevron-up"
        expand-icon="mdi-chevron-down"

        value="cc"
      >
        <template v-slot:activator="{ props }">
          <v-list-item color="primary" base-color="primary" v-bind="props">
            <template v-slot:prepend>
              <v-icon
                icon="mdi-credit-card"
                :size="!isMobile ? 'default' : 'x-large'"
              ></v-icon>
            </template>
            <v-list-item-title>
              <span :class="isMobile ? 'text-h6' : ''">CREDIT CARD</span>
            </v-list-item-title>
            <v-list-item-subtitle>
              <span :class="isMobile ? 'text-subtitle-1' : ''">
                {{ cc_accounts ? cc_accounts.length : 0 }}
                {{
                  cc_accounts && cc_accounts.length == 1
                    ? "account"
                    : "accounts"
                }}
              </span>
            </v-list-item-subtitle>
          </v-list-item>
        </template>
        <v-list-item
          title="No Accounts"
          v-if="cc_accounts && cc_accounts.length == 0"
        ></v-list-item>
        <v-list-item
          v-for="(account, i) in sortForMenu(cc_accounts)"
          :key="i"
          color="accent"
          @click="setAccount(account.id, False)"
          v-else
          :style="account.parent_account_id ? { '--child-indent': '44px' } : {}"
        >
          <template v-slot:prepend>
            <BankLogo :logo-url="account.bank?.logo_url" :size="20" class="mr-1" />
          </template>
          <v-list-item-title>
            <span :class="isMobile ? 'text-subtitle-1 font-weight-bold' : ''">{{ account.account_name }}</span>
            <v-tooltip v-if="account.is_parent_account" text="Combined account" location="top">
              <template v-slot:activator="{ props }">
                <v-icon icon="mdi-layers" color="secondary" size="x-small" class="ml-1" v-bind="props" />
              </template>
            </v-tooltip>
          </v-list-item-title>
          <v-list-item-subtitle>
            <span
              :class="
                account.balance >= 0
                  ? 'text-success font-weight-bold'
                  : 'text-error font-weight-bold'
              "
            >
              <NumberFlow
                :value="account.balance"
                :format="{ style: 'currency', currency: 'USD' }"
              />
            </span>
          </v-list-item-subtitle>
        </v-list-item>
      </v-list-group>
      <v-divider></v-divider>
      <v-list-group
        collapse-icon="mdi-chevron-up"
        expand-icon="mdi-chevron-down"

        value="investment"
      >
        <template v-slot:activator="{ props }">
          <v-list-item color="primary" base-color="primary" v-bind="props">
            <template v-slot:prepend>
              <v-icon
                icon="mdi-finance"
                :size="!isMobile ? 'default' : 'x-large'"
              ></v-icon>
            </template>
            <v-list-item-title>
              <span :class="isMobile ? 'text-h6' : ''">INVESTMENT</span>
            </v-list-item-title>
            <v-list-item-subtitle>
              <span :class="isMobile ? 'text-subtitle-1' : ''">
                {{ investment_accounts ? investment_accounts.length : 0 }}
                {{
                  investment_accounts && investment_accounts.length == 1
                    ? "account"
                    : "accounts"
                }}
              </span>
            </v-list-item-subtitle>
          </v-list-item>
        </template>
        <v-list-item
          title="No Accounts"
          v-if="investment_accounts && investment_accounts.length == 0"
        ></v-list-item>
        <v-list-item
          v-for="(account, i) in sortForMenu(investment_accounts)"
          :key="i"
          color="accent"
          @click="setAccount(account.id, False)"
          v-else
          :style="account.parent_account_id ? { '--child-indent': '44px' } : {}"
        >
          <template v-slot:prepend>
            <BankLogo :logo-url="account.bank?.logo_url" :size="20" class="mr-1" />
          </template>
          <v-list-item-title>
            <span :class="isMobile ? 'text-subtitle-1 font-weight-bold' : ''">{{ account.account_name }}</span>
            <v-tooltip v-if="account.is_parent_account" text="Combined account" location="top">
              <template v-slot:activator="{ props }">
                <v-icon icon="mdi-layers" color="secondary" size="x-small" class="ml-1" v-bind="props" />
              </template>
            </v-tooltip>
          </v-list-item-title>
          <v-list-item-subtitle>
            <span
              :class="
                account.balance >= 0
                  ? 'text-success font-weight-bold'
                  : 'text-error font-weight-bold'
              "
            >
              <NumberFlow
                :value="account.balance"
                :format="{ style: 'currency', currency: 'USD' }"
              />
            </span>
          </v-list-item-subtitle>
        </v-list-item>
      </v-list-group>
      <v-divider></v-divider>
      <v-list-group
        collapse-icon="mdi-chevron-up"
        expand-icon="mdi-chevron-down"

        value="loan"
      >
        <template v-slot:activator="{ props }">
          <v-list-item color="primary" base-color="primary" v-bind="props">
            <template v-slot:prepend>
              <v-icon
                icon="mdi-car-back"
                :size="!isMobile ? 'default' : 'x-large'"
              ></v-icon>
            </template>
            <v-list-item-title>
              <span :class="isMobile ? 'text-h6' : ''">LOAN</span>
            </v-list-item-title>
            <v-list-item-subtitle>
              <span :class="isMobile ? 'text-subtitle-1' : ''">
                {{ loan_accounts ? loan_accounts.length : 0 }}
                {{
                  loan_accounts && loan_accounts.length == 1
                    ? "account"
                    : "accounts"
                }}
              </span>
            </v-list-item-subtitle>
          </v-list-item>
        </template>
        <v-list-item
          title="No Accounts"
          v-if="loan_accounts && loan_accounts.length == 0"
        ></v-list-item>
        <v-list-item
          v-for="(account, i) in sortForMenu(loan_accounts)"
          :key="i"
          color="accent"
          @click="setAccount(account.id, False)"
          v-else
          :style="account.parent_account_id ? { '--child-indent': '44px' } : {}"
        >
          <template v-slot:prepend>
            <BankLogo :logo-url="account.bank?.logo_url" :size="20" class="mr-1" />
          </template>
          <v-list-item-title>
            <span :class="isMobile ? 'text-subtitle-1 font-weight-bold' : ''">{{ account.account_name }}</span>
            <v-tooltip v-if="account.is_parent_account" text="Combined account" location="top">
              <template v-slot:activator="{ props }">
                <v-icon icon="mdi-layers" color="secondary" size="x-small" class="ml-1" v-bind="props" />
              </template>
            </v-tooltip>
          </v-list-item-title>
          <v-list-item-subtitle>
            <span
              :class="
                account.balance >= 0
                  ? 'text-success font-weight-bold'
                  : 'text-error font-weight-bold'
              "
            >
              <NumberFlow
                :value="account.balance"
                :format="{ style: 'currency', currency: 'USD' }"
              />
            </span>
          </v-list-item-subtitle>
        </v-list-item>
      </v-list-group>
      <v-divider></v-divider>
      <v-list-group
        collapse-icon="mdi-chevron-up"
        expand-icon="mdi-chevron-down"

        value="inactive"
      >
        <template v-slot:activator="{ props }">
          <v-list-item color="primary" base-color="primary" v-bind="props">
            <template v-slot:prepend>
              <v-icon
                icon="mdi-bank-off"
                :size="!isMobile ? 'default' : 'x-large'"
              ></v-icon>
            </template>
            <v-list-item-title>
              <span :class="isMobile ? 'text-h6' : ''">INACTIVE</span>
            </v-list-item-title>
            <v-list-item-subtitle>
              <span :class="isMobile ? 'text-subtitle-1' : ''">
                {{ inactive_accounts ? inactive_accounts.length : 0 }}
                {{
                  inactive_accounts && inactive_accounts.length == 1
                    ? "account"
                    : "accounts"
                }}
              </span>
            </v-list-item-subtitle>
          </v-list-item>
        </template>
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
          <template v-slot:prepend>
            <BankLogo :logo-url="account.bank?.logo_url" :size="20" class="mr-1" />
          </template>
          <v-list-item-title>
            <span class="font-italic">
              <span :class="isMobile ? 'text-subtitle-1 font-weight-bold' : ''">
                {{ account.account_name }}
              </span>
            </span>
          </v-list-item-title>
        </v-list-item>
      </v-list-group>
    </v-list>
  </div>
</template>
<script setup>
  import { useAccounts } from "@/composables/accountsComposable";
  import { ref, computed, watch } from "vue";
  import { useRouter } from "vue-router";
  import { useTransactionsStore } from "@/stores/transactions";
  import NumberFlow from "@number-flow/vue";
  import { useDisplay } from "vuetify";
  import { useAuthStore } from "@/stores/auth";
  import { useOnlineStatus } from "@/composables/useOnlineStatus";
  import BankLogo from "@/components/BankLogo.vue";
  const { isOnline } = useOnlineStatus();

  const { smAndDown } = useDisplay();
  const authStore = useAuthStore();
  const isMobile = smAndDown;

  const transactions_store = useTransactionsStore();
  const router = useRouter();
  const openedGroups = ref([]);

  const sortForMenu = accounts => {
    if (!accounts) return []
    const parents = accounts.filter(a => a.is_parent_account)
    const children = accounts.filter(a => a.parent_account_id !== null)
    const standalone = accounts.filter(a => !a.is_parent_account && a.parent_account_id === null)
    const result = []
    for (const parent of parents) {
      result.push(parent)
      result.push(...children.filter(c => c.parent_account_id === parent.id))
    }
    result.push(...standalone)
    return result
  }

  const setAccount = (account, forecast) => {
    transactions_store.resetFilters();
    transactions_store.pageinfo.account_id = account;
    transactions_store.pageinfo.forecast = forecast;
    transactions_store.pageinfo.maxdays = 14;
    transactions_store.pageinfo.view_type = 1;
    router.push("/accounts/" + account);
  };

  const {
    accounts,
    checking_accounts,
    cc_accounts,
    savings_accounts,
    investment_accounts,
    loan_accounts,
    inactive_accounts,
  } = useAccounts();

  const FAVORITE_TYPE_ORDER = { checking: 0, savings: 1, 'credit-card': 2, investment: 3, loan: 4 };

  const favoriteAccounts = computed(() =>
    [...(accounts.value ?? []).filter(a => a.is_favorite)].sort((a, b) => {
      const ta = FAVORITE_TYPE_ORDER[a.account_type?.slug] ?? 99;
      const tb = FAVORITE_TYPE_ORDER[b.account_type?.slug] ?? 99;
      return ta !== tb ? ta - tb : a.account_name.localeCompare(b.account_name);
    })
  );

  watch(favoriteAccounts, val => {
    if (val && val.length > 0 && !openedGroups.value.includes("favorites")) {
      openedGroups.value = ["favorites"];
    }
  }, { immediate: true });

  const add_account_link = ref("/accounts/add");
</script>

<style>
.accounts-menu .v-list-item__prepend .v-list-item__spacer {
  width: 8px !important;
}
.accounts-menu .v-list-group__items .v-list-item {
  padding-inline-start: calc(14px + var(--child-indent, 0px)) !important;
}
.accounts-menu .v-list-item-title {
  overflow: visible;
}
</style>
