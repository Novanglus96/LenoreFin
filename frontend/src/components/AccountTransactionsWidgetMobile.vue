<template>
  <v-card variant="outlined" :elevation="4" class="bg-white">
    <template v-slot:append>
      <v-tooltip text="Add New Transaction" location="top">
        <template v-slot:activator="{ props }">
          <v-btn
            icon="mdi-invoice-plus"
            flat
            variant="plain"
            color="success"
            @click="transactionAddFormDialog = true"
            v-bind="props"
            v-if="!isActive"
          ></v-btn>
        </template>
      </v-tooltip>
      <TransactionFormMobile
        v-model="transactionAddFormDialog"
        @add-transaction="clickAddTransaction"
        @edit-transaction="clickEditTransaction"
        :isEdit="false"
        @update-dialog="updateAddDialog"
        :account_id="props.account"
        :passedFormData="blankForm"
      />
    </template>
    <template v-slot:title>
      <span class="text-subtitle-2 text-secondary">Transactions</span>
    </template>
    <template v-slot:text>
      <v-data-iterator
        :items="transactions ? transactions.transactions : []"
        :loading="isLoading"
        items-per-page="10"
      >
        <template v-slot:default="{ items }">
          <template v-for="(item, i) in items" :key="i">
            <v-card
              class="flex ma-0 pa-0 ga-0"
              hover
              ripple
              role="button"
              @click="toggleMore(i)"
              :loading="isActive"
              :disabled="isActive"
              :color="item.raw.status.id === 1 ? 'grey-lighten-1' : ''"
              ><template v-slot:loader="{ isActive }">
                <v-progress-linear
                  :active="isActive"
                  color="secondary"
                  height="4"
                  indeterminate
                ></v-progress-linear> </template
              ><v-card-text
                ><v-container class="flex ma-0 pa-0 ga-0"
                  ><v-row dense
                    ><v-col cols="7">
                      <v-container
                        ><v-row dense
                          ><v-col
                            class="text-truncate text-subtitle-2 font-weight-bold"
                            >{{ item.raw.description }}</v-col
                          ></v-row
                        ><v-row dense
                          ><v-col>{{
                            item.raw.status.transaction_status
                          }}</v-col></v-row
                        >
                        <v-row dense
                          ><v-col class="font-italic">{{
                            item.raw.transaction_date
                          }}</v-col></v-row
                        ></v-container
                      ></v-col
                    ><v-col cols="4" class="d-flex justify-center align-center"
                      ><v-container
                        ><v-row dense
                          ><v-col class="d-flex justify-center align-center"
                            ><span
                              :class="getClassForMoney(item.raw.pretty_total)"
                            >
                              {{ formatCurrency(item.raw.pretty_total) }}
                            </span></v-col
                          ></v-row
                        ><v-row
                          dense
                          v-if="
                            item.raw.checkNumber ||
                            item.raw.paycheck ||
                            item.raw.id < 0 ||
                            item.raw.attachments
                          "
                          ><v-col class="d-flex justify-center align-center"
                            ><div v-if="item.raw.checkNumber">
                              <v-icon
                                icon="mdi-checkbook"
                                color="amber"
                              ></v-icon
                              ><span
                                :class="
                                  item.raw.status.id == 1
                                    ? 'font-italic text-grey'
                                    : 'font-weight-bold text-black'
                                "
                                >#{{ item.raw.checkNumber }}</span
                              >
                            </div>
                            <div v-if="item.raw.paycheck">
                              <v-icon
                                icon="mdi-cash-multiple"
                                color="amber"
                              ></v-icon>
                            </div>
                            <div v-if="item.raw.id < 0">
                              <v-icon icon="mdi-bell" color="amber"></v-icon>
                            </div>
                            <div v-if="item.raw.attachments">
                              <v-icon
                                icon="mdi-paperclip"
                                color="amber"
                              ></v-icon></div></v-col></v-row></v-container></v-col
                    ><v-col cols="1" class="d-flex justify-center align-center"
                      ><v-icon
                        :icon="
                          !showMore[i] ? 'mdi-chevron-down' : 'mdi-chevron-up'
                        "
                        variant="plain"
                      ></v-icon></v-col></v-row></v-container></v-card-text></v-card
            ><v-expand-transition
              ><v-card
                v-if="showMore[i]"
                color="grey-lighten-2"
                class="flex ma-0 pa-0 ga-0"
                ><v-card-text
                  ><v-container class="flex ma-0 pa-0 ga-0"
                    ><v-row dense
                      ><v-col
                        ><v-container
                          ><v-row dense
                            ><v-col
                              ><span
                                :class="
                                  item.raw.status.id == 1
                                    ? 'font-italic text-grey text-body-2'
                                    : 'font-weight-bold text-black text-body-2'
                                "
                                v-for="tag in item.raw.tags"
                                :key="tag"
                              >
                                <v-icon
                                  icon="mdi-tag"
                                  size="x-small"
                                  :color="
                                    item.raw.status.id == 1 ? 'grey' : 'black'
                                  "
                                  v-if="tag"
                                ></v-icon>
                                {{ tag }}&nbsp;
                              </span></v-col
                            ></v-row
                          ><v-row dense
                            ><v-col class="text-secondary">{{
                              item.raw.pretty_account
                            }}</v-col></v-row
                          ></v-container
                        ></v-col
                      ></v-row
                    ></v-container
                  ></v-card-text
                ><v-card-actions
                  ><v-spacer></v-spacer
                  ><v-btn
                    color="secondary"
                    :disabled="item.raw.status.id > 1 ? true : false"
                    @click="clickClearTransaction(item.raw, i)"
                    >{{
                      item.raw.id < 0 ? "Add as Transaction" : "Clear"
                    }}</v-btn
                  ><v-btn
                    color="secondary"
                    v-if="item.raw.id > 0"
                    @click="toggleEditDialog(i, item.raw)"
                    >Edit</v-btn
                  ><TransactionFormMobile
                    v-model="transactionEditFormDialog[i]"
                    @add-transaction="clickAddTransaction"
                    @edit-transaction="clickEditTransaction"
                    :isEdit="true"
                    @update-dialog="toggleEditDialog(i)"
                    :passedFormData="editTransaction" />
                  <v-btn
                    color="error"
                    v-if="item.raw.id > 0"
                    @click="toggleDeleteDialog(i)"
                    >Remove</v-btn
                  ><v-dialog width="500" v-model="showDeleteDialog[i]">
                    <v-card :title="item.raw.description">
                      <v-card-text>
                        Are you sure you want to delete this transaction?
                      </v-card-text>

                      <v-card-actions>
                        <v-spacer></v-spacer>

                        <v-btn
                          text="Confirm"
                          @click="
                            clickRemoveTransaction(item.raw.id, i);
                            toggleDeleteDialog(i);
                          "
                        ></v-btn>
                      </v-card-actions>
                    </v-card> </v-dialog></v-card-actions></v-card
            ></v-expand-transition>

            <br />
          </template>
        </template>
        <template v-slot:loader
          ><v-skeleton-loader
            class="border"
            type="paragraph"
          ></v-skeleton-loader
        ></template>
        <template v-slot:footer="{ page, pageCount, prevPage, nextPage }">
          <div class="d-flex align-center justify-center pa-4">
            <v-btn
              :disabled="page === 1"
              density="comfortable"
              icon="mdi-arrow-left"
              variant="tonal"
              rounded
              @click="prevPage"
            ></v-btn>

            <div class="mx-2 text-caption">
              Page {{ page }} of {{ pageCount }}
            </div>

            <v-btn
              :disabled="page >= pageCount"
              density="comfortable"
              icon="mdi-arrow-right"
              variant="tonal"
              rounded
              @click="nextPage"
            ></v-btn>
          </div>
        </template>
      </v-data-iterator>
    </template>
  </v-card>
</template>
<script setup>
import { ref, defineProps, defineEmits, computed } from "vue";
import { useTransactions } from "@/composables/transactionsComposable";
import { useReminders } from "@/composables/remindersComposable";
import TransactionFormMobile from "@/components/TransactionFormMobile";

const today = new Date();
const year = today.getFullYear();
const month = String(today.getMonth() + 1).padStart(2, "0");
const day = String(today.getDate()).padStart(2, "0");
const formattedDate = `${year}-${month}-${day}`;
const showDeleteDialog = ref({});
const transactionAddFormDialog = ref(false);
const transactionEditFormDialog = ref({});
const showMore = ref({});

const props = defineProps({
  account: Number,
  maxdays: { type: Number, default: 14 },
  forecast: { type: Boolean, default: false },
  dateLimit: String,
});
const emit = defineEmits([
  "addTransaction",
  "removeTransaction",
  "editTransaction",
  "clearTransaction",
]);

const toggleMore = index => {
  showMore.value[index] = !showMore.value[index];
};

const toggleDeleteDialog = index => {
  showDeleteDialog.value[index] = !showDeleteDialog.value[index];
};

const toggleEditDialog = (index, transaction) => {
  if (!transaction) {
    editTransaction.value = {
      id: 0,
      transaction_date: formattedDate,
      total_amount: 0,
      status: {
        id: 1,
        transaction_status: "Pending",
      },
      memo: "",
      description: null,
      edit_date: formattedDate,
      add_date: formattedDate,
      transaction_type: {
        id: 1,
        transaction_type: "Expense",
      },
      reminder: null,
      paycheck: null,
      balance: 0,
      pretty_account: null,
      tags: [],
      details: [],
      pretty_total: 0,
      source_account_id: 0,
      destination_account_id: null,
    };
  } else {
    editTransaction.value = transaction;
  }
  transactionEditFormDialog.value[index] =
    !transactionEditFormDialog.value[index];
};

const blankForm = ref({
  id: 0,
  status: {
    id: 1,
  },
  transaction_type: {
    id: 1,
  },
  transaction_date: formattedDate,
  memo: "",
  source_account_id: parseInt(props.account),
  destination_account_id: null,
  edit_date: formattedDate,
  add_date: formattedDate,
  tag_id: 1,
  total_amount: 0,
});
const editTransaction = ref({
  id: 0,
  transaction_date: formattedDate,
  total_amount: 0,
  status: {
    id: 1,
    transaction_status: "Pending",
  },
  memo: "",
  description: null,
  edit_date: formattedDate,
  add_date: formattedDate,
  transaction_type: {
    id: 1,
    transaction_type: "Expense",
  },
  reminder: null,
  paycheck: null,
  balance: 0,
  pretty_account: null,
  tags: [],
  details: [],
  pretty_total: 0,
  source_account_id: 0,
  destination_account_id: null,
});

const {
  isLoading,
  isFetching,
  transactions,
  removeTransaction,
  clearTransaction,
} = useTransactions();

const isActive = computed(
  () => !(isLoading.value === false && isFetching.value === false),
);
const { addReminderTransaction } = useReminders();

const getClassForMoney = (amount, status) => {
  let color = "";
  let font = "";

  if (status == 1) {
    font = "font-italic";
    if (amount < 0) {
      color = "text-red-lighten-1";
    } else {
      color = "text-green-lighten-1";
    }
  } else {
    font = "font-weight-bold";
    if (amount < 0) {
      color = "text-red";
    } else {
      color = "text-green";
    }
  }

  return color + " " + font + " text-h6";
};

const clickAddTransaction = async () => {
  emit("addTransaction", props.account);
};

const clickRemoveTransaction = async (transaction, index) => {
  showMore.value[index] = false;
  let transactions = [transaction];
  removeTransaction(transactions);
};

const clickClearTransaction = async (transaction, index) => {
  showMore.value[index] = false;
  if (transaction.id > 0) {
    let transactions = [transaction.id];
    clearTransaction(transactions);
  } else {
    addReminderTransaction(transaction);
  }
};

const clickEditTransaction = async transaction_id => {
  emit("editTransaction", transaction_id);
};

const updateAddDialog = () => {
  transactionAddFormDialog.value = false;
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
<style>
/* alt-pagination */
.alt-pagination .bh-pagination .bh-page-item {
  width: auto; /* equivalent to w-max */
  min-width: 32px;
  border-radius: 0.25rem; /* equivalent to rounded */
}
/* Customize the color of the selected page number */
.alt-pagination .bh-pagination .bh-page-item.bh-active {
  background-color: #06966a; /* Change this to your desired color */
  border-color: black;
  font-weight: bold; /* Optional: Make the text bold */
}
.alt-pagination .bh-pagination .bh-page-item:not(.bh-active):hover {
  background-color: #ff5900;
  border-color: black;
}

.icon-with-text {
  position: relative;
  display: inline-block;
}

.icon-text {
  position: absolute;
  top: 0;
  right: 1;
  color: black;
  padding: 4px 1px;
  font-size: 0.7rem;
}

.floating-button-group {
  position: fixed;
  bottom: 82px;
  right: 12px;
  display: flex;
  flex-direction: column;
  gap: 1px;
  z-index: 1000; /* Ensure it appears above most content */
}
</style>
