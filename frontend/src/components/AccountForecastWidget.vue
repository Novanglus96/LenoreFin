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
                        :disabled="isLoading"
                        >
                        </v-btn>
                    </template>
                    <v-card width="100">
                        <v-card-text>Test</v-card-text>
                    </v-card>
                </v-menu>
            </template>
            <template v-slot:title>
                <span class="text-subtitle-2 text-accent">Forecast</span>
            </template>
            <template v-slot:text>
                <v-progress-circular
                    color="accent"
                    indeterminate
                    :size="300"
                    :width="12"
                    v-if="isLoading"
                >Loading...</v-progress-circular>
                <Line :data="data" :options="options" v-else/>
            </template>
        </v-card>
</template>
<script setup>
import { ref } from 'vue'
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
} from 'chart.js'
import { Line } from 'vue-chartjs'

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
)

const data = ref({
    labels: ['Dec 06', 'Dec 07', 'Dec 08', 'Dec 09', 'Dec 10', 'Dec 11', 'Dec 12', 'Dec 13', 'Dec 14', 'Dec 15', 'Dec 16', 'Dec 17', 'Dec 18', 'Dec 19', 'Dec 20', 'Dec 21', 'Dec 22', 'Dec 23'],
    datasets: [
        {
            label: 'Data One',
            backgroundColor: '#f87979',
            data: [10, 10, 10, 10, 39, 80, 40, 1000, 2000, 30000, 400],
            fill: {
                target: 1,
                above: 'rgb(255, 0, 0)',   // Area will be red above the origin
                below: 'rgb(0, 0, 255)'    // And blue below the origin
            }
        }
    ]
})

const options = ref({
    responsive: true,
    maintainAspectRatio: false
})

</script>