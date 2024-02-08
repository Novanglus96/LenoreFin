<template>
    <v-dialog
        width="400"
    >
        <v-card>
            <v-card-title>Adjust Balance</v-card-title>
            <v-card-text>
                <v-container>
                    <v-row density>
                        <v-col>
                            <v-text-field
                                v-model="currentBalance"
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
            <v-card-actions><v-spacer></v-spacer><v-btn @click="emit('updateDialog', false)" color="accent">Close</v-btn><v-btn @click="clickAdjustBalance()" color="accent" :disabled="balanceSubmit">Adjust</v-btn></v-card-actions>
        </v-card>
    </v-dialog>
</template>
<script setup>
import { defineEmits, defineProps, ref, watch } from 'vue'
import { useTransactions } from '@/composables/transactionsComposable'

const today = new Date();
const year = today.getFullYear();
const month = String(today.getMonth() + 1).padStart(2, '0');
const day = String(today.getDate()).padStart(2, '0');
const formattedDate = `${year}-${month}-${day}`;
const props = defineProps({
    account: Object
})

const checkBalance = async () => {
    if (new_balance.value !== '' && new_balance.value !== null) {
        balanceSubmit.value = false
    } else {
        balanceSubmit.value = true
    }
}

const currentBalance = ref(props.account.balance)

watch(() => props.account.balance, (newValue) => {
    currentBalance.value = newValue
})
const required = [
    value => {
        if (value) return true;

        return 'This field is required.';
    },
];

const new_balance = ref('')
const balanceForm = ref({
    id: 0,
    status_id: 2,
    transaction_type_id: 1,
    transaction_date: formattedDate,
    memo: "",
    source_account_id: props.account.id,
    destination_account_id: null,
    edit_date: formattedDate,
    add_date: formattedDate,
    tag_id: 35,
    total_amount: '',
    description: 'Balance Adjustment'
})

const balanceSubmit = ref(true)

const emit = defineEmits(['updateDialog'])
const { addTransaction } = useTransactions()
const clickAdjustBalance = async () => {
    if (currentBalance.value > new_balance.value) {
        balanceForm.value.transaction_type_id = 1
    } else {
        balanceForm.value.transaction_type_id = 2
    }
    balanceForm.value.total_amount = new_balance.value - currentBalance.value
    await addTransaction(balanceForm.value)
    emit('updateDialog', false)
    new_balance.value = ''
}
</script>