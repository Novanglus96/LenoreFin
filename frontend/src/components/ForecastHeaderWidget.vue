<template>
    <div>
        <v-card
            variant="outlined"
            :elevation="4"
            class="bg-accent"
        >
            <template v-slot:text>
                <v-row desnity="compact">
                    <v-col col="2"></v-col>
                    <v-col col="2" class="text-center text-black font-weight-bold">
                        <v-autocomplete
                            clearable
                            label="Account for Forecast"
                            :items="accounts"
                            variant="outlined"
                            :loading="accounts_isLoading"
                            item-title="account_name"
                            item-value="id"
                            v-model="account_selected"
                            prepend-icon="mdi-arrow-left-bold"
                            append-icon="mdi-arrow-right-bold"
                            auto-select-first
                            base-color="primary"
                            @update:model-value="clickAccountUpdate"
                        ></v-autocomplete>
                    </v-col>
                    <v-col col="2"></v-col>
                </v-row>
            </template>
        </v-card>
    </div>
</template>
<script setup>
import { useAccounts } from '@/composables/accountsComposable'
import { ref, defineEmits } from 'vue'

const emit = defineEmits(['updateAccount'])
const account_selected = ref(null)
const { accounts, isLoading: accounts_isLoading } = useAccounts()

const clickAccountUpdate = () => {
    console.log('account:', account_selected.value)
    emit('updateAccount', account_selected.value)
}
</script>