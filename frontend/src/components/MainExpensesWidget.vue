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
            <span class="text-subtitle-2 text-accent">Main Expenses</span>
        </template>
        <template v-slot:text>
            <v-progress-circular
                color="accent"
                indeterminate
                :size="300"
                :width="12"
                v-if="isLoading"
            >Loading...</v-progress-circular>
            <Pie :data="tag_graph" :options="options" v-else/>
        </template>
    </v-card>
</template>

<script setup>
import { Pie } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { ref } from 'vue'
import { useGraphs } from '@/composables/tagsComposable'

ChartJS.register(ArcElement, Tooltip, Legend)

const { tag_graph, isLoading } = useGraphs(null, true, 0, [0], 'Main Expenses')

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