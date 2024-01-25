<template>
    <div>
        <v-row class="pa-1 ga-1" no-gutters>
            <v-col class="rounded">
                <TagsHeaderWidget />
            </v-col>
        </v-row>
        <v-row class="pa-1 ga-1 rounded" no-gutters>
            <v-col class="rounded">
                Transactions
            </v-col>
        </v-row>
    </div>
</template>
<script setup>
import TagsHeaderWidget from '@/components/TagsHeaderWidget.vue'

</script>