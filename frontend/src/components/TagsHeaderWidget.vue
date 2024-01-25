<template>
    <div>
        <v-card
            variant="outlined"
            :elevation="4"
            class="bg-accent"
            v-if="!isLoading"
        >
            <template v-slot:text>
                <v-row desnity="compact">
                    <v-col>
                        <div  class="text-center">
                            <v-btn prepend-icon="mdi-plus" size="small" variant="text">
                                Add Tag
                            </v-btn>
                        </div>
                        <v-slide-group
                            v-model="tag_selected"
                            class="pa-4"
                            selected-class="bg-secondary"
                            show-arrows
                            center-active
                        >
                        <v-slide-group-item
                            v-for="tag in tags"
                            :key="tag.id"
                            v-slot="{ toggle, selectedClass }"
                            @group:selected="clickSelectTag"
                            :value="tag.id"
                        >
                            <v-card
                            color="primary"
                            :class="['ma-4', selectedClass]"
                            height="75"
                            width="200"
                            @click="toggle"
                            :title="tag.parent ? tag.parent.tag_name : tag.tag_name"
                            :subtitle="!tag.parent ? '' : tag.tag_name"
                            prepend-icon="mdi-tag"
                            >
                            </v-card>
                        </v-slide-group-item>
                        </v-slide-group>

                        <v-expand-transition>
                        <v-sheet
                            v-if="tag_selected != null"
                            height="150"
                            color="primary"
                        >
                            <div class="d-flex fill-height align-center justify-center">
                            <h3 class="text-h6">
                                Selected {{ tag_selected }}
                            </h3>
                            </div>
                        </v-sheet>
                        </v-expand-transition>
                    </v-col>
                </v-row>
            </template>
        </v-card>
        <v-skeleton-loader type="card" v-if="isLoading"></v-skeleton-loader>
    </div>
</template>
<script setup>
import { ref, defineEmits } from 'vue'
import { useTags } from '@/composables/tagsComposable'

const emit = defineEmits(['tagSelected'])
const tag_selected = ref(null)
const { tags, isLoading } = useTags()

const clickSelectTag = () => {
    emit('tagSelected', tag_selected.value)
}
</script>