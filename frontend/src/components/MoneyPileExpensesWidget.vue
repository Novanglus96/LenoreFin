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
            <span class="text-subtitle-2 text-accent">Money Pile Expenses</span>
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
import { useMainStore } from '@/stores/main'

ChartJS.register(ArcElement, Tooltip, Legend)

const mainstore = useMainStore();
const data = ref({
    labels: [
        'Eating Out',
    ],
    datasets: [{
        label: 'Money Pile Expenses',
        data: [8.79],
        backgroundColor: mainstore.graphColors,
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