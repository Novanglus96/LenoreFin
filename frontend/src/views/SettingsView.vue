<template>
    <div>
        <v-row class="pa-1 ga-1" no-gutters>
            <v-col class="rounded">
                <v-tabs
                    v-model="tab"
                    color="accent"
                    align-tabs="center"
                >
                    <v-tab :value="1">Options</v-tab>
                    <v-tab :value="2">Fields</v-tab>
                    <v-tab :value="3">Log</v-tab>
                </v-tabs>
                <v-window v-model="tab">
                    <v-window-item :key="1" :value="1">
                        <v-container fluid>
                        <v-row>
                            <v-col>
                                Options
                            </v-col>
                        </v-row>
                        </v-container>
                    </v-window-item>
                    <v-window-item :key="2" :value="2">
                        <v-container fluid>
                        <v-row>
                            <v-col>
                                Fields
                            </v-col>
                        </v-row>
                        </v-container>
                    </v-window-item>
                    <v-window-item :key="3" :value="3">
                        <v-container fluid>
                        <v-row>
                            <v-col>
                                <LogTableWidget />
                            </v-col>
                        </v-row>
                        </v-container>
                    </v-window-item>
                </v-window>
            </v-col>
        </v-row>
    </div>
</template>
<script setup>
import { ref } from 'vue'
import LogTableWidget from '@/components/LogTableWidget.vue'

const tab = ref(null)
</script>