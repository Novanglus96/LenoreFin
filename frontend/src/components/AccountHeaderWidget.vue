<template>
    <div>
        <v-card
            variant="outlined"
            :elevation="4"
            :class="account.active ? 'bg-accent' : 'bg-grey'"
            v-if="!isLoading"
        >
            <template v-slot:append>
                <v-tooltip text="Adjust Balance" location="top">
                    <template v-slot:activator="{ props }">
                        <v-btn icon="mdi-cash-edit" flat variant="plain" @click="adjBalDialog = true" v-bind="props"/>
                    </template>
                </v-tooltip>
                <AdjustBalanceForm v-model="adjBalDialog" :account="account" @update-dialog="updateAdjBalDialog" />
                <v-tooltip text="Edit Account" location="top">
                    <template v-slot:activator="{ props }">
                        <v-btn icon="mdi-application-edit" flat variant="plain" @click="editDialog = true" v-bind="props"/>
                    </template>
                </v-tooltip>
                <EditAccountForm v-model="editDialog" :account="account" @update-dialog="updateEditDialog"/>
                <v-tooltip :text="account.active ? 'Delete Account' : 'Enable Account'" location="top">
                    <template v-slot:activator="{ props }">
                        <v-btn :icon="account.active ? 'mdi-bank-remove' : 'mdi-bank-check'" :color="account.active ? 'red' : 'green'" flat variant="plain" @click="deleteDialog = true" v-bind="props"/>
                    </template>
                </v-tooltip>
                <DeleteAccountForm v-model="deleteDialog" :account="account" @update-dialog="updateDeleteDialog" />
            </template>
            <template v-slot:title>
                {{ account.active ? account.account_name : account.account_name + ' (Inactive)'}}
            </template>
            <template v-slot:subtitle>
                ${{ account.balance }}
            </template>
            <template v-slot:text>
                <v-row desnity="compact" v-if="account.account_type.id == 1">
                    <v-col col="2" class="text-right text-black font-weight-bold">Statement Ending:</v-col><v-col col="2">{{ account.next_cycle_date }}</v-col>
                    <v-col col="2" class="text-right text-black font-weight-bold">Last Statement:</v-col><v-col col="2">${{ account.last_statement_amount }}</v-col>
                    <v-col col="2" class="text-right text-black font-weight-bold">Rewards:</v-col><v-col col="2">${{ account.rewards_amount }}</v-col>
                    <v-col col="2" class="text-right text-black font-weight-bold">Available Credit:</v-col><v-col col="2">${{ account.available_credit }}</v-col>
                </v-row>
            </template>
        </v-card>
        <v-skeleton-loader type="card" color="accent" height="100" v-else></v-skeleton-loader>
    </div>
</template>
<script setup>
import { defineProps, ref } from 'vue'
import { useAccountByID } from '@/composables/accountsComposable'
import EditAccountForm from './EditAccountForm.vue'
import AdjustBalanceForm from './AdjustBalanceForm.vue'
import DeleteAccountForm from './DeleteAccountForm.vue'


const adjBalDialog = ref(false)
const editDialog = ref(false)
const deleteDialog = ref(false)

const props = defineProps({
    account: Array
})

const { account, isLoading } = useAccountByID(props.account)

const updateAdjBalDialog = (value) => {
    adjBalDialog.value = value
}
const updateEditDialog = (value) => {
    editDialog.value = value
}
const updateDeleteDialog = (value) => {
    deleteDialog.value = value
}
</script>