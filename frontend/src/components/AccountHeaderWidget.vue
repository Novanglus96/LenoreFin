<template>
    <div>
        <v-card
            variant="outlined"
            :elevation="4"
            class="bg-accent"
            v-if="!isLoading"
        >
            <template v-slot:append>
                <v-tooltip text="Adjust Balance" location="top">
                    <template v-slot:activator="{ props }">
                        <v-btn icon="mdi-cash-edit" flat variant="plain" @click="adjBalDialog = true" v-bind="props"/>
                    </template>
                </v-tooltip>
                <v-dialog
                    v-model="adjBalDialog"
                    width="400"
                >
                    <v-card>
                        <v-card-title>Adjust Balance</v-card-title>
                        <v-card-text>
                            <v-container>
                                <v-row density>
                                    <v-col>
                                        <v-text-field
                                            v-model="account.balance"
                                            variant="outlined"
                                            label="Current Balance"
                                            prefix="$"
                                            disabled
                                        ></v-text-field>
                                    </v-col>
                                </v-row>
                                <v-row density>
                                    <v-col>
                                        <v-text-field
                                            v-model="new_balance"
                                            variant="outlined"
                                            label="New Balance*"
                                            :rules="required"
                                            prefix="$"
                                            @update:model-value="checkBalance"
                                        ></v-text-field>
                                    </v-col>
                                </v-row>
                            </v-container>
                        </v-card-text>
                        <v-card-actions><v-btn @click="clickAdjustBalance()" color="accent" :disabled="balanceSubmit">Adjust</v-btn><v-btn @click="adjBalDialog = false" color="accent">Close</v-btn></v-card-actions>
                    </v-card>
                </v-dialog>
                <v-tooltip text="Edit Account" location="top">
                    <template v-slot:activator="{ props }">
                        <v-btn icon="mdi-application-edit" flat variant="plain" @click="clickEditAccount(props.account)" v-bind="props"/>
                    </template>
                </v-tooltip>
                <v-tooltip text="Delete Account" location="top">
                    <template v-slot:activator="{ props }">
                        <v-btn icon="mdi-bank-remove" color="red" flat variant="plain" @click="clickRemoveAccount(props.account)" v-bind="props"/>
                    </template>
                </v-tooltip>
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
import { defineProps, defineEmits } from 'vue'
import { useAccountByID } from '@/composables/accountsComposable'
import { ref } from 'vue'
import { useTransactions } from '@/composables/transactionsComposable'

const { addTransaction } = useTransactions()
const today = new Date();
const year = today.getFullYear();
const month = String(today.getMonth() + 1).padStart(2, '0');
const day = String(today.getDate()).padStart(2, '0');
const formattedDate = `${year}-${month}-${day}`;
const adjBalDialog = ref(false)
const props = defineProps({
    account: Array
})

const new_balance = ref('')
const balanceForm = ref({
    id: 0,
    status_id: 2,
    transaction_type_id: 1,
    transaction_date: formattedDate,
    memo: "",
    source_account_id: props.account,
    destination_account_id: null,
    edit_date: formattedDate,
    add_date: formattedDate,
    tag_id: 35,
    total_amount: '',
    description: 'Balance Adjustment'
})

const balanceSubmit = ref(true)

const emit = defineEmits(['removeAccount', 'editAccount'])

const { account, isLoading } = useAccountByID(props.account)

const clickAdjustBalance = async () => {
    if (account.value.balance > new_balance.value) {
        balanceForm.value.transaction_type_id = 1
    } else {
        balanceForm.value.transaction_type_id = 2
    }
    balanceForm.value.total_amount = new_balance.value - account.value.balance
    addTransaction(balanceForm.value)
    adjBalDialog.value = false
}

const clickRemoveAccount = async (account_id) => {
    emit('removeAccount', account_id)
}

const clickEditAccount = async (account_id) => {
    emit('editAccount', account_id)
}

const checkBalance = async () => {
    if (new_balance.value !== '' && new_balance.value !== null) {
        balanceSubmit.value = false
    } else {
        balanceSubmit.value = true
    }
}

const required = [
    value => {
        if (value) return true;

        return 'This field is required.';
    },
];
</script>