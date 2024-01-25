<template>
    <div>
        <v-card
            variant="outlined"
            :elevation="4"
            class="bg-accent"
        >
            <template v-slot:text>
                <v-row desnity="compact">
                    <v-col>
                        <v-slide-group
                            v-model="model"
                            class="pa-4"
                            selected-class="bg-warning"
                            show-arrows
                            center-active
                        >
                        <v-slide-group-item
                            v-for="n in 15"
                            :key="n"
                            v-slot="{ toggle, selectedClass }"
                        >
                            <v-card
                            color="primary"
                            :class="['ma-4', selectedClass]"
                            height="75"
                            width="200"
                            @click="toggle"
                            title="Parent Tag"
                            subtitle="Sub Tag"
                            prepend-icon="mdi-tag"
                            >
                            </v-card>
                        </v-slide-group-item>
                        </v-slide-group>

                        <v-expand-transition>
                        <v-sheet
                            v-if="model != null"
                            height="150"
                            color="primary"
                        >
                            <div class="d-flex fill-height align-center justify-center">
                            <h3 class="text-h6">
                                Selected {{ model }}
                            </h3>
                            </div>
                        </v-sheet>
                        </v-expand-transition>
                    </v-col>
                </v-row>
            </template>
        </v-card>
    </div>
</template>
<script setup>
import { ref } from 'vue'

const model = ref(null)
</script>