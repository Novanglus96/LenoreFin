<template>
        <v-container class="ma-0 pa-0 ga-0">
            <v-row dense>
                <v-col><v-span class="text-h6 text-accent">Upcoming Transactions</v-span></v-col><v-col cols=1 class="text-right"><v-btn icon="mdi-cog" size="xs" flat></v-btn></v-col>
            </v-row>
            <v-row>
                <v-col><v-data-table :items="items" density="compact" items-per-page="10"></v-data-table></v-col>
            </v-row>
        </v-container>
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