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
            <span class="text-subtitle-2 text-accent">Upcoming Reminders</span>
        </template>
        <template v-slot:text>
            <v-data-table :items="items" density="compact" items-per-page="5"></v-data-table>
        </template>
    </v-card>
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