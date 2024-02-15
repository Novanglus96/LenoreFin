<template>
  <v-card>
    <v-card-title>Log Entries</v-card-title>
    <vue3-datatable
      :rows="log_entries"
      :columns="columns"
      :loading="isLoading"
      :totalRows="log_entries ? log_entries.length : 0"
      :isServerMode="false"
      pageSize="20"
      :stickyHeader="true"
      noDataContent="No Log Entries"
      search=""
      ref="log_table"
      height="810px"
      skin="bh-table-striped bh-table-compact"
      :pageSizeOptions="[20]"
      :showPageSize="false"
      paginationInfo="Showing {0} to {1} of {2} log entries"
      class="alt-pagination"
    >
      <template #error_level="row"
        ><!-- eslint-disable-line -->
        <v-btn v-if="row.value.error_level.id == 0" variant="plain">
          <v-icon icon="mdi-bug" color="blue"></v-icon>
          <v-tooltip
            :text="row.value.error_level.error_level"
            activator="parent"
            location="end"
          ></v-tooltip>
        </v-btn>
        <v-btn v-if="row.value.error_level.id == 1" variant="plain">
          <v-icon icon="mdi-information" color="grey"></v-icon>
          <v-tooltip
            :text="row.value.error_level.error_level"
            activator="parent"
            location="end"
          ></v-tooltip>
        </v-btn>
        <v-btn v-if="row.value.error_level.id == 2" variant="plain">
          <v-icon icon="mdi-alert" color="warning"></v-icon>
          <v-tooltip
            :text="row.value.error_level.error_level"
            activator="parent"
            location="end"
          ></v-tooltip>
        </v-btn>
        <v-btn v-if="row.value.error_level.id == 3" variant="plain">
          <v-icon icon="mdi-alert" color="error"></v-icon>
          <v-tooltip
            :text="row.value.error_level.error_level"
            activator="parent"
            location="end"
          ></v-tooltip>
        </v-btn>
      </template>
    </vue3-datatable>
  </v-card>
</template>
<script setup>
import Vue3Datatable from "@bhplugin/vue3-datatable";
import "@bhplugin/vue3-datatable/dist/style.css";
import { useLogEntries } from "@/composables/logentriesComposable";
import { ref } from "vue";

const { log_entries, isLoading } = useLogEntries();

const columns = ref([
  { field: "log_date", title: "Date", width: "120px" },
  { field: "error_level", title: "Level", width: "50px" },
  { field: "log_entry", title: "Entry" },
  { field: "error_num", title: "Error #", type: "number", width: "100px" },
  { field: "account.account_name", title: "Account" },
  { field: "reminder.description", title: "Reminder" },
  { field: "transaction.description", title: "Transaction" },
]);
</script>
