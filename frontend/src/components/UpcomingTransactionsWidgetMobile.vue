<template>
  <v-card variant="outlined" :elevation="4" class="bg-white">
    <template v-slot:title>
      <span class="text-subtitle-2 text-secondary">Upcoming Transactions</span>
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
                        ><v-row dense v-if="item.raw.checkNumber"
                          ><v-col class="d-flex justify-center align-center"
                            ><v-icon icon="mdi-checkbook" color="amber"></v-icon
                            ><span
                              :class="
                                item.raw.status.id == 1
                                  ? 'font-italic text-grey icon-text'
                                  : 'font-weight-bold text-black icon-text'
                              "
                              >#{{ item.raw.checkNumber }}</span
                            ></v-col
                          ></v-row
                        ><v-row dense v-if="item.raw.paycheck"
                          ><v-col class="d-flex justify-center align-center"
                            ><v-icon
                              icon="mdi-cash-multiple"
                              color="amber"
                            ></v-icon></v-col></v-row></v-container></v-col
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
                ></v-card
              ></v-expand-transition
            >

            <br />
          </template>
        </template>
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
import { useTransactions } from "@/composables/transactionsComposable";
import { ref } from "vue";

const showMore = ref({});
const { isLoading, transactions } = useTransactions();

const toggleMore = index => {
  showMore.value[index] = !showMore.value[index];
};

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
