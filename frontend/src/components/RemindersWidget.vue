<template>
    <v-container class="ma-0 pa-0 ga-0" fluid>
        <v-row dense>
            <v-col><v-span class="text-h6 text-accent">Upcoming Reminders</v-span></v-col><v-col cols=1 class="text-right"><v-btn icon="mdi-cog" size="xs" flat></v-btn></v-col>
        </v-row>
        <v-row>
            <v-col><v-data-table :items="items" density="compact" items-per-page="5"></v-data-table></v-col>
        </v-row>
    </v-container>
</template>
<script setup>
const items = [
    {
        Date: 'January 5th, 2024',
        Amount: '$-400.00',
        Reminder: 'Transfer to Kids',
    },
    {
        Date: 'January 5th, 2024',
        Amount: '$-200.00',
        Reminder: 'Transfer to Money Pile',
    },
    {
        Date: 'January 5th, 2024',
        Amount: '$991.48',
        Reminder: 'Primepoint Payroll - Danielle',
    },
    {
        Date: 'January 5th, 2024',
        Amount: '$192.30',
        Reminder: 'Dependent Care Contribution',
    },
    {
        Date: 'January 5th, 2024',
        Amount: '$-100.00',
        Reminder: 'Transfer to Reno',
    },
]
</script>