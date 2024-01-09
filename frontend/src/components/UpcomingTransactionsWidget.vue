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
            <span class="text-subtitle-2 text-accent">Upcoming Transactions</span>
        </template>
        <template v-slot:text>
            <v-data-table
                :loading="isLoading"
                :headers="headers"
                :items="transactions"
                density="compact"
                items-per-page="10"
                no-filter
                item-value="id"
            >
                <template v-slot:item.pretty_total="{ value }"><!-- eslint-disable-line -->
                    <span :class="value >= 0 ? 'text-green' : 'text-red'">${{ value }}</span>
                </template>
                <template v-slot:item.status="{ value }"><!-- eslint-disable-line -->
                    <v-icon icon="mdi-cash" :color="value.id == '1' ? 'grey' : 'green'"></v-icon>
                </template>
                <template v-slot:item.tags="{ value }"><!-- eslint-disable-line -->
                    <div v-for="tag in value" :key="tag"><v-icon icon="mdi-tag"></v-icon> {{ tag }} </div>
                </template>
                <template v-slot:loading>
                    <v-skeleton-loader type="table-row@10"></v-skeleton-loader>
                </template>
            </v-data-table>
        </template>
    </v-card>
</template>
<script setup>
import { useTransactions } from '@/composables/transactionsComposable'

const { isLoading, transactions } = useTransactions()
const headers = [
    {
        title: 'Date',
        align: 'center',
        key: 'transaction_date',
        sortable: false,
        removable: false,
    },
    {
        title: 'Amount',
        align: 'center',
        key: 'pretty_total',
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
        key: 'tags',
        sortable: false,
        removable: false,
    },
    {
        title: 'Account',
        align: 'start',
        key: 'pretty_account',
        sortable: false,
        removable: false,
    },
]

</script>