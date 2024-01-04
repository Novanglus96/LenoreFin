<template>
    <v-card
        variant="outlined"
        :elevation="4"
        class="bg-white"
    >
        <template v-slot:append>
            <v-btn icon="mdi-cog" to="/" flat size="xs"></v-btn>
        </template>
        <template v-slot:title>
            <span class="text-subtitle-2 text-accent">Upcoming Transactions</span>
        </template>
        <template v-slot:text>
            <v-data-table :items="items" density="compact" items-per-page="10"></v-data-table>
        </template>
    </v-card>
</template>
<script setup>
const items = [
    {
        Date: '3rd Jan 2024',
        Amount: '$-950',
        Description: 'Rent',
        Tag: 'Rent',
        Account: 'Our Checking Account',
    },
    {
        Date: '4th Jan 2024',
        Amount: '$-503.36',
        Description: 'Transfer from Savings (Christmas)',
        Tag: 'Transfer',
        Account: 'Ally - Christmas => Our Checking Account',
    },
    {
        Date: '4th Jan 2024',
        Amount: '$-1660.46',
        Description: 'Transfer to Checking (Kids)',
        Tag: 'Transfer',
        Account: 'Ally - Kids => Our Checking Account',
    },
    {
        Date: '4th Jan 2024',
        Amount: '$-1530.00',
        Description: 'Zelle Payment to Lilys Ducklings',
        Tag: 'Kids/Child Care',
        Account: 'Our Checking Account',
    },
    {
        Date: '4th Jan 2024',
        Amount: '$-20',
        Description: 'Transfer to Checking (Charity)',
        Tag: 'Transfer',
        Account: 'Ally - Charity => Our Checking Account',
    },
]
</script>