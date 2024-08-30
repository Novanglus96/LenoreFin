<template>
  <v-card variant="outlined" :elevation="4" class="bg-white">
    <template v-slot:append>
      <v-tooltip text="Add Rule" location="top">
        <template v-slot:activator="{ props }">
          <v-btn
            icon="mdi-table-plus"
            flat
            variant="plain"
            v-bind="props"
            @click="importFileDialog = true"
          ></v-btn>
        </template>
      </v-tooltip>
    </template>
    <template v-slot:title>
      <span class="text-subtitle-2 text-secondary">Rules</span>
    </template>
    <template v-slot:text>
      <vue3-datatable
        :rows="calculator_rules ? calculator_rules : []"
        :columns="columns"
        :loading="isLoading"
        :totalRows="calculator_rules ? calculator_rules.length : 0"
        :isServerMode="false"
        pageSize="10"
        :hasCheckbox="false"
        :stickyHeader="true"
        firstArrow="First"
        lastArrow="Last"
        previousArrow="Prev"
        nextArrow="Next"
        :showNumbersCount="3"
        noDataContent="No rules"
        search=""
        ref="rules_table"
        height="650px"
        :pageSizeOptions="[60]"
        :showPageSize="false"
        paginationInfo="Showing {0} to {1} of {2} rules"
        @change="pageChanged"
        class="alt-pagination"
        rowClass="cursor-pointer"
        @rowClick="rowClick"
      >
        <template #rule_total="data">
          <span>${{ data.value.rule_total }}</span>
        </template>
        <template #actions="data">
          <div>
            <v-btn
              icon="mdi-delete"
              flat
              variant="plain"
              @click="deleteRule(data.value.id)"
            ></v-btn>
          </div>
        </template> </vue3-datatable
    ></template>
  </v-card>
</template>
<script setup>
import { ref } from "vue";
import Vue3Datatable from "@bhplugin/vue3-datatable";
import "@bhplugin/vue3-datatable/dist/style.css";

const columns = ref([
  { field: "id", title: "ID", isUnique: true, hide: true },
  { field: "rule_name", title: "Rule Name" },
  { field: "rule_total", title: "Total", type: "number", width: "100px" },
  { field: "actions", title: "Actions", width: "100px" },
]);

const calculator_rules = ref([
  {
    id: 1,
    rule_name: "Test",
    rule_total: 100,
  },
  {
    id: 2,
    rule_name: "Test #2",
    rule_total: 200,
  },
  {
    id: 3,
    rule_name: "Test #3",
    rule_total: 300,
  },
  {
    id: 4,
    rule_name: "Test #4",
    rule_total: 400,
  },
]);
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
