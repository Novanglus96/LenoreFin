<template>
  <div>
    <v-card
      variant="outlined"
      :elevation="4"
      :class="account && account.active ? 'bg-primary' : 'bg-primary-darken-2'"
      v-if="account"
      style="position: relative; overflow: hidden;"
    >
      <!-- Bank logo watermark -->
      <img
        v-if="account.bank && account.bank.logo_url"
        :src="account.bank.logo_url"
        alt=""
        class="bank-watermark"
        aria-hidden="true"
      />
      <v-icon
        v-else
        icon="mdi-bank"
        class="bank-watermark bank-watermark--icon"
        aria-hidden="true"
      />
      <template v-slot:text>
        <v-container fluid>
          <v-row density="compact" class="">
            <v-col lg="2" v-if="!smAndDown"></v-col>
            <v-col
              class="text-secondary text-center text-h6 font-weight-bold pa-0 ma-0 ga-0 align-content-center"
            >
              <v-card
                class="d-flex align-center justify-center mx-1 px-1 gx-1 bg-primary-lighten-1"
                variant="outlined"
              >
                <img
                  v-if="smAndDown && account.bank && account.bank.logo_url"
                  :src="account.bank.logo_url"
                  alt=""
                  aria-hidden="true"
                  class="inline-bank-logo mr-1"
                />
                <v-icon
                  v-else-if="smAndDown && account.bank"
                  icon="mdi-bank"
                  size="small"
                  class="mr-1"
                  aria-hidden="true"
                />
                <v-tooltip v-if="account.is_parent_account" text="Combined account" location="top">
                  <template v-slot:activator="{ props }">
                    <v-icon icon="mdi-layers" color="secondary" size="small" class="mr-1" v-bind="props" />
                  </template>
                </v-tooltip>
                <!-- Desktop: tooltip triggers edit on click -->
                <v-tooltip text="Edit Account" location="top" v-if="authStore.isFullAccess && !smAndDown">
                  <template v-slot:activator="{ props }">
                    <span
                      class="mx-1"
                      @click="editDialog = true"
                      tabindex="0"
                      @keydown.enter="editDialog = true"
                      role="button"
                      aria-pressed="false"
                      v-bind="props"
                    >
                      {{
                        account.active
                          ? account.account_name
                          : account.account_name + " (Inactive)"
                      }}
                    </span>
                  </template>
                </v-tooltip>
                <!-- Mobile full-access: plain name text (chevron is the toggle) -->
                <span class="mx-1 flex-grow-1" v-if="authStore.isFullAccess && smAndDown">
                  {{
                    account.active
                      ? account.account_name
                      : account.account_name + " (Inactive)"
                  }}
                </span>
                <span class="mx-1" v-if="!authStore.isFullAccess">
                  {{
                    account.active
                      ? account.account_name
                      : account.account_name + " (Inactive)"
                  }}
                </span>
                <EditAccountForm
                  v-model="editDialog"
                  :account="account"
                  @update-dialog="updateEditDialog"
                />
                <!-- Desktop inline action buttons -->
                <v-tooltip
                  :text="account.is_favorite ? 'Remove from Favorites' : 'Add to Favorites'"
                  location="top"
                  v-if="!smAndDown"
                >
                  <template v-slot:activator="{ props }">
                    <v-btn
                      :icon="account.is_favorite ? 'mdi-star' : 'mdi-star-outline'"
                      :color="account.is_favorite ? 'amber' : undefined"
                      flat
                      variant="text"
                      @click="toggleFavorite(account.id)"
                      v-bind="props"
                      size="small"
                      class="mx-0"
                      :disabled="!isOnline"
                    />
                  </template>
                </v-tooltip>
                <v-tooltip
                  :text="account.active ? 'Delete Account' : 'Enable Account'"
                  location="top"
                  v-if="authStore.isFullAccess && !smAndDown"
                >
                  <template v-slot:activator="{ props }">
                    <v-btn
                      :icon="account.active ? 'mdi-delete' : 'mdi-delete-restore'"
                      flat
                      variant="text"
                      @click="deleteDialog = true"
                      v-bind="props"
                      size="small"
                      class="mx-0"
                      :disabled="!isOnline"
                    />
                  </template>
                </v-tooltip>
                <!-- Mobile chevron toggle -->
                <v-btn
                  v-if="smAndDown"
                  :icon="actionDrawer ? 'mdi-chevron-up' : 'mdi-chevron-down'"
                  flat
                  variant="text"
                  size="small"
                  class="mx-0"
                  @click="actionDrawer = !actionDrawer"
                />
                <DeleteAccountForm
                  v-model="deleteDialog"
                  :account="account"
                  @update-dialog="updateDeleteDialog"
                />
              </v-card>
              <!-- Mobile inline action expand panel -->
              <v-expand-transition>
                <v-card
                  v-if="actionDrawer && smAndDown"
                  class="mx-1 mt-0 bg-primary-darken-2"
                  variant="outlined"
                  rounded="0 0 4 4"
                >
                  <v-card-text class="d-flex justify-center ga-3 py-2 px-2">
                    <v-btn
                      v-if="authStore.isFullAccess"
                      variant="tonal"
                      color="primary"
                      prepend-icon="mdi-pencil"
                      size="small"
                      @click="actionDrawer = false; editDialog = true"
                      :disabled="!isOnline"
                    >
                      Edit
                    </v-btn>
                    <v-btn
                      variant="tonal"
                      :color="account.is_favorite ? 'amber' : undefined"
                      :prepend-icon="account.is_favorite ? 'mdi-star' : 'mdi-star-outline'"
                      size="small"
                      @click="toggleFavorite(account.id)"
                      :disabled="!isOnline"
                    >
                      {{ account.is_favorite ? 'Unfavorite' : 'Favorite' }}
                    </v-btn>
                    <v-btn
                      v-if="authStore.isFullAccess"
                      variant="tonal"
                      color="error"
                      :prepend-icon="account.active ? 'mdi-delete' : 'mdi-delete-restore'"
                      size="small"
                      @click="actionDrawer = false; deleteDialog = true"
                      :disabled="!isOnline"
                    >
                      {{ account.active ? 'Delete' : 'Enable' }}
                    </v-btn>
                  </v-card-text>
                </v-card>
              </v-expand-transition>
            </v-col>
            <v-col cols="2" v-if="!smAndDown"></v-col>
          </v-row>
          <!-- Large Display View -->
          <v-row density="compact" v-if="!smAndDown">
            <v-col class="text-center align-content-end">
              <v-tooltip text="Adjust Balance" location="top" v-if="authStore.isFullAccess && !account.is_parent_account">
                <template v-slot:activator="{ props }">
                  <div
                    class="text-accent font-weight-bold text-h4 d-inline-block"
                    @click="adjBalDialog = true"
                    tabindex="0"
                    @keydown.enter="adjBalDialog = true"
                    role="button"
                    aria-pressed="false"
                    v-bind="props"
                    width="200"
                  >
                    <NumberFlow
                      :value="account.balance"
                      :format="{ style: 'currency', currency: 'USD' }"
                    />
                  </div>
                </template>
              </v-tooltip>
              <div
                class="text-accent font-weight-bold text-h4 d-inline-block"
                v-if="!authStore.isFullAccess || account.is_parent_account"
              >
                <NumberFlow
                  :value="account.balance"
                  :format="{ style: 'currency', currency: 'USD' }"
                />
              </div>
              <AdjustBalanceForm
                v-model="adjBalDialog"
                :account="account"
                @update-dialog="updateAdjBalDialog"
              />
              <div class="text-primary-lighten-2">{{ account.is_parent_account ? 'combined balance' : 'current balance' }}</div>
            </v-col>
            <v-col
              v-if="account.account_type.id == 1"
              class="text-center align-content-end"
            >
              <div class="text-white font-weight-bold text-body">
                {{
                  account.statement_date
                    ? formatDate(account.statement_date)
                    : "n/a"
                }}
              </div>
              <div class="text-primary-lighten-2">statement end date</div>
            </v-col>
            <v-col
              v-if="account.account_type.id == 1"
              class="text-center align-content-end"
            >
              <div class="text-white font-weight-bold text-body">
                <NumberFlow
                  :value="account.statement_balance"
                  :format="{ style: 'currency', currency: 'USD' }"
                />
              </div>
              <div class="text-primary-lighten-2">{{ account.calculate_payments && account.payment_strategy === 'M' ? 'minimum due' : 'statement balance' }}</div>
            </v-col>
            <v-col
              v-if="account.account_type.id == 1"
              class="text-center align-content-end"
            >
              <div class="text-white font-weight-bold text-body">
                {{ account.due_date ? formatDate(account.due_date) : "n/a" }}
              </div>
              <div class="text-primary-lighten-2">due date</div>
            </v-col>
            <v-col
              v-if="account.account_type.id == 1"
              class="text-center align-content-end"
            >
              <div
                class="text-white font-weight-bold text-body d-inline-block"
                @click="handleClick"
                tabindex="0"
                @keydown.enter="handleClick"
                role="button"
                aria-pressed="false"
              >
                <NumberFlow
                  :value="account.rewards_amount"
                  :format="{ style: 'currency', currency: 'USD' }"
                />
              </div>
              <div class="text-primary-lighten-2">
                rewards
                <v-icon
                  size="small"
                  icon="mdi-chart-line"
                  color="accent"
                ></v-icon>
              </div>
              <RewardsGraphs
                v-model="showRewardGraph"
                @update-dialog="updateRewardGraphDialog"
                :current-amounts="account.current_yr_rewards"
                :last-amounts="account.last_yr_rewards"
              />
            </v-col>
            <v-col
              v-if="account.account_type.id == 1"
              class="text-center align-content-end"
            >
              <div class="text-white font-weight-bold text-body">
                <NumberFlow
                  :value="account.available_credit"
                  :format="{ style: 'currency', currency: 'USD' }"
                />
              </div>
              <div class="text-primary-lighten-2">available credit</div>
            </v-col>
            <!-- Investment: estimated annual return -->
            <v-col
              v-if="account.account_type.slug === 'investment'"
              class="text-center align-content-end"
            >
              <div class="text-white font-weight-bold text-body">
                <span v-if="investmentReturn && investmentReturn.sufficient_data">
                  {{ investmentReturn.rate > 0 ? '+' : '' }}{{ investmentReturn.rate.toFixed(2) }}%
                  <v-tooltip
                    v-if="account.calculate_interest && authStore.isFullAccess && isOnline"
                    location="bottom"
                    text="Apply to forecast APY"
                  >
                    <template v-slot:activator="{ props: tipProps }">
                      <v-icon
                        size="x-small"
                        icon="mdi-chart-line-variant"
                        color="accent"
                        class="cursor-pointer"
                        v-bind="tipProps"
                        @click="applyReturnToForecast()"
                      />
                    </template>
                  </v-tooltip>
                </span>
                <span v-else class="text-primary-lighten-2">—</span>
              </div>
              <div class="text-primary-lighten-2">
                est. annual return
                <v-tooltip
                  location="bottom"
                  :text="`Based on last ${investmentReturn?.period_months ?? 12} months (${investmentReturn?.data_points ?? 0} transactions)`"
                >
                  <template v-slot:activator="{ props: tipProps }">
                    <v-icon size="x-small" icon="mdi-information-outline" v-bind="tipProps" />
                  </template>
                </v-tooltip>
              </div>
            </v-col>
          </v-row>
          <!-- Small Display View -->
          <v-row density="compact" v-if="smAndDown">
            <v-col class="text-center align-content-end">
              <v-tooltip text="Adjust Balance" location="top" v-if="authStore.isFullAccess && !account.is_parent_account">
                <template v-slot:activator="{ props }">
                  <div
                    class="text-accent-lighten-1 font-weight-bold text-h4 d-inline-block"
                    @click="adjBalDialog = true"
                    tabindex="0"
                    @keydown.enter="adjBalDialog = true"
                    role="button"
                    aria-pressed="false"
                    v-bind="props"
                    width="200"
                  >
                    <NumberFlow
                      :value="account.balance"
                      :format="{ style: 'currency', currency: 'USD' }"
                    />
                  </div>
                </template>
              </v-tooltip>
              <div
                class="text-accent-lighten-1 font-weight-bold text-h4 d-inline-block"
                v-if="!authStore.isFullAccess || account.is_parent_account"
              >
                <NumberFlow
                  :value="account.balance"
                  :format="{ style: 'currency', currency: 'USD' }"
                />
              </div>
              <AdjustBalanceForm
                v-model="adjBalDialog"
                :account="account"
                @update-dialog="updateAdjBalDialog"
              />
              <div class="text-primary-lighten-2">{{ account.is_parent_account ? 'combined balance' : 'current balance' }}</div>
            </v-col>
          </v-row>
          <v-row density="compact" v-if="smAndDown">
            <v-col class="text-center">
              <v-btn
                size="x-small"
                variant="text"
                :append-icon="!showMore ? 'mdi-chevron-down' : 'mdi-chevron-up'"
                @click="toggleMore"
                v-if="account.account_type.id == 1 || account.account_type.slug === 'investment'"
              >
                {{ !showMore ? "more" : "less" }}
              </v-btn>
            </v-col>
          </v-row>
        </v-container>
        <v-expand-transition>
          <v-container fluid v-if="account.account_type.slug === 'investment' && showMore">
            <v-row density="compact">
              <v-col class="text-center align-content-end">
                <div class="text-white font-weight-bold text-body">
                  <span v-if="investmentReturn && investmentReturn.sufficient_data">
                    {{ investmentReturn.rate > 0 ? '+' : '' }}{{ investmentReturn.rate.toFixed(2) }}%
                    <v-tooltip
                      v-if="account.calculate_interest && authStore.isFullAccess && isOnline"
                      location="bottom"
                      text="Apply to forecast APY"
                    >
                      <template v-slot:activator="{ props: tipProps }">
                        <v-icon
                          size="x-small"
                          icon="mdi-chart-line-variant"
                          color="accent"
                          class="cursor-pointer"
                          v-bind="tipProps"
                          @click="applyReturnToForecast()"
                        />
                      </template>
                    </v-tooltip>
                  </span>
                  <span v-else class="text-primary-lighten-2">—</span>
                </div>
                <div class="text-primary-lighten-2">est. annual return</div>
              </v-col>
            </v-row>
          </v-container>
        </v-expand-transition>
        <v-expand-transition>
          <v-container fluid v-if="account.account_type.id == 1 && showMore">
            <v-row density="compact" class="">
              <v-col
                v-if="account.account_type.id == 1"
                class="text-center align-content-end"
              >
                <div class="text-white font-weight-bold text-body">
                  {{
                    account.statement_date
                      ? formatDateShort(account.statement_date)
                      : "n/a"
                  }}
                </div>
                <div class="text-primary-lighten-2">statement end</div>
              </v-col>
              <v-col
                v-if="account.account_type.id == 1"
                class="text-center align-content-end"
              >
                <div class="text-white font-weight-bold text-body">
                  <NumberFlow
                    :value="account.statement_balance"
                    :format="{ style: 'currency', currency: 'USD' }"
                  />
                </div>
                <div class="text-primary-lighten-2">{{ account.calculate_payments && account.payment_strategy === 'M' ? 'minimum due' : 'statement balance' }}</div>
              </v-col>
            </v-row>
            <v-row density="compact">
              <v-col
                v-if="account.account_type.id == 1"
                class="text-center align-content-end"
              >
                <div class="text-white font-weight-bold text-body">
                  {{
                    account.due_date ? formatDateShort(account.due_date) : "n/a"
                  }}
                </div>
                <div class="text-primary-lighten-2">due date</div>
              </v-col>
              <v-col
                v-if="account.account_type.id == 1"
                class="text-center align-content-end"
              >
                <div
                  class="text-white font-weight-bold text-body d-inline-block"
                  @click="handleClick"
                  tabindex="0"
                  @keydown.enter="handleClick"
                  role="button"
                  aria-pressed="false"
                >
                  <NumberFlow
                    :value="account.rewards_amount"
                    :format="{ style: 'currency', currency: 'USD' }"
                  />
                </div>
                <div class="text-primary-lighten-2">
                  rewards
                  <v-icon
                    size="small"
                    icon="mdi-chart-line"
                    color="accent"
                  ></v-icon>
                </div>
                <RewardsGraphs
                  v-model="showRewardGraph"
                  @update-dialog="updateRewardGraphDialog"
                  :current-amounts="account.current_yr_rewards"
                  :last-amounts="account.last_yr_rewards"
                />
              </v-col>
              <v-col
                v-if="account.account_type.id == 1"
                class="text-center align-content-end"
              >
                <div class="text-white font-weight-bold text-body">
                  <NumberFlow
                    :value="account.available_credit"
                    :format="{ style: 'currency', currency: 'USD' }"
                  />
                </div>
                <div class="text-primary-lighten-2">available</div>
              </v-col>
            </v-row>
          </v-container>
        </v-expand-transition>
      </template>
    </v-card>
    <v-skeleton-loader
      type="card"
      color="primary"
      height="100"
      v-else
    ></v-skeleton-loader>
  </div>
</template>
<script setup>
  import { defineProps, ref, computed } from "vue";
  import { useAccountByID, useAccounts, useInvestmentReturn } from "@/composables/accountsComposable";
  import EditAccountForm from "./EditAccountForm.vue";
  import AdjustBalanceForm from "./AdjustBalanceForm.vue";
  import DeleteAccountForm from "./DeleteAccountForm.vue";
  import NumberFlow from "@number-flow/vue";
  import { useDisplay } from "vuetify";
  import RewardsGraphs from "./RewardsGraphs.vue";
  import { useAuthStore } from "@/stores/auth";
  import { useOnlineStatus } from "@/composables/useOnlineStatus";
  const { isOnline } = useOnlineStatus();

  const { smAndDown } = useDisplay();
  const authStore = useAuthStore();
  const adjBalDialog = ref(false);
  const editDialog = ref(false);
  const deleteDialog = ref(false);
  const actionDrawer = ref(false);
  const showMore = ref(false);
  const showRewardGraph = ref(false);

  const props = defineProps({
    account: Array,
  });

  const { account, editAccount } = useAccountByID(props.account);
  const { toggleFavorite } = useAccounts();

  const accountId = computed(() =>
    Array.isArray(props.account) ? props.account[0] : props.account,
  );
  const isInvestment = computed(
    () => account.value?.account_type?.slug === "investment",
  );
  const { investmentReturn } = useInvestmentReturn(
    computed(() => (isInvestment.value ? accountId.value : null)),
  );

  async function applyReturnToForecast() {
    if (!investmentReturn.value?.sufficient_data) return;
    await editAccount({
      id: accountId.value,
      annual_rate: investmentReturn.value.rate,
    });
  }

  const updateAdjBalDialog = value => {
    adjBalDialog.value = value;
  };
  const updateEditDialog = value => {
    editDialog.value = value;
  };
  const updateDeleteDialog = value => {
    deleteDialog.value = value;
  };
  const updateRewardGraphDialog = value => {
    showRewardGraph.value = value;
  };
  const formatDate = dateString => {
    const date = new Date(dateString + "T00:00:00Z");
    return new Intl.DateTimeFormat("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      timeZone: "UTC",
    }).format(date);
  };

  const formatDateShort = (input, padDay = false) => {
    let date;

    // If input is already a Date object, trust it
    if (input instanceof Date) {
      date = input;
    } else if (typeof input === "string" && /^\d{4}-\d{2}-\d{2}$/.test(input)) {
      // Manual parse YYYY-MM-DD to LOCAL date (no timezone shift)
      const [y, m, d] = input.split("-").map(Number);
      date = new Date(y, m - 1, d);
    } else {
      date = new Date(input); // fallback for timestamps
    }

    if (isNaN(date)) {
      console.warn("Invalid date:", input);
      return "";
    }

    const month = date.toLocaleString("en-US", { month: "short" });
    const day = date.getDate();

    return `${month}-${padDay ? String(day).padStart(2, "0") : day}`;
  };

  const toggleMore = () => {
    showMore.value = !showMore.value;
  };

  const handleClick = () => {
    showRewardGraph.value = true;
  };
</script>
<style scoped>
  .bank-watermark {
    position: absolute;
    right: -16px;
    top: -16px;
    width: 160px;
    height: 160px;
    object-fit: contain;
    opacity: 0.15;
    transform: rotate(20deg);
    pointer-events: none;
    z-index: 0;
  }

  .bank-watermark--icon {
    font-size: 160px !important;
    width: 160px;
    height: 160px;
  }

  .inline-bank-logo {
    height: 20px;
    width: auto;
    max-width: 48px;
    object-fit: contain;
    opacity: 0.8;
    flex-shrink: 0;
  }

  @media (max-width: 600px) {
    .bank-watermark {
      display: none;
    }
  }
</style>
