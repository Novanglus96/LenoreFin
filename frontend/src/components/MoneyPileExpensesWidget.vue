<template>
    <v-container class="ma-0 pa-0 ga-0">
        <v-row dense>
            <v-col><v-span class="text-subtitle-2 text-accent">Money Pile Expenses</v-span></v-col><v-col cols=1 class="text-right"><v-btn icon="mdi-cog" size="xs" flat></v-btn></v-col>
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
        'Eating Out',
    ],
    datasets: [{
        label: 'Money Pile Expenses',
        data: [8.79],
        backgroundColor: [
            '#06966A',
            '#ECFDF5',
            'green',
            'blue',
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