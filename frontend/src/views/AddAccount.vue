<template>
    <v-card v-if="page1">
        <v-card-title>What bank is this account with?</v-card-title>
        <v-card-text>
            <v-form @submit.prevent>
                <v-autocomplete
                    clearable
                    label="Bank Name"
                    :items="banks"
                    variant="outlined"
                    :loading="isLoading"
                    item-title="bank_name"
                    item-value="id"
                    
                ></v-autocomplete>
                <v-btn>Don't see your bank?</v-btn>
            </v-form>
        </v-card-text>
        <v-card-actions>
            <v-btn @click="page1 ? (page1 = false, page2 = true) : (page1 = true, page2 = false)">
                Next
            </v-btn>
        </v-card-actions>
    </v-card>
    <v-card v-if="page2">
        <v-card-title>This is page2</v-card-title>
        <v-card-actions>
            <v-btn @click="page2 ? (page2 = false, page1 = true) : (page2 = true, page1 = false)">
                Back
            </v-btn>
            <v-btn @click="page2 ? (page2 = false, page3 = true) : (page2 = true, page3 = false)">
                Next
            </v-btn>
        </v-card-actions>
    </v-card>
</template>
<script setup>
import { useBanks } from '@/composables/banksComposable'
import { ref } from 'vue'

const page1 = ref(true)
const page2 = ref(false)
const page3 = ref(false)
const { banks, isLoading } = useBanks()
</script>