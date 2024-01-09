<template>
    <div>
        <v-card
            variant="outlined"
            :elevation="4"
            class="bg-accent"
            v-if="!isLoading"
        >
            <template v-slot:append>
                <v-btn icon="mdi-cash-edit" flat variant="plain" @click="clickAdjustBalance(props.account)"/>
                <v-btn icon="mdi-application-edit" flat variant="plain" @click="clickEditAccount(props.account)"/>
                <v-btn icon="mdi-bank-remove" color="red" flat variant="plain" @click="clickRemoveAccount(props.account)"/>
            </template>
            <template v-slot:title>
                {{ account.account_name }}
            </template>
            <template v-slot:subtitle>
                ${{ account.balance }}
            </template>
            <template v-slot:text>
                <v-row desnity="compact" v-if="account.account_type.id == 1">
                    <v-col col="2" class="text-right text-black font-weight-bold">Statement Ending:</v-col><v-col col="2">{{ account.next_cycle_date }}</v-col>
                    <v-col col="2" class="text-right text-black font-weight-bold">Last Statement:</v-col><v-col col="2">$-1000.00</v-col>
                    <v-col col="2" class="text-right text-black font-weight-bold">Rewards:</v-col><v-col col="2">${{ account.rewards_amount }}</v-col>
                    <v-col col="2" class="text-right text-black font-weight-bold">Available Credit:</v-col><v-col col="2">${{ account.available_credit }}</v-col>
                </v-row>
            </template>
        </v-card>
        <v-skeleton-loader type="card" color="accent" height="100" v-else></v-skeleton-loader>
    </div>
</template>
<script setup>
import { defineProps, defineEmits } from 'vue'
import { useAccountByID } from '@/composables/accountsComposable'

const props = defineProps({
    account: Array
})

const emit = defineEmits(['adjustBalance', 'removeAccount', 'editAccount'])

const { account, isLoading } = useAccountByID(props.account)

const clickAdjustBalance = async (account_id) => {
    emit('adjustBalance', account_id)
}

const clickRemoveAccount = async (account_id) => {
    emit('removeAccount', account_id)
}

const clickEditAccount = async (account_id) => {
    emit('editAccount', account_id)
}
</script>