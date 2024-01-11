<template>
    <v-card variant="outlined" :elevation="4" class="bg-white">
        <template v-slot:append>
            <v-menu location="start">
                <template v-slot:activator="{ props }">
                    <v-btn icon="mdi-cog" flat size="xs" v-bind="props">
                    </v-btn>
                </template>
                <v-card width="100">
                    <v-card-text>Test</v-card-text>
                </v-card>
            </v-menu>
        </template>
        <template v-slot:title>
            <span class="text-subtitle-2 text-accent">Transactions</span>
        </template>
        <template v-slot:text>
            <v-btn icon="mdi-invoice-text-check" flat :disabled="selected.length === 0" variant="plain" @click="clickClearTransaction(selected)"></v-btn>
            <v-btn icon="mdi-invoice-text-edit" flat :disabled="selected.length === 0 || selected.length > 1" variant="plain" @click="transactionEditFormDialog = true"></v-btn>
            <TransactionForm v-model="transactionEditFormDialog" @add-transaction="clickAddTransaction" @edit-transaction="clickEditTransaction" :isEdit="true" @update-dialog="updateEditDialog"/>
            <v-btn icon="mdi-invoice-remove" flat :disabled="selected.length === 0" variant="plain" color="error" @click="clickRemoveTransaction(selected)"></v-btn>
            <v-btn icon="mdi-invoice-plus" flat variant="plain" color="success" @click="transactionAddFormDialog = true"></v-btn>
            <TransactionForm v-model="transactionAddFormDialog" @add-transaction="clickAddTransaction" @edit-transaction="clickEditTransaction" :isEdit="false" @update-dialog="updateAddDialog"/>
            <v-data-table
                :loading="isLoading"
                :headers="headers"
                :items="transactions"
                density="compact"
                items-per-page="20"
                no-filter
                show-select
                v-model="selected"
                item-value="id">
                <template v-slot:item.pretty_total="{ value }"><!-- eslint-disable-line -->
                    <span :class="value >= 0 ? 'text-green' : 'text-red'">${{ value }}</span>
                </template>
                <template v-slot:item.balance="{ value }"><!-- eslint-disable-line -->
                    <span :class="value >= 0 ? 'text-green' : 'text-red'">${{ value }}</span>
                </template>
                <template v-slot:item.status="{ value }"><!-- eslint-disable-line -->
                    <v-icon icon="mdi-cash" :color="value.id == '1' ? 'grey' : 'green'"></v-icon>
                </template>
                <template v-slot:item.tags="{ value }"><!-- eslint-disable-line -->
                    <div v-for="tag in value" :key="tag"><v-icon icon="mdi-tag"></v-icon> {{ tag }} </div>
                </template>
                <template v-slot:expanded-row="{ columns, item }">
                    <tr>
                        <td :colspan="columns.length">
                        <span class="font-weight-bold">Memo: </span>{{ item.memo }}
                        </td>
                    </tr>
                </template>
                <template v-slot:loading>
                    <v-skeleton-loader type="table-row@20"></v-skeleton-loader>
                </template>
            </v-data-table>
        </template>
    </v-card>
</template>
<script setup>
import { ref, defineProps, defineEmits } from 'vue'
import { useTransactions } from '@/composables/transactionsComposable'
import TransactionForm from '@/components/TransactionForm'

const transactionAddFormDialog = ref(false)
const transactionEditFormDialog = ref(false)
const props = defineProps({
    account: Array
})
const emit = defineEmits(['addTransaction', 'removeTransaction', 'editTransaction', 'clearTransaction'])
const { isLoading, transactions } = useTransactions(props.account)
const selected = ref([])
const headers = [
    {
        title: 'Status',
        align: 'center',
        key: 'status',
        sortable: false,
        removable: false,
    },
    {
        title: 'Date',
        align: 'center',
        key: 'transaction_date',
        sortable: false,
        removable: false,
    },
    {
        title: 'Amount',
        align: 'center',
        key: 'pretty_total',
        sortable: false,
        removable: false,
    },
    {
        title: 'Balance',
        align: 'center',
        key: 'balance',
        sortable: false,
        removable: false,
    },
    {
        title: 'Description',
        align: 'start',
        key: 'description',
        sortable: false,
        removable: false,
    },
    {
        title: 'Tag',
        align: 'start',
        key: 'tags',
        sortable: false,
        removable: false,
    },
    {
        title: 'Account',
        align: 'start',
        key: 'pretty_account',
        sortable: false,
        removable: false,
    },
    {
        title: '',
        key: 'data-table-expand'
    }
]

const clickAddTransaction = async () => {
    emit('addTransaction', props.account)
}

const clickRemoveTransaction = async (transaction_id) => {
    emit('removeTransaction', transaction_id)
}

const clickClearTransaction = async (transaction_id) => {
    emit('clearTransaction', transaction_id)
}

const clickEditTransaction = async (transaction_id) => {
    emit('editTransaction', transaction_id)
}

const updateAddDialog = () => {
    transactionAddFormDialog.value = false
}

const updateEditDialog = () => {
    transactionEditFormDialog.value = false
}
</script>