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
                <span class="text-subtitle-2 text-accent" v-if="props.start_integer == 0">Forecast</span>
                <span class="text-subtitle-2 text-accent" v-else>Cash Flow</span>
            </template>
            <template v-slot:text>
                <v-progress-circular
                    color="accent"
                    indeterminate
                    :size="300"
                    :width="12"
                    v-if="isLoading"
                >Loading...</v-progress-circular>
                <Line :data="account_forecast" :options="options" v-if="!isLoading" ref="Forecast" aria-label="Account Forecast">Unable to load forecast</Line>
            </template>
        </v-card>
</template>
<script setup>
import { ref, defineProps } from 'vue'
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
} from 'chart.js'
import { Line } from 'vue-chartjs'
import { useAccountForecasts } from '@/composables/forecastsComposable'

const props = defineProps({
    account: Array,
    start_integer: { type: Number, default: 14 },
    end_integer: { type: Number, default: 90 }
})

const { isLoading, account_forecast } = useAccountForecasts(props.account, props.start_integer, props.end_integer)

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
)

const options = ref({
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: "5",
    plugins: {
        tooltip: {
            callbacks: {
                label: function (context) {
                    let label = context.dataset.label || '';

                    if (label) {
                        label += ': ';
                    }
                    if (context.parsed.y !== null) {
                        label += new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(context.parsed.y);
                    }
                    return label;
                }
            }
        },
        legend: {
            display: false,
        }
    },
    scales: {
        y: {
            ticks: {
                // Include a dollar sign in the ticks
                callback: function (value) {
                    return '$' + value;
                }
            }
        }
    }
})

</script>