<template>
    <v-card
        variant="outlined"
        :elevation="4"
        class="bg-white"
    >
        <template v-slot:append>
            <v-menu location="start">
                <template v-slot:activator="{ props }">
                    <v-btn
                    icon="mdi-cog"
                    flat
                    size="xs"
                    v-bind="props"
                    >
                    </v-btn>
                </template>
                <v-card width="100">
                    <v-card-text>Test</v-card-text>
                </v-card>
            </v-menu>
        </template>
        <template v-slot:title>
            <span class="text-subtitle-2 text-accent">Upcoming Reminders</span>
        </template>
        <template v-slot:text>
            <vue3-datatable 
                :rows="items"
                :columns="columns"
                :loading="isLoading"
                :totalRows="items.length"
                :isServerMode="false"
                pageSize="5"
                :hasCheckbox="false"
                :stickyHeader="true"
                noDataContent="No reminders"
                ref="reminders_table"
                height="220px"
                skin="bh-table-striped bh-table-compact"
                :pageSizeOptions="[5]"
                :showPageSize="false"
                paginationInfo="Showing {0} to {1} of {2} reminders"
                class="alt-pagination"
            ><!--height="280px"-->
                <template #date="row"><!-- eslint-disable-line -->
                    <span class="font-weight-bold text-black">{{ row.value.date }}</span>
                </template>
                <template #amount="row"><!-- eslint-disable-line -->
                    <span :class="getClassForMoney(row.value.amount)">${{ row.value.amount }}</span>
                </template>
                <template #reminder="row"><!-- eslint-disable-line -->
                    <span class="font-weight-bold text-black">{{ row.value.reminder }}</span>
                </template>
            </vue3-datatable>
        </template>
    </v-card>
</template>
<script setup>
import { useMainStore } from '@/stores/main'
import Vue3Datatable from '@bhplugin/vue3-datatable'
import '@bhplugin/vue3-datatable/dist/style.css'
import { ref } from 'vue'

const mainstore = useMainStore()

const columns = ref([
    { field: 'date', title: 'Date', type: 'date', width: '120px' },
    { field: 'amount', title: 'Amount', type: 'number', width: '100px' },
    { field: 'reminder', title: 'Reminder' },
])
const getClassForMoney = (amount) => {
    let color = ''
    let font = ''

    font = "font-weight-bold"
    if (amount < 0) {
        color = 'text-red'
    } else {
        color = 'text-green'
    }

    return color + ' ' + font
}
const items = mainstore.reminder_items // Data point for data
</script>
<style>
.alt-pagination .bh-pagination .bh-page-item {
       background-color: #06966A;
       color: white;
}
</style>