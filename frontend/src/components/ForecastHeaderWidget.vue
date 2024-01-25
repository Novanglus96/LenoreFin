<template>
    <div>
        <v-card
            variant="outlined"
            :elevation="4"
            class="bg-accent"
            v-if="!accounts_isLoading"
        >
            <template v-slot:text>
                <v-row desnity="compact">
                    <v-col col="2">
                        <v-slide-group
                            v-model="account_selected"
                            class="pa-4"
                            selected-class="bg-secondary"
                            show-arrows
                            center-active
                        >
                            <v-slide-group-item
                                v-for="account in accounts"
                                :key="account.id"
                                v-slot="{ toggle, selectedClass }"
                                :value="account.id"
                                @group:selected="clickAccountUpdate"
                            >
                                <v-card
                                    color="primary"
                                    :class="['ma-4', selectedClass]"
                                    height="75"
                                    width="350"
                                    @click="toggle"
                                    :title="account.account_name"
                                    :subtitle="account.bank.bank_name"
                                    prepend-icon="mdi-bank"
                                >
                                </v-card>
                            </v-slide-group-item>
                        </v-slide-group>
                    </v-col>
                </v-row>
            </template>
        </v-card>
        <v-skeleton-loader type="card" v-if="accounts_isLoading"></v-skeleton-loader>
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