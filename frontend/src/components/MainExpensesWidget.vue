<template>
    <v-container class="ma-0 pa-0 ga-0">
        <v-row dense>
            <v-col><v-span class="text-subtitle-2 text-accent">Main Expenses</v-span></v-col><v-col cols=1 class="text-right"><v-btn icon="mdi-cog" size="xs" flat></v-btn></v-col>
        </v-row>
        <v-row dense>
            <v-col>
                <Pie :data="data" :options="options" />
            </v-col>
        </v-row>
    </v-container>
</template>

<script setup>
import { Pie } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { ref } from 'vue'

ChartJS.register(ArcElement, Tooltip, Legend)

const data = ref({
    labels: [
        'Money Pile',
        'Kids',
        'Rent',
        'Subscriptions'
    ],
    datasets: [{
        label: 'Main Expenses',
        data: [.33, 58.05, 36.04, 5.58],
        backgroundColor: [
            '#7fb1b1',
            '#597c7c',
            '#7f8cb1',
            '#7fb17f',
            '#597c59',
            '#b17fa5',
            '#7c5973',
            '#b1a77f',
            '#edffff',
            '#dbffff',
        ],
        hoverOffset: 4
    }]
})
const options = ref({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'right'
        }
    }
})

</script>