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
            <v-data-table
                :loading="isLoading"
                :headers="headers"
                :items="items"
                :item-value="reminder"
                density="compact"
                items-per-page="5"
                no-filter
            >
                <template v-slot:item="{ item }">
                    <tr>
                        <td class="text-center" width="10%">{{ item.date }}</td>
                        <td class="text-center" width="10%"><span :class="item.amount >= 0 ? 'text-green' : 'text-red'">${{ item.amount }}</span></td>
                        <td width="100%">{{ item.reminder }}</td>
                    </tr>
                </template>
                <template v-slot:loading>
                    <v-skeleton-loader type="table-row@5"></v-skeleton-loader>
                </template>
            </v-data-table>
        </template>
    </v-card>
</template>
<script setup>
import { useMainStore } from '@/stores/main'

const mainstore = useMainStore()
const headers = [
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
        title: 'Reminder',
        align: 'start',
        key: 'reminder',
        sortable: false,
        removable: false,
    },
]
const items = mainstore.reminder_items // Data point for data
</script>