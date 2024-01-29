<template>
    <div>
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
            class="alt-pagination">

        </vue3-datatable>
    </div>
</template>
<script setup>
import Vue3Datatable from '@bhplugin/vue3-datatable'
import '@bhplugin/vue3-datatable/dist/style.css'
import { useLogEntries } from '@/composables/logentriesComposable'
import { ref } from 'vue'

const { log_entries, isLoading } = useLogEntries()

const columns = ref([
    { field: 'log_date', title: 'Date', width: '120px' },
    { field: 'error_num', title: 'Error #', type: 'number', width: '100px' },
    { field: 'log_entry', title: 'Entry' },
    { field: 'account.account_name', title: 'Account' },
    { field: 'reminder.description', title: 'Reminder' },
    { field: 'transaction.description', title: 'Transaction' },
    { field: 'error_level.error_level', title: 'Level' },
])
</script>