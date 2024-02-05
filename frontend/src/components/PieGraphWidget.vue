<template>
    <v-card
        variant="outlined"
        :elevation="4"
        class="bg-white"
    >
        <template v-slot:append>
            <v-menu location="start" :close-on-content-click="false">
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
                <v-card width="350">
                    <v-card-title>Widget {{ props.widget }}</v-card-title>
                    <v-card-subtitle>Settings</v-card-subtitle>
                    <v-card-text>
                        <v-container>
                            <v-row dense>
                                <v-col>
                                    <v-text-field
                                        v-model="formData.graph_name"
                                        variant="outlined"
                                        label="Graph Name*"
                                        :rules="required"
                                        @update:model-value="checkFormComplete"
                                    ></v-text-field>
                                </v-col>
                            </v-row>
                        </v-container>
                    </v-card-text>
                    <v-card-actions><v-btn :disabled="!formComplete" @click="submitForm()">Save</v-btn></v-card-actions>
                </v-card>
            </v-menu>
        </template>
        <template v-slot:title>
            <span class="text-subtitle-2 text-accent">{{ props.graph_name }}</span>
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
import { ref, defineProps } from 'vue'
import { useGraphs } from '@/composables/tagsComposable'
import { useMainStore } from '@/stores/main';

const mainstore = useMainStore()
ChartJS.register(ArcElement, Tooltip, Legend)
const props = defineProps({
    widget: {
        type: Number,
        default: 1
    }
})
const formData = ref({
    graph_name: props.graph_name,
    month: props.month,
    tag_id: props.tag_id,
    expense: props.expense,
    exlude: props.exclude
})
const formComplete = ref(false)
const { tag_graph, isLoading } = useGraphs(props.widget)

const options = ref({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'right'
        }
    },
    tooltip: {
        callbacks: {
            label: function (context) {
                let label = context.dataset.data || '';

                if (label) {
                    label += ': ';
                }
                if (context.parsed.x !== null) {
                    label += new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(context.parsed.x);
                }
                return label;
            }
        }
    },
})

const required = [
    value => {
        if (value) return true;

        return 'This field is required.';
    },
];

const checkFormComplete = async () => {
    if (formData.value.graph_name !== null
        && formData.value.graph_name !== ''
        && formData.value.month !== null
        && formData.value.month !== ''
        && formData.value.expense !== ''
        && formData.value.expense !== null
    ) {
        formComplete.value = true
    } else {
        formComplete.value = false
    }
}

const submitForm = () => {
    if (props.widget == 1) {
        mainstore.options.widget1_graph_name = formData.value.graph_name
    } else if (props.widget == 2) {
        mainstore.options.widget2_graph_name = formData.value.graph_name
    } else if (props.widget == 3) {
        mainstore.options.widget3_graph_name = formData.value.graph_name
    }
    formComplete.value = false
}
</script>