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
            <span class="text-subtitle-2 text-accent">Main Expenses</span>
        </template>
        <template v-slot:text>
            <Pie :data="data" :options="options" />
        </template>
    </v-card>
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