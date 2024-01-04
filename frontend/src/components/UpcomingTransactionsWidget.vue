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
                :headers="headers"
                :items="items"
                density="compact"
                items-per-page="10"
                no-filter
            >
                <template v-slot:item="{ item }">
                        <tr>
                            <td class="text-center" width="10%">{{ item.date }}</td>
                            <td class="text-center" width="10%"><span :class="item.amount >= 0 ? 'text-green' : 'text-red'">${{ item.amount }}</span></td>
                            <td width="20%">{{ item.description }}</td>
                            <td width="10%"><v-icon icon="mdi-tag" size="xs"></v-icon>{{ item.tag }}</td>
                            <td width="100%">{{ item.account }}</td>
                        </tr>
                    </template>
            </v-data-table>
        </template>
    </v-card>
</template>
<script setup>
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
const items = [
    {
        date: '3rd Jan 2024',
        amount: '-950.00',
        description: 'Rent',
        tag: 'Rent',
        account: 'Our Checking Account',
    },
    {
        date: '4th Jan 2024',
        amount: '-503.36',
        description: 'Transfer from Savings (Christmas)',
        tag: 'Transfer',
        account: 'Ally - Christmas => Our Checking Account',
    },
    {
        date: '4th Jan 2024',
        amount: '-1660.46',
        description: 'Transfer to Checking (Kids)',
        tag: 'Transfer',
        account: 'Ally - Kids => Our Checking Account',
    },
    {
        date: '4th Jan 2024',
        amount: '-1530.00',
        description: 'Zelle Payment to Lilys Ducklings',
        tag: 'Kids/Child Care',
        account: 'Our Checking Account',
    },
    {
        date: '4th Jan 2024',
        amount: '-20.00',
        description: 'Transfer to Checking (Charity)',
        tag: 'Transfer',
        account: 'Ally - Charity => Our Checking Account',
    },
]
</script>