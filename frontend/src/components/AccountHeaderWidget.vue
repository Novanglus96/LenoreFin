<template>
  <div>
    <v-card
      variant="outlined"
      :elevation="4"
      :class="account.active ? 'bg-primary' : 'bg-primary-darken-2'"
      v-if="!isLoading"
    >
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
                <v-tooltip text="Edit Account" location="top">
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
                <EditAccountForm
                  v-model="editDialog"
                  :account="account"
                  @update-dialog="updateEditDialog"
                />
                <v-tooltip
                  :text="account.active ? 'Delete Account' : 'Enable Account'"
                  location="top"
                >
                  <template v-slot:activator="{ props }">
                    <v-btn
                      :icon="
                        account.active ? 'mdi-delete' : 'mdi-delete-restore'
                      "
                      flat
                      variant="text"
                      @click="deleteDialog = true"
                      v-bind="props"
                      size="small"
                      class="mx-0"
                    />
                  </template>
                </v-tooltip>
                <DeleteAccountForm
                  v-model="deleteDialog"
                  :account="account"
                  @update-dialog="updateDeleteDialog"
                />
              </v-card>
            </v-col>
            <v-col cols="2" v-if="!smAndDown"></v-col>
          </v-row>
          <!-- Large Display View -->
          <v-row density="compact" v-if="!smAndDown">
            <v-col class="text-center align-content-end">
              <v-tooltip text="Adjust Balance" location="top">
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
              <AdjustBalanceForm
                v-model="adjBalDialog"
                :account="account"
                @update-dialog="updateAdjBalDialog"
              />
              <div class="text-primary-lighten-2">current balance</div>
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
                  :value="account.last_statement_amount"
                  :format="{ style: 'currency', currency: 'USD' }"
                />
              </div>
              <div class="text-primary-lighten-2">last statement balance</div>
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
          </v-row>
          <!-- Small Display View -->
          <v-row density="compact" v-if="smAndDown">
            <v-col class="text-center align-content-end">
              <v-tooltip text="Adjust Balance" location="top">
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
              <AdjustBalanceForm
                v-model="adjBalDialog"
                :account="account"
                @update-dialog="updateAdjBalDialog"
              />
              <div class="text-primary-lighten-2">current balance</div>
            </v-col>
          </v-row>
          <v-row density="compact" v-if="smAndDown">
            <v-col class="text-center">
              <v-btn
                size="x-small"
                variant="text"
                :append-icon="!showMore ? 'mdi-chevron-down' : 'mdi-chevron-up'"
                @click="toggleMore"
                v-if="account.account_type.id == 1"
              >
                {{ !showMore ? "more" : "less" }}
              </v-btn>
            </v-col>
          </v-row>
        </v-container>
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
                    :value="account.last_statement_amount"
                    :format="{ style: 'currency', currency: 'USD' }"
                  />
                </div>
                <div class="text-primary-lighten-2">last statement</div>
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
  import { defineProps, ref } from "vue";
  import { useAccountByID } from "@/composables/accountsComposable";
  import EditAccountForm from "./EditAccountForm.vue";
  import AdjustBalanceForm from "./AdjustBalanceForm.vue";
  import DeleteAccountForm from "./DeleteAccountForm.vue";
  import NumberFlow from "@number-flow/vue";
  import { useDisplay } from "vuetify";
  import RewardsGraphs from "./RewardsGraphs.vue";

  const { smAndDown } = useDisplay();
  const adjBalDialog = ref(false);
  const editDialog = ref(false);
  const deleteDialog = ref(false);
  const showMore = ref(false);
  const showRewardGraph = ref(false);

  const props = defineProps({
    account: Array,
  });

  const { account, isLoading } = useAccountByID(props.account);

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
