<template>
  <v-card variant="outlined" :elevation="4" class="bg-white">
    <template v-slot:title>
      <span class="text-subtitle-2 text-secondary">Upcoming Transactions</span>
    </template>
    <template v-slot:text>
      <!-- Large Display View -->
      <vue3-datatable
        :rows="transactions ? transactions.transactions : []"
        :columns="columns"
        :loading="isLoading"
        :totalRows="transactions ? transactions.transactions.length : 0"
        :isServerMode="false"
        pageSize="10"
        :hasCheckbox="false"
        noDataContent="No transactions"
        ref="trans_table"
        skin="bh-table-striped bh-table-compact"
        :pageSizeOptions="[10]"
        :showPageSize="false"
        paginationInfo="Showing {0} to {1} of {2} transactions"
        class="alt-pagination"
        v-if="!smAndDown"
      >
        <!--height="280px"-->
        <template #transaction_date="row">
          <span
            :class="
              row.value.status.id == 1
                ? 'font-italic text-grey'
                : 'font-weight-bold text-black'
            "
          >
            {{ row.value.transaction_date }}
          </span>
        </template>
        <template #pretty_total="row">
          <span
            :class="
              getClassForMoney(row.value.pretty_total, row.value.status.id)
            "
          >
            {{ formatCurrency(row.value.pretty_total) }}
          </span>
        </template>
        <template #checkNumber="row">
          <v-tooltip text="Check" location="top">
            <template v-slot:activator="{ props }">
              <div class="icon-with-text" v-if="row.value.checkNumber">
                <v-icon
                  icon="mdi-checkbook"
                  color="amber"
                  v-bind="props"
                ></v-icon>
                <span
                  :class="
                    row.value.status.id == 1
                      ? 'font-italic text-grey icon-text'
                      : 'font-weight-bold text-black icon-text'
                  "
                >
                  #{{ row.value.checkNumber }}
                </span>
              </div>
            </template>
          </v-tooltip>
        </template>
        <template #description="row">
          <span
            :class="
              row.value.status.id == 1
                ? 'font-italic text-grey'
                : 'font-weight-bold text-black'
            "
          >
            {{ row.value.description }}
          </span>
        </template>
        <template #tags="row">
          <span
            :class="
              row.value.status.id == 1
                ? 'font-italic text-grey text-body-2'
                : 'font-weight-bold text-black text-body-2'
            "
            v-for="tag in row.value.tags"
            :key="tag"
          >
            <v-icon
              icon="mdi-tag"
              size="x-small"
              :color="row.value.status.id == 1 ? 'grey' : 'black'"
              v-if="tag"
            ></v-icon>
            {{ tag }}&nbsp;
          </span>
        </template>
        <template #pretty_account="row">
          <span
            :class="
              row.value.status.id == 1
                ? 'font-italic text-grey'
                : 'font-weight-bold text-black'
            "
          >
            {{ row.value.pretty_account }}
          </span>
        </template>
      </vue3-datatable>
      <!-- Small Display View -->
      <v-list v-if="!isLoading && smAndDown" density="compact">
        <div
          v-for="transaction in transactions.transactions"
          :key="transaction.id"
        >
          <v-list-item
            :key="transaction.id"
            class="border-thin"
            rounded
            elevation="1"
          >
            <v-list-item-title class="font-weight-bold text-truncate">
              <v-icon
                icon="mdi-circle-medium"
                color="grey"
                v-if="transaction.status.id == 1"
              ></v-icon>
              {{ transaction.description }}
            </v-list-item-title>
            <v-list-item-subtitle>
              <v-container class="ma-0 pa-0 ga-0">
                <v-row dense class="ma-0 pa-0 ga-0">
                  <v-col class="ma-0 pa-0 ga-0">
                    {{ transaction.transaction_date }}
                  </v-col>
                  <v-col class="ma-0 pa-0 ga-0 text-right" cols="6">
                    <span :class="getClassForMoney(transaction.pretty_total)">
                      {{ formatCurrency(transaction.pretty_total) }}
                    </span>
                  </v-col>
                </v-row>
                <v-row dense class="ma-0 pa-0 ga-0">
                  <v-col class="ma-0 pa-0 ga-0 font-italic" cols="3">
                    <v-icon
                      icon="mdi-cash-multiple"
                      v-if="transaction.paycheck"
                      color="amber"
                    ></v-icon>
                    <v-icon
                      icon="mdi-checkbook"
                      color="amber"
                      v-if="transaction.checkNumber"
                    ></v-icon>
                  </v-col>
                  <v-col
                    class="ma-0 pa-0 ga-0 text-right font-weight-bold text-truncate"
                  >
                    {{ transaction.pretty_account }}
                  </v-col>
                </v-row>
                <v-row dense class="ma-0 pa-0 ga-0">
                  <v-col class="ma-0 pa-0 ga-0 text-center text-truncate">
                    <span
                      :class="
                        transaction.status.id == 1
                          ? 'font-italic text-grey text-body-2'
                          : 'font-weight-bold text-black text-body-2'
                      "
                      v-for="tag in transaction.tags"
                      :key="tag"
                    >
                      <v-icon
                        icon="mdi-tag"
                        size="x-small"
                        :color="transaction.status.id == 1 ? 'grey' : 'black'"
                        v-if="tag"
                      ></v-icon>
                      <v-icon
                        icon="mdi-tag-hidden"
                        size="x-small"
                        :color="transaction.status.id == 1 ? 'grey' : 'black'"
                        v-else
                      ></v-icon>
                      {{ tag }}&nbsp;
                    </span>
                    <span
                      :class="
                        transaction.status.id == 1
                          ? 'font-italic text-grey text-body-2'
                          : 'font-weight-bold text-black text-body-2'
                      "
                      v-if="transaction.tags.length === 0"
                    >
                      <v-icon
                        icon="mdi-tag-hidden"
                        size="x-small"
                        :color="transaction.status.id == 1 ? 'grey' : 'black'"
                      ></v-icon>
                    </span>
                  </v-col>
                </v-row>
              </v-container>
            </v-list-item-subtitle>
          </v-list-item>
        </div>
      </v-list>
    </template>
  </v-card>
</template>
<script setup>
  import { useTransactions } from "@/composables/transactionsComposable";
  import Vue3Datatable from "@bhplugin/vue3-datatable";
  import "@bhplugin/vue3-datatable/dist/style.css";
  import { ref } from "vue";
  import { useDisplay } from "vuetify";

  const { smAndDown } = useDisplay();

  const { isLoading, transactions } = useTransactions();
  const columns = ref([
    { field: "transaction_date", title: "Date", type: "date", width: "120px" },
    { field: "pretty_total", title: "Amount", type: "number", width: "100px" },
    { field: "checkNumber", tilte: "Check #", width: "75px" },
    { field: "description", title: "Description" },
    { field: "tags", title: "Tag(s)", width: "200px" },
    { field: "pretty_account", title: "Account" },
  ]);

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

    return color + " " + font;
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
</style>
