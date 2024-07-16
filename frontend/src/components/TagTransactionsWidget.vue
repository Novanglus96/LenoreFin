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
                    >{{ tag_transactions.year1 }} Avg: ${{
                      tag_transactions.year1_avg
                    }}</span
                  ></v-col
                >
                <v-col class="text-left"
                  ><span class="text-subtitle-2"
                    >{{ tag_transactions.year2 }} Avg: ${{
                      tag_transactions.year2_avg
                    }}</span
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
            <vue3-datatable
              :rows="tag_transactions.transactions"
              :columns="columns"
              :loading="isLoading"
              :totalRows="
                tag_transactions.transactions
                  ? tag_transactions.transactions.length
                  : 0
              "
              :isServerMode="false"
              pageSize="10"
              :hasCheckbox="false"
              :stickyHeader="true"
              noDataContent="No transactions"
              ref="tag_trans_table"
              height="405px"
              skin="bh-table-striped bh-table-compact"
              :pageSizeOptions="[10]"
              :showPageSize="false"
              paginationInfo="Showing {0} to {1} of {2} transactions"
              class="alt-pagination"
              ><!--height="280px"-->
              <template #transaction_date="row">
                {{ row.value.transaction_date }}
              </template>
              <template #transaction.total_amount="row">
                <span
                  :class="
                    row.value.transaction.total_amount < 0
                      ? 'text-red'
                      : 'text-green'
                  "
                  >${{ row.value.transaction.total_amount }}</span
                >
              </template>
              <template #detail_amt="row">
                <span
                  :class="row.value.detail_amt < 0 ? 'text-red' : 'text-green'"
                  >${{ row.value.detail_amt }}</span
                >
              </template>
              <template #description="row">
                {{ row.value.description }}
              </template>
              <template #memo="row">
                {{ row.memo }}
              </template>
              <template #pretty_account="row">
                {{ row.value.pretty_account }}
              </template>
            </vue3-datatable>
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
import Vue3Datatable from "@bhplugin/vue3-datatable";
import "@bhplugin/vue3-datatable/dist/style.css";
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

const props = defineProps({
  tagID: {
    type: Number,
  },
});

const columns = ref([
  {
    field: "transaction.transaction_date",
    title: "Date",
    type: "date",
    width: "120px",
  },
  {
    field: "transaction.total_amount",
    title: "Trans Amount",
    type: "number",
    width: "100px",
  },
  { field: "detail_amt", title: "Tag Amount", type: "number", width: "100px" },
  { field: "transaction.description", title: "Description" },
  { field: "transaction.memo", title: "Memo" },
  { field: "pretty_account", title: "Account" },
]);
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
  aspectRatio: "5",
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
