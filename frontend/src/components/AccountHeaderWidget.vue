<template>
  <div>
    <v-card
      variant="outlined"
      :elevation="4"
      :class="account.active ? 'bg-secondary' : 'bg-grey'"
      v-if="!isLoading"
    >
      <template v-slot:text>
        <v-container fluid>
          <v-row density="compact" class=""
            ><v-col cols="2"></v-col
            ><v-col
              class="text-primary text-center text-h6 font-weight-bold pa-0 ma-0 ga-0 align-content-center"
              ><v-card
                class="d-flex align-center justify-center mx-1 px-1 gx-1 bg-secondary-lighten-1"
                variant="outlined"
                ><v-tooltip text="Edit Account" location="top">
                  <template v-slot:activator="{ props }">
                    <span
                      class="mx-1"
                      @click="editDialog = true"
                      tabindex="0"
                      @keydown.enter="editDialog = true"
                      role="button"
                      aria-pressed="false"
                      v-bind="props"
                      >{{
                        account.active
                          ? account.account_name
                          : account.account_name + " (Inactive)"
                      }}</span
                    ></template
                  >
                </v-tooltip>
                <EditAccountForm
                  v-model="editDialog"
                  :account="account"
                  @update-dialog="updateEditDialog" />
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
                  @update-dialog="updateDeleteDialog" /></v-card></v-col
            ><v-col cols="2"></v-col></v-row
          ><v-row density="compact"
            ><v-col class="text-center align-content-end"
              ><v-tooltip text="Adjust Balance" location="top">
                <template v-slot:activator="{ props }"
                  ><div
                    class="text-accent-lighten-1 font-weight-bold text-h4 d-inline-block"
                    @click="adjBalDialog = true"
                    tabindex="0"
                    @keydown.enter="adjBalDialog = true"
                    role="button"
                    aria-pressed="false"
                    v-bind="props"
                    width="200"
                  >
                    {{ formatCurrency(account.balance) }}
                  </div></template
                ></v-tooltip
              ><AdjustBalanceForm
                v-model="adjBalDialog"
                :account="account"
                @update-dialog="updateAdjBalDialog"
              />
              <div class="text-secondary-lighten-2">current balance</div></v-col
            >
            <v-col
              v-if="account.account_type.id == 1"
              class="text-center align-content-end"
              ><div class="text-white font-weight-bold text-body">
                {{
                  account.next_cycle_date
                    ? formatDate(account.next_cycle_date)
                    : "n/a"
                }}
              </div>
              <div class="text-secondary-lighten-2">
                statement end date
              </div></v-col
            ><v-col
              v-if="account.account_type.id == 1"
              class="text-center align-content-end"
              ><div class="text-white font-weight-bold text-body">
                {{ formatCurrency(account.last_statement_amount) }}
              </div>
              <div class="text-secondary-lighten-2">
                last statement balance
              </div></v-col
            ><v-col
              v-if="account.account_type.id == 1"
              class="text-center align-content-end"
              ><div class="text-white font-weight-bold text-body">
                {{ account.due_date ? formatDate(account.due_date) : "n/a" }}
              </div>
              <div class="text-secondary-lighten-2">due date</div></v-col
            ><v-col
              v-if="account.account_type.id == 1"
              class="text-center align-content-end"
              ><div
                class="text-white font-weight-bold text-body d-inline-block"
                @click="handleClick"
                tabindex="0"
                @keydown.enter="handleClick"
                role="button"
                aria-pressed="false"
              >
                {{ formatCurrency(account.rewards_amount) }}
              </div>
              <div class="text-secondary-lighten-2">rewards</div></v-col
            ><v-col
              v-if="account.account_type.id == 1"
              class="text-center align-content-end"
              ><div class="text-white font-weight-bold text-body">
                {{ formatCurrency(account.available_credit) }}
              </div>
              <div class="text-secondary-lighten-2">
                available credit
              </div></v-col
            ></v-row
          >
        </v-container>
      </template>
    </v-card>
    <v-skeleton-loader
      type="card"
      color="secondary"
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

const adjBalDialog = ref(false);
const editDialog = ref(false);
const deleteDialog = ref(false);

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
const formatDate = dateString => {
  const date = new Date(dateString + "T00:00:00Z");
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    timeZone: "UTC",
  }).format(date);
};

const formatCurrency = value => {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
};
</script>
