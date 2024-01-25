<template>
    <div>
        <v-row class="pa-1 ga-1" no-gutters>
            <v-col class="rounded">
                <TagsHeaderWidget @tag-selected="clickSelectedTag"/>
            </v-col>
        </v-row>
        <v-row class="pa-1 ga-1 rounded" no-gutters>
            <v-col class="rounded">
                Averages {{ selected_tag }}
            </v-col>
        </v-row>
        <v-row class="pa-1 ga-1 rounded" no-gutters>
            <v-col class="rounded">
                Transactions {{ selected_tag }}
            </v-col>
        </v-row>
    </div>
</template>
<script setup>
import TagsHeaderWidget from '@/components/TagsHeaderWidget.vue'
import { ref } from 'vue'

const selected_tag = ref(null)

const clickSelectedTag = (tag_id) => {
    selected_tag.value = tag_id
}
</script>