<template>
    <v-card variant="outlined" :elevation="4" class="bg-white">
        <template v-slot:append>
            <v-menu location="start">
                <template v-slot:activator="{ props }">
                    <v-btn icon="mdi-cog" flat size="xs" v-bind="props">
                    </v-btn>
                </template>
                <v-card width="100">
                    <v-card-text>Test</v-card-text>
                </v-card>
            </v-menu>
        </template>
        <template v-slot:title>
            <span class="text-subtitle-2 text-accent">Transactions</span>
        </template>
        <template v-slot:text>
            <v-btn icon="mdi-invoice-text-check" flat :disabled="selected.length === 0" variant="plain"></v-btn>
            <v-btn icon="mdi-invoice-text-edit" flat :disabled="selected.length === 0 || selected.length > 1" variant="plain"></v-btn>
            <v-btn icon="mdi-invoice-remove" flat :disabled="selected.length === 0" variant="plain" color="error"></v-btn>
            <v-btn icon="mdi-invoice-plus" flat variant="plain" color="success"></v-btn>
            <v-data-table
                :loading="isLoading"
                :headers="headers"
                :items="items"
                density="compact"
                items-per-page="20"
                no-filter
                show-select
                v-model="selected"
                item-value="id">
                <template v-slot:item.amount="{ value }"><!-- eslint-disable-line -->
                    <span :class="value >= 0 ? 'text-green' : 'text-red'">${{ value }}</span>
                </template>
                <template v-slot:item.balance="{ value }"><!-- eslint-disable-line -->
                    <span :class="value >= 0 ? 'text-green' : 'text-red'">${{ value }}</span>
                </template>
                <template v-slot:item.status="{ value }"><!-- eslint-disable-line -->
                    <v-icon icon="mdi-cash" :color="value == 'Pending' ? 'grey' : 'green'"></v-icon>
                </template>
                <template v-slot:item.tag="{ value }"><!-- eslint-disable-line -->
                    <v-icon icon="mdi-tag"></v-icon> {{ value }}
                </template>
                <template v-slot:loading>
                    <v-skeleton-loader type="table-row@20"></v-skeleton-loader>
                </template>
            </v-data-table>
        </template>
    </v-card>
</template>
<script setup>
import { useMainStore } from '@/stores/main'
import { ref } from 'vue'

const selected = ref([])
const mainstore = useMainStore()
const headers = [
    {
        title: 'Status',
        align: 'center',
        key: 'status',
        sortable: false,
        removable: false,
    },
    {
        title: 'Date',
        align: 'center',
        key: 'date',
        sortable: false,
        removable: false,
    },
    {
        title: 'Amount',
        align: 'center',
        key: 'amount',
        sortable: false,
        removable: false,
    },
    {
        title: 'Balance',
        align: 'center',
        key: 'balance',
        sortable: false,
        removable: false,
    },
    {
        title: 'Description',
        align: 'start',
        key: 'description',
        sortable: false,
        removable: false,
    },
    {
        title: 'Tag',
        align: 'start',
        key: 'tag',
        sortable: false,
        removable: false,
    },
    {
        title: 'Account',
        align: 'start',
        key: 'account',
        sortable: false,
        removable: false,
    },
]
const items = mainstore.transaction_items // Data point for data
</script>