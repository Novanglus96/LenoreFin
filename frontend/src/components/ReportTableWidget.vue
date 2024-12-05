<template>
  <div>
    <v-row class="pa-1 ga-1 rounded" no-gutters>
      <v-col class="rounded">
        <v-card>
          <v-card-title>{{ props.data[0].year1 }}</v-card-title>
          <v-card-text>
            <v-container>
              <v-row dense>
                <v-col
                  ><vue3-datatable
                    :rows="local_data ? local_data : []"
                    :columns="columns"
                    :loading="props.isLoading"
                    :totalRows="local_data ? local_data.length : 0"
                    :isServerMode="true"
                    :pageSize="14"
                    :hasCheckbox="false"
                    firstArrow="First"
                    lastArrow="Last"
                    previousArrow="Prev"
                    nextArrow="Next"
                    :showNumbersCount="3"
                    noDataContent="No data"
                    ref="pay_table"
                    :pageSizeOptions="[14]"
                    :showPageSize="false"
                    :pagination="false"
                    :stickyFirstColumn="true"
                  >
                  </vue3-datatable></v-col
              ></v-row>
            </v-container>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>
<script setup>
import { ref, computed, defineProps } from "vue";
import Vue3Datatable from "@bhplugin/vue3-datatable";
import "@bhplugin/vue3-datatable/dist/style.css";

const props = defineProps({
  isLoading: Boolean,
  data: Array,
});

const local_data = computed(() => {
  let formatted_data = [];
  let totals = [];

  props.data.forEach(() => {
    totals.push(0);
  });

  const currentMonth = new Date().getMonth() + 1;
  props.data.forEach((row, index) => {
    const new_object = {};
    new_object.id = index;
    new_object.item = row.pretty_name;
    let total = 0;
    for (let i = 0; i <= 11; i++) {
      const date = new Date();
      date.setMonth(i);
      const monthname = date.toLocaleString("en-US", { month: "short" });
      const lower_monthname = monthname.toLowerCase();
      new_object[lower_monthname] = formatToUSD(
        parseFloat(row.data.datasets[0].data[i]),
      );
      total += parseFloat(row.data.datasets[0].data[i]);
    }
    new_object.ytd = formatToUSD(total);
    new_object.avg = formatToUSD(total / currentMonth);
    formatted_data.push(new_object);
  });

  return formatted_data;
});
const columns = ref([
  {
    field: "item",
    title: "",
    cellClass: "bg-secondary text-right font-weight-bold text-caption",
    headerClass: "text-right",
  },
  {
    field: "jan",
    title: "Jan",
    cellClass: "text-center text-caption",
    headerClass: "text-center",
  },
  {
    field: "feb",
    title: "Feb",
    cellClass: "text-center text-caption",
    headerClass: "text-center",
  },
  {
    field: "mar",
    title: "Mar",
    cellClass: "text-center text-caption",
    headerClass: "text-center",
  },
  {
    field: "apr",
    title: "Apr",
    cellClass: "text-center text-caption",
    headerClass: "text-center",
  },
  {
    field: "may",
    title: "May",
    cellClass: "text-center text-caption",
    headerClass: "text-center",
  },
  {
    field: "jun",
    title: "Jun",
    cellClass: "text-center text-caption",
    headerClass: "text-center",
  },
  {
    field: "jul",
    title: "Jul",
    cellClass: "text-center text-caption",
    headerClass: "text-center",
  },
  {
    field: "aug",
    title: "Aug",
    cellClass: "text-center text-caption",
    headerClass: "text-center",
  },
  {
    field: "sep",
    title: "Sep",
    cellClass: "text-center text-caption",
    headerClass: "text-center",
  },
  {
    field: "oct",
    title: "Oct",
    cellClass: "text-center text-caption",
    headerClass: "text-center",
  },
  {
    field: "nov",
    title: "Nov",
    cellClass: "text-center text-caption",
    headerClass: "text-center",
  },
  {
    field: "dec",
    title: "Dec",
    cellClass: "text-center text-caption",
    headerClass: "text-center",
  },
  {
    field: "ytd",
    title: "YTD",
    cellClass: "text-center font-weight-bold text-secondary text-caption",
    headerClass: "text-center",
  },
  {
    field: "avg",
    title: "AVG",
    cellClass: "text-center font-weight-bold text-accent text-caption",
    headerClass: "text-center",
  },
  { field: "id", title: "ID", isUnique: true, hide: true },
]);

const formatToUSD = amount => {
  return amount.toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  });
};
</script>
