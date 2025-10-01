<template>
  <v-card variant="outlined" :elevation="4" class="bg-surface">
    <v-card-title class="text-left">
      <span class="text-subtitle-2 text-secondary">
        {{ calculator ? calculator.rule.name : null }} Transactions
      </span>
    </v-card-title>
    <v-card-text class="ma-0 pa-0 ga-0">
      <v-data-table
        :headers="displayHeaders"
        :items="calculator ? calculator.transactions : []"
        :items-length="calculator ? calculator.transactions.length : 0"
        :loading="calculator_isLoading"
        item-value="id"
        v-model:items-per-page="itemsPerPage"
        :items-per-page-options="[
          {
            value: 10,
            title: 10,
          },
        ]"
        items-per-page-text="Transactions per page"
        no-data-text="No transactions!"
        loading-text="Loading transactions..."
        disable-sort
        :show-select="true"
        fixed-footer
        striped="odd"
        density="compact"
        width="100%"
        return-object
        v-model="selected"
        select-strategy="all"
        v-model:page="page"
        :header-props="{ class: 'font-weight-bold bg-primary' }"
        :row-props="{ class: 'text-body-2' }"
        v-if="props.ruleID"
      >
        <template
          v-slot:item.data-table-select="{
            internalItem,
            isSelected,
            toggleSelect,
          }"
        >
          <v-checkbox-btn
            :model-value="isSelected(internalItem)"
            color="secondary"
            @update:model-value="toggleSelect(internalItem)"
            :disabled="!isSelectable(internalItem.raw)"
          ></v-checkbox-btn>
        </template>
        <template v-slot:bottom>
          <div class="text-center pt-2">
            <v-pagination v-model="page" :length="pageCount"></v-pagination>
          </div>
        </template>
        <template v-slot:[`header.transaction_date`] v-if="mdAndUp">
          <div class="text-center">Date</div>
        </template>
        <template v-slot:[`header.pretty_total`] v-if="mdAndUp">
          <div class="text-center">Total</div>
        </template>
        <template v-slot:[`header.details`] v-if="mdAndUp">
          <div class="text-center">Tag Amounts</div>
        </template>
        <template v-slot:[`item.transaction_date`]="{ item }" v-if="mdAndUp">
          <div class="text-center">
            {{ formatDate(item.transaction_date, true) }}
          </div>
        </template>
        <template v-slot:[`item.pretty_total`]="{ item }" v-if="mdAndUp">
          <div class="text-center">
            <span :class="getClassForMoney(item.pretty_total)">
              {{ formatCurrency(item.pretty_total) }}
            </span>
          </div>
        </template>
        <template v-slot:[`item.details`]="{ item }" v-if="mdAndUp">
          <div class="text-center text-subtitle-2">
            <span v-for="detail in item.details" :key="detail">
              <v-icon
                icon="mdi-tag"
                size="x-small"
                :color="item.status.id == 1 ? 'grey' : 'black'"
                v-if="detail"
              ></v-icon>
              {{ detail.tag.tag_name }} :
              <span
                :class="getClassForMoney(detail.detail_amt, item.status.id)"
              >
                {{ formatCurrency(detail.detail_amt) }}
              </span>
              <br />
            </span>
          </div>
        </template>
        <!-- Mobile View -->
        <template v-slot:[`item.mobile`]="{ item }">
          <v-container class="ma-0 pa-0 ga-0">
            <v-row dense class="ma-0 pa-0 ga-0">
              <v-col class="ma-0 pa-0 ga-0 text-left">
                {{ formatDate(item.transaction_date, true) }}
              </v-col>
              <v-col class="ma-0 pa-0 ga-0 text-right">
                <span :class="getClassForMoney(item.pretty_total)">
                  {{ formatCurrency(item.pretty_total) }}
                </span>
              </v-col>
            </v-row>
            <v-row dense class="ma-0 pa-0 ga-0">
              <v-col class="ma-0 pa-0 ga-0 font-weight-bold">
                {{ item.description }}
              </v-col>
            </v-row>
            <v-row dense class="ma-0 pa-0 ga-0">
              <v-col
                class="ma-0 pa-0 ga-0 text-secondary text-left text-truncate"
              >
                <span>
                  {{ item.pretty_account }}
                </span>
              </v-col>
            </v-row>
            <v-row dense class="ma-0 pa-0 ga-0">
              <v-col class="ma-0 pa-0 ga-0">
                <div class="text-center text-subtitle-2">
                  <span v-for="detail in item.details" :key="detail">
                    <v-icon
                      icon="mdi-tag"
                      size="x-small"
                      :color="item.status.id == 1 ? 'grey' : 'black'"
                      v-if="detail"
                    ></v-icon>
                    {{ detail.tag.tag_name }} :
                    <span
                      :class="
                        getClassForMoney(detail.detail_amt, item.status.id)
                      "
                    >
                      {{ formatCurrency(detail.detail_amt) }}
                    </span>
                    &nbsp;
                  </span>
                </div>
              </v-col>
            </v-row>
          </v-container>
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>
<script setup>
  import { ref, defineProps, watch, computed } from "vue";
  import { useCalculator } from "@/composables/calculatorComposable";
  import { usePlanningStore } from "@/stores/planning";
  import { useDisplay } from "vuetify";

  const { mdAndUp } = useDisplay();

  const planningstore = usePlanningStore();
  const props = defineProps({
    ruleID: {
      type: Number,
    },
    timeframe: {
      type: Number,
    },
  });

  const local_rule_id = ref(props.ruleID);
  const local_timeframe = ref(props.timeframe);
  const selected = ref([]);

  const { calculator, isLoading: calculator_isLoading } = useCalculator(
    local_rule_id.value,
    local_timeframe.value,
  );
  const page = ref(1);
  const itemsPerPage = ref(10);
  const pageCount = computed(() =>
    calculator.value && itemsPerPage.value
      ? Math.ceil(calculator.value.transactions.length / itemsPerPage.value)
      : 1,
  );

  const headers = ref([
    { title: "Date", key: "transaction_date", width: "80px" },
    { title: "Total", key: "pretty_total", width: "100px" },
    { title: "Tag Amounts", key: "details", width: "160px" },
    { title: "Description", key: "description" },
    { title: "Account", key: "pretty_account" },
  ]);
  const displayHeaders = computed(() => {
    if (mdAndUp.value) {
      return headers.value;
    }
    // For small screens, use your single mobile column
    return [{ title: "", key: "mobile" }];
  });

  watch(
    () => selected.value,
    val => {
      if (val) {
        planningstore.calculator.selected_transactions = val;
      } else {
        planningstore.calculator.selected_transactions = [];
      }
    },
  );

  const getClassForMoney = (amount, status) => {
    let color = "";

    if (status == 1) {
      if (amount < 0) {
        color = "text-red-lighten-1";
      } else {
        color = "text-green-lighten-1";
      }
    } else {
      if (amount < 0) {
        color = "text-red";
      } else {
        color = "text-green";
      }
    }

    return color;
  };
  watch(props.ruleID, newValue => {
    local_rule_id.value = newValue;
  });
  watch(props.timeframe, newValue => {
    local_timeframe.value = newValue;
  });
  const formatCurrency = value => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };
  const isSelectable = item => item;

  const formatDate = (input, padDay = false) => {
    // Normalize input to a Date object
    const date = input instanceof Date ? input : new Date(input);

    if (isNaN(date)) {
      console.warn("Invalid date:", input);
      return "";
    }

    const month = date.toLocaleString("en-US", { month: "short" }); // 'Sep'
    const day = date.getDate(); // 16

    return `${month}-${padDay ? String(day).padStart(2, "0") : day}`;
  };
</script>
