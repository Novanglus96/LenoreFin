<template>
  <v-card variant="outlined" :elevation="4" class="bg-white ma-0 pa-0 ga-0">
    <v-card-title>
      <span class="text-subtitle-2 text-secondary">Upcoming Transactions</span>
    </v-card-title>
    <v-card-text>
      <v-list v-if="!isLoading" density="compact">
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
              {{ transaction.description }}
            </v-list-item-title>
            <v-list-item-subtitle>
              <v-container class="ma-0 pa-0 ga-0">
                <v-row dense class="ma-0 pa-0 ga-0">
                  <v-col class="ma-0 pa-0 ga-0">
                    {{ transaction.status.transaction_status }}
                  </v-col>
                  <v-col class="ma-0 pa-0 ga-0 text-right">
                    <span :class="getClassForMoney(transaction.pretty_total)">
                      {{ formatCurrency(transaction.pretty_total) }}
                    </span>
                  </v-col>
                </v-row>
                <v-row dense class="ma-0 pa-0 ga-0">
                  <v-col class="ma-0 pa-0 ga-0 font-italic" cols="3">
                    {{ transaction.transaction_date }}
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
    </v-card-text>
  </v-card>
</template>
<script setup>
  import { useTransactions } from "@/composables/transactionsComposable";

  const { isLoading, transactions } = useTransactions();

  const getClassForMoney = (amount, status) => {
    let color = "";
    let font = "";

    if (status == 1) {
      font = "font-italic font-weight-bold";
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
