<template>
  <v-row class="pa-1 ga-1 rounded" no-gutters>
    <v-col class="rounded">
      <v-card variant="outlined" :elevation="4" class="bg-surface">
        <v-card-title class="text-subtitle-2 text-primary pa-3 pb-1">
          <v-icon icon="mdi-star" color="amber" size="small" class="mr-1" />
          Favorite Accounts
        </v-card-title>

        <!-- Loading skeletons -->
        <v-card-text v-if="isLoading" class="pa-2">
          <v-skeleton-loader
            v-for="n in 3"
            :key="n"
            type="list-item-two-line"
            class="mb-1"
          />
        </v-card-text>

        <!-- No favorites -->
        <v-card-text
          v-else-if="!favoriteBalances || favoriteBalances.length === 0"
          class="text-center text-medium-emphasis pa-6"
        >
          <v-icon icon="mdi-star-outline" size="x-large" class="mb-2" />
          <div class="text-body-2">No favorite accounts yet.</div>
          <div class="text-caption">Star an account from its detail view.</div>
        </v-card-text>

        <!-- Account rows -->
        <v-card-text v-else class="pa-2">
          <!-- Column headers -->
          <v-row
            dense
            class="text-caption text-medium-emphasis px-2 pb-1"
            no-gutters
          >
            <v-col>Account</v-col>
            <v-col cols="3" class="text-right">Current</v-col>
            <v-col cols="3" class="text-right">{{ projectedLabel }}</v-col>
          </v-row>
          <v-divider class="mb-1" />

          <v-row
            v-for="account in favoriteBalances"
            :key="account.id"
            dense
            no-gutters
            class="py-1 px-2 rounded account-row"
            align="center"
            @click="navigateTo(account.id)"
            style="cursor: pointer"
          >
            <!-- Account name + type indicator -->
            <v-col class="d-flex align-center ga-2 overflow-hidden">
              <v-avatar size="8" :color="account.account_type_color" />
              <BankLogo
                v-if="account.logo_url"
                :logo-url="account.logo_url"
                :size="18"
                class="flex-shrink-0"
              />
              <span class="text-body-2 font-weight-medium text-truncate">
                {{ account.account_name }}
              </span>
            </v-col>

            <!-- Current balance -->
            <v-col cols="3" class="text-right">
              <span
                :class="
                  account.balance >= 0
                    ? 'text-success font-weight-bold text-body-2'
                    : 'text-error font-weight-bold text-body-2'
                "
              >
                <NumberFlow
                  :value="account.balance ?? 0"
                  :format="{ style: 'currency', currency: 'USD' }"
                />
              </span>
            </v-col>

            <!-- Projected balance -->
            <v-col cols="3" class="text-right">
              <span
                :class="
                  (account.projected_balance ?? 0) >= 0
                    ? 'text-success text-body-2'
                    : 'text-error text-body-2'
                "
              >
                <NumberFlow
                  :value="account.projected_balance ?? 0"
                  :format="{ style: 'currency', currency: 'USD' }"
                />
              </span>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>
<script setup>
  import { computed } from "vue";
  import { useRouter } from "vue-router";
  import NumberFlow from "@number-flow/vue";
  import BankLogo from "@/components/BankLogo.vue";
  import { useFavoriteBalances } from "@/composables/accountsComposable";
  import { useTransactionsStore } from "@/stores/transactions";

  const { favoriteBalances, isLoading } = useFavoriteBalances();
  const router = useRouter();
  const transactions_store = useTransactionsStore();

  const projectedLabel = computed(() => {
    const d = new Date();
    d.setMonth(d.getMonth() + 1, 1);
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  });

  function navigateTo(accountId) {
    transactions_store.resetFilters();
    transactions_store.pageinfo.account_id = accountId;
    router.push(`/accounts/${accountId}`);
  }
</script>
<style scoped>
  .account-row:hover {
    background-color: rgba(var(--v-theme-primary), 0.06);
  }
</style>
