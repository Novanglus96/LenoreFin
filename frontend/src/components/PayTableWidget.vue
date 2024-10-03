<template>
  <div>
    <v-row class="pa-1 ga-1 rounded" no-gutters>
      <v-col class="rounded">
        <v-card>
          <v-card-title>2024</v-card-title>
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
                    :stickyHeader="true"
                    firstArrow="First"
                    lastArrow="Last"
                    previousArrow="Prev"
                    nextArrow="Next"
                    :showNumbersCount="3"
                    noDataContent="No data"
                    @rowSelect="rowSelected"
                    ref="pay_table"
                    height="600px"
                    :pageSizeOptions="[14]"
                    :showPageSize="false"
                    @change="pageChanged"
                    :pagination="false"
                    skin="bh-table-striped bh-table-hover bh-table-bordered bh-table-compact"
                  >
                    <template #month="row"
                      ><span class="font-weight-bold">{{
                        row.value.month
                      }}</span></template
                    >
                    <template #gross="row"
                      ><span
                        v-if="row.value.month === 'YTD'"
                        class="font-weight-bold text-secondary"
                        >{{ row.value.gross }}</span
                      >
                      <span
                        v-if="row.value.month === 'AVG'"
                        class="font-weight-bold text-accent"
                        >{{ row.value.gross }}</span
                      >
                      <span
                        v-if="
                          row.value.month != 'YTD' && row.value.month != 'AVG'
                        "
                        >{{ row.value.gross }}</span
                      >
                    </template>
                    <template #net="row"
                      ><span
                        v-if="row.value.month === 'YTD'"
                        class="font-weight-bold text-secondary"
                        >{{ row.value.net }}</span
                      >
                      <span
                        v-if="row.value.month === 'AVG'"
                        class="font-weight-bold text-accent"
                        >{{ row.value.net }}</span
                      >
                      <span
                        v-if="
                          row.value.month != 'YTD' && row.value.month != 'AVG'
                        "
                        >{{ row.value.net }}</span
                      >
                    </template>
                    <template #taxes="row"
                      ><span
                        v-if="row.value.month === 'YTD'"
                        class="font-weight-bold text-secondary"
                        >{{ row.value.taxes }}</span
                      >
                      <span
                        v-if="row.value.month === 'AVG'"
                        class="font-weight-bold text-accent"
                        >{{ row.value.taxes }}</span
                      >
                      <span
                        v-if="
                          row.value.month != 'YTD' && row.value.month != 'AVG'
                        "
                        >{{ row.value.taxes }}</span
                      >
                    </template>
                    <template #health="row"
                      ><span
                        v-if="row.value.month === 'YTD'"
                        class="font-weight-bold text-secondary"
                        >{{ row.value.health }}</span
                      >
                      <span
                        v-if="row.value.month === 'AVG'"
                        class="font-weight-bold text-accent"
                        >{{ row.value.health }}</span
                      >
                      <span
                        v-if="
                          row.value.month != 'YTD' && row.value.month != 'AVG'
                        "
                        >{{ row.value.health }}</span
                      >
                    </template>
                    <template #pension="row"
                      ><span
                        v-if="row.value.month === 'YTD'"
                        class="font-weight-bold text-secondary"
                        >{{ row.value.pension }}</span
                      >
                      <span
                        v-if="row.value.month === 'AVG'"
                        class="font-weight-bold text-accent"
                        >{{ row.value.pension }}</span
                      >
                      <span
                        v-if="
                          row.value.month != 'YTD' && row.value.month != 'AVG'
                        "
                        >{{ row.value.pension }}</span
                      >
                    </template>
                    <template #fsa="row"
                      ><span
                        v-if="row.value.month === 'YTD'"
                        class="font-weight-bold text-secondary"
                        >{{ row.value.fsa }}</span
                      >
                      <span
                        v-if="row.value.month === 'AVG'"
                        class="font-weight-bold text-accent"
                        >{{ row.value.fsa }}</span
                      >
                      <span
                        v-if="
                          row.value.month != 'YTD' && row.value.month != 'AVG'
                        "
                        >{{ row.value.fsa }}</span
                      >
                    </template>
                    <template #dca="row"
                      ><span
                        v-if="row.value.month === 'YTD'"
                        class="font-weight-bold text-secondary"
                        >{{ row.value.dca }}</span
                      >
                      <span
                        v-if="row.value.month === 'AVG'"
                        class="font-weight-bold text-accent"
                        >{{ row.value.dca }}</span
                      >
                      <span
                        v-if="
                          row.value.month != 'YTD' && row.value.month != 'AVG'
                        "
                        >{{ row.value.dca }}</span
                      >
                    </template>
                    <template #union="row"
                      ><span
                        v-if="row.value.month === 'YTD'"
                        class="font-weight-bold text-secondary"
                        >{{ row.value.union }}</span
                      >
                      <span
                        v-if="row.value.month === 'AVG'"
                        class="font-weight-bold text-accent"
                        >{{ row.value.union }}</span
                      >
                      <span
                        v-if="
                          row.value.month != 'YTD' && row.value.month != 'AVG'
                        "
                        >{{ row.value.union }}</span
                      >
                    </template>
                    <template #fourfiftysevenb="row"
                      ><span
                        v-if="row.value.month === 'YTD'"
                        class="font-weight-bold text-secondary"
                        >{{ row.value.fourfiftysevenb }}</span
                      >
                      <span
                        v-if="row.value.month === 'AVG'"
                        class="font-weight-bold text-accent"
                        >{{ row.value.fourfiftysevenb }}</span
                      >
                      <span
                        v-if="
                          row.value.month != 'YTD' && row.value.month != 'AVG'
                        "
                        >{{ row.value.fourfiftysevenb }}</span
                      >
                    </template></vue3-datatable
                  ></v-col
                ></v-row
              >
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
  data: Object,
});

const local_data = computed(() => {
  let formatted_data = [];
  let gross_total = 0;
  let net_total = 0;
  let taxes_total = 0;
  let health_total = 0;
  let pension_total = 0;
  let fsa_total = 0;
  let dca_total = 0;
  let union_total = 0;
  let fourfiftysevenb_total = 0;
  const currentMonth = new Date().getMonth() + 1;
  for (let i = 0; i <= 11; i++) {
    const date = new Date();
    date.setMonth(i);
    const monthname = date.toLocaleString("en-US", { month: "short" });
    gross_total += parseFloat(props.data.gross.data.datasets[0].data[i]);
    net_total += parseFloat(props.data.net.data.datasets[0].data[i]);
    taxes_total += parseFloat(props.data.taxes.data.datasets[0].data[i]);
    health_total += parseFloat(props.data.health.data.datasets[0].data[i]);
    pension_total += parseFloat(props.data.pension.data.datasets[0].data[i]);
    fsa_total += parseFloat(props.data.fsa.data.datasets[0].data[i]);
    dca_total += parseFloat(props.data.dca.data.datasets[0].data[i]);
    union_total += parseFloat(props.data.union.data.datasets[0].data[i]);
    fourfiftysevenb_total += parseFloat(
      props.data.fourfiftysevenb.data.datasets[0].data[i],
    );

    const empty_object = {
      id: i,
      month: monthname,
      gross: formatToUSD(parseFloat(props.data.gross.data.datasets[0].data[i])),
      net: formatToUSD(parseFloat(props.data.net.data.datasets[0].data[i])),
      taxes: formatToUSD(parseFloat(props.data.taxes.data.datasets[0].data[i])),
      health: formatToUSD(
        parseFloat(props.data.health.data.datasets[0].data[i]),
      ),
      pension: formatToUSD(
        parseFloat(props.data.pension.data.datasets[0].data[i]),
      ),
      fsa: formatToUSD(parseFloat(props.data.fsa.data.datasets[0].data[i])),
      dca: formatToUSD(parseFloat(props.data.dca.data.datasets[0].data[i])),
      union: formatToUSD(parseFloat(props.data.union.data.datasets[0].data[i])),
      fourfiftysevenb: formatToUSD(
        parseFloat(props.data.fourfiftysevenb.data.datasets[0].data[i]),
      ),
    };
    formatted_data.push(empty_object);
  }
  const total_object = {
    id: 13,
    month: "YTD",
    gross: formatToUSD(gross_total),
    net: formatToUSD(net_total),
    taxes: formatToUSD(taxes_total),
    health: formatToUSD(health_total),
    pension: formatToUSD(pension_total),
    fsa: formatToUSD(fsa_total),
    dca: formatToUSD(dca_total),
    union: formatToUSD(union_total),
    fourfiftysevenb: formatToUSD(fourfiftysevenb_total),
  };
  formatted_data.push(total_object);
  const avg_object = {
    id: 14,
    month: "AVG",
    gross: formatToUSD(gross_total / currentMonth),
    net: formatToUSD(net_total / currentMonth),
    taxes: formatToUSD(taxes_total / currentMonth),
    health: formatToUSD(health_total / currentMonth),
    pension: formatToUSD(pension_total / currentMonth),
    fsa: formatToUSD(fsa_total / currentMonth),
    dca: formatToUSD(dca_total / currentMonth),
    union: formatToUSD(union_total / currentMonth),
    fourfiftysevenb: formatToUSD(fourfiftysevenb_total / currentMonth),
  };
  formatted_data.push(avg_object);
  return formatted_data;
});
const columns = ref([
  { field: "id", title: "ID", isUnique: true, hide: true },
  { field: "month", title: "Mth", cellClass: "bg-secondary text-right" },
  {
    field: "gross",
    title: "Gross",
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    field: "net",
    title: "Net",
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    field: "taxes",
    title: "Taxes",
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    field: "health",
    title: "Health",
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    field: "pension",
    title: "Pension",
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    field: "fsa",
    title: "FSA",
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    field: "dca",
    title: "DCA",
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    field: "union",
    title: "Union Dues",
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    field: "fourfiftysevenb",
    title: "457B",
    cellClass: "text-center",
    headerClass: "text-center",
  },
]);

const formatToUSD = amount => {
  return amount.toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};
</script>
