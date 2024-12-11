<template>
  <div>
    <v-row class="pa-1 ga-1 rounded" no-gutters>
      <v-col class="rounded">
        <v-card v-if="!isLoading">
          <v-card-title>Tag Totals</v-card-title>
          <v-card-text>
            <v-container>
              <v-row dense>
                <v-col>
                  <Bar :data="tag_transactions.data" :options="options" />
                </v-col>
              </v-row>
              <v-row>
                <v-col class="text-right"
                  ><span class="text-subtitle-2"
                    >{{ tag_transactions.year1 }} Avg:
                    {{ formatCurrency(tag_transactions.year1_avg) }}</span
                  ></v-col
                >
                <v-col class="text-left"
                  ><span class="text-subtitle-2"
                    >{{ tag_transactions.year2 }} Avg:
                    {{ formatCurrency(tag_transactions.year2_avg) }}</span
                  ></v-col
                >
              </v-row>
            </v-container>
          </v-card-text>
        </v-card>
        <v-skeleton-loader type="card" v-else></v-skeleton-loader>
      </v-col>
    </v-row>
    <v-row class="pa-1 ga-1 rounded" no-gutters>
      <v-col class="rounded">
        <v-card v-if="!isLoading">
          <v-card-title>Transactions</v-card-title>
          <v-card-text>
            <v-data-iterator
              :items="tag_transactions ? tag_transactions.transactions : []"
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
                                  >{{ item.raw.transaction.description }}</v-col
                                ></v-row
                              ><v-row dense
                                ><v-col>{{
                                  item.raw.transaction.status.transaction_status
                                }}</v-col></v-row
                              >
                              <v-row dense
                                ><v-col class="font-italic">{{
                                  item.raw.transaction.transaction_date
                                }}</v-col></v-row
                              ></v-container
                            ></v-col
                          ><v-col
                            cols="4"
                            class="d-flex justify-center align-center"
                            ><v-container
                              ><v-row dense
                                ><v-col
                                  class="d-flex justify-center align-center"
                                  ><span
                                    :class="
                                      getClassForMoney(item.raw.detail_amt)
                                    "
                                  >
                                    {{ formatCurrency(item.raw.detail_amt) }}
                                  </span></v-col
                                ></v-row
                              ><v-row dense
                                ><v-col
                                  class="d-flex justify-center align-center"
                                  ><span
                                    :class="
                                      getClassForMoneyBalance(
                                        item.raw.transaction.total_amount,
                                      )
                                    "
                                    >({{
                                      formatCurrency(
                                        item.raw.transaction.total_amount,
                                      )
                                    }})</span
                                  ></v-col
                                ></v-row
                              ><v-row
                                dense
                                v-if="
                                  item.raw.transaction.checkNumber ||
                                  item.raw.transaction.paycheck ||
                                  item.raw.transaction.id < 0 ||
                                  item.raw.transaction.attachments
                                "
                                ><v-col
                                  class="d-flex justify-center align-center"
                                  ><div v-if="item.raw.transaction.checkNumber">
                                    <v-icon
                                      icon="mdi-checkbook"
                                      color="amber"
                                    ></v-icon
                                    ><span
                                      :class="
                                        item.raw.transaction.status.id == 1
                                          ? 'font-italic text-grey'
                                          : 'font-weight-bold text-black'
                                      "
                                      >#{{
                                        item.raw.transaction.checkNumber
                                      }}</span
                                    >
                                  </div>
                                  <div v-if="item.raw.transaction.paycheck">
                                    <v-icon
                                      icon="mdi-cash-multiple"
                                      color="amber"
                                    ></v-icon>
                                  </div>
                                  <div v-if="item.raw.transaction.id < 0">
                                    <v-icon
                                      icon="mdi-bell"
                                      color="amber"
                                    ></v-icon>
                                  </div>
                                  <div v-if="item.raw.transaction.attachments">
                                    <v-icon
                                      icon="mdi-paperclip"
                                      color="amber"
                                    ></v-icon></div></v-col></v-row></v-container></v-col
                          ><v-col
                            cols="1"
                            class="d-flex justify-center align-center"
                            ><v-icon
                              :icon="
                                !showMore[i]
                                  ? 'mdi-chevron-down'
                                  : 'mdi-chevron-up'
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
                                        item.raw.transaction.status.id == 1
                                          ? 'font-italic text-grey text-body-2'
                                          : 'font-weight-bold text-black text-body-2'
                                      "
                                    >
                                      {{ item.raw.transaction.memo }}
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
          </v-card-text>
        </v-card>
        <v-skeleton-loader type="card" v-else></v-skeleton-loader>
      </v-col>
    </v-row>
  </div>
</template>
<script setup>
import { defineProps, ref, computed } from "vue";
import { useGraphTransactions } from "@/composables/tagsComposable";
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from "chart.js";
import { Bar } from "vue-chartjs";
import annotationPlugin from "chartjs-plugin-annotation";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  annotationPlugin,
);

const showMore = ref({});
const props = defineProps({
  tagID: {
    type: Number,
  },
});

const { tag_transactions, isLoading } = useGraphTransactions(props.tagID);
const this_year_avg = computed(() =>
  tag_transactions.value.year1_avg ? tag_transactions.value.year1_avg : 0,
);
const show_year1 = computed(() =>
  tag_transactions.value.year1_avg !== 0 ? true : false,
);
const last_year_avg = computed(() =>
  tag_transactions.value.year2_avg ? tag_transactions.value.year2_avg : 0,
);
const show_year2 = computed(() =>
  tag_transactions.value.year2_avg !== 0 ? true : false,
);
const options = ref({
  responsive: true,
  maintainAspectRatio: true,
  aspectRatio: "1",
  plugins: {
    annotation: {
      annotations: [
        {
          type: "line",
          display: show_year1,
          mode: "horizontal",
          scaleID: "y",
          value: this_year_avg,
          borderColor: "#034a45",
          borderWidth: 1,
          borderDash: [3, 3],
        },
        {
          type: "line",
          display: show_year2,
          mode: "horizontal",
          scaleID: "y",
          value: last_year_avg,
          borderColor: "#88b3b0",
          borderWidth: 1,
          borderDash: [3, 3],
        },
      ],
    },
    tooltip: {
      enabled: true,
      callbacks: {
        label: function (context) {
          let label = context.dataset.label || "";
          if (label) {
            label += ": ";
          }
          if (context.parsed.y !== null) {
            label += new Intl.NumberFormat("en-US", {
              style: "currency",
              currency: "USD",
            }).format(context.parsed.y);
          }
          return label;
        },
      },
    },
  },
  scales: {
    y: {
      ticks: {
        // Include a dollar sign in the ticks
        callback: function (value) {
          return "$" + value;
        },
      },
    },
  },
});

const toggleMore = index => {
  showMore.value[index] = !showMore.value[index];
};

const formatCurrency = value => {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
};

const getClassForMoneyBalance = (amount, status) => {
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

  return color + " " + font + " text-subtitle-2";
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
</style>
