<template>
    <v-dialog v-model="show" persistent width="1024">
        <v-card>
            <v-card-title>
                <span class="text-h5" v-if="props.isEdit == false">Add Transaction</span>
                <span class="text-h5" v-else>Edit Transaction</span>
            </v-card-title>
            <v-card-text>
                <v-container>
                    <v-row>
                        <v-col>
                            <VueDatePicker
                                v-model="formData.transaction_date"
                                timezone="America/New_York"
                                model-type="yyyy-MM-dd"
                                :enable-time-picker="false"
                                auto-apply
                                format="yyyy-MM-dd"
                            ></VueDatePicker>
                        </v-col>
                    </v-row>
                    <v-row>
                        <v-col>
                            <v-autocomplete
                                clearable
                                label="Transaction Type*"
                                :items="transaction_types"
                                variant="outlined"
                                :loading="transaction_types_isLoading"
                                item-title="transaction_type"
                                item-value="id"
                                v-model="formData.transaction_type_id"
                                :rules="required"
                                @update:model-value="checkFormComplete"
                            ></v-autocomplete>
                        </v-col>
                        <v-col>
                            <v-autocomplete
                                clearable
                                label="Transaction Status*"
                                :items="transaction_statuses"
                                variant="outlined"
                                :loading="transaction_statuses_isLoading"
                                item-title="transaction_status"
                                item-value="id"
                                v-model="formData.status_id"
                                :rules="required"
                                @update:model-value="checkFormComplete"
                            ></v-autocomplete>
                        </v-col>
                    </v-row>
                    <v-row>
                        <v-col>
                            <v-text-field
                                v-model="amount"
                                variant="outlined"
                                label="Amount*"
                                :rules="required"
                                prefix="$"
                                @update:model-value="checkFormComplete"
                            ></v-text-field>
                        </v-col>
                        <v-col>
                            <v-text-field
                                v-model="formData.description"
                                variant="outlined"
                                label="Description*"
                                :rules="required"
                                @update:model-value="checkFormComplete"
                            ></v-text-field>
                        </v-col>
                    </v-row>
                    <v-row>
                        <v-col>
                            <v-autocomplete
                                clearable
                                label="Source Account*"
                                :items="accounts"
                                variant="outlined"
                                :loading="accounts_isLoading"
                                item-title="account_name"
                                item-value="id"
                                v-model="formData.source_account_id"
                                :rules="required"
                                @update:model-value="checkFormComplete"
                            ></v-autocomplete>
                        </v-col>
                        <v-col>
                            <v-autocomplete
                                clearable
                                label="Destination Account*"
                                :items="accounts"
                                variant="outlined"
                                :loading="accounts_isLoading"
                                item-title="account_name"
                                item-value="id"
                                v-model="formData.destination_account_id"
                                :rules="required"
                                @update:model-value="checkFormComplete"
                                v-if="formData.transaction_type_id == 3"
                            ></v-autocomplete>
                        </v-col>
                    </v-row>
                    <v-row>
                        <v-col>
                            <!-- TODO: Enable adding tags here -->
                            <v-autocomplete
                                clearable
                                label="Tag*"
                                :items="tags"
                                variant="outlined"
                                :loading="tags_isLoading"
                                item-title="tag_name"
                                item-value="id"
                                v-model="formData.tag_id"
                                v-if="!isEdit"
                                :rules="required"
                                @update:model-value="checkFormComplete"
                            >
                                <template v-slot:item="{ props, item }">
                                    <v-list-item
                                    v-bind="props"
                                    prepend-icon="mdi-tag"
                                    :title="item.raw.parent ? item.raw.parent.tag_name : item.raw.tag_name"
                                    :subtitle="item.raw.parent ? item.raw.tag_name : null"
                                    ></v-list-item>
                                </template>
                            </v-autocomplete>
                        </v-col>
                        <v-col>
                            <v-textarea
                                clearable
                                label="Memo"
                                variant="outlined"
                                v-model="formData.memo"
                            ></v-textarea>
                        </v-col>
                    </v-row>
                </v-container>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn
                    color="accent"
                    variant="text"
                    @click="closeDialog"
                >
                    Close
                </v-btn>
                <v-btn
                    color="accent"
                    variant="text"
                    @click="submitForm"
                    :disabled="!formComplete"
                >
                    Save
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>
<script setup>
import { ref, defineEmits, defineProps, onMounted, watchEffect } from 'vue'
import { useTransactionTypes } from '@/composables/transactionTypesComposable'
import { useTransactionStatuses } from '@/composables/transactionStatusesComposable'
import { useAccounts } from '@/composables/accountsComposable'
import { useTags } from '@/composables/tagsComposable'
import { useTransactions } from '@/composables/transactionsComposable'
import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';

const today = new Date();
const year = today.getFullYear();
const month = String(today.getMonth() + 1).padStart(2, '0');
const day = String(today.getDate()).padStart(2, '0');
const { accounts, isLoading: accounts_isLoading } = useAccounts()
const formattedDate = `${year}-${month}-${day}`;
const formComplete = ref(false)
const { transaction_types, isLoading: transaction_types_isLoading } = useTransactionTypes()
const { transaction_statuses, isLoading: transaction_statuses_isLoading } = useTransactionStatuses()
const { tags, isLoading: tags_isLoading } = useTags()
const { addTransaction } = useTransactions()
const props = defineProps({
    itemFormDialog: {
        type: Boolean,
        default: false
    },
    isEdit: {
        type: Boolean,
        default: false
    },
    passedFormData: Array,
    account_id: {
        type: Number,
        default: 1
    }
})
const formData = ref({
    id: 0,
    status_id: 1,
    transaction_type_id: 1,
    transaction_date: formattedDate,
    memo: "",
    source_account_id: null,
    destination_account_id: null,
    edit_date: formattedDate,
    add_date: formattedDate,
    tag_id: 1,
    total_amount: 0
})

const amount = ref(null)
const show = ref(props.itemFormDialog)
const emit = defineEmits(['updateDialog'])
const watchPassedFormData = () => {
    watchEffect(() => {
        if (props.passedFormData) {
            formData.value.id = props.passedFormData.id;
            formData.value.name = props.passedFormData.name;
            formData.value.matches = props.passedFormData.matches;
        }
    })
}

const required = [
    value => {
        if (value) return true;

        return 'This field is required.';
    },
];

const checkFormComplete = async () => {
    if (formData.value.transaction_type_id !== null 
        && formData.value.transaction_type_id !== '' 
        && formData.value.status_id !== null 
        && formData.value.status_id !== ''
        && formData.value.description !== ''
        && formData.value.description !== null
        && amount.value !== ''
        && amount.value !== null
        && formData.value.transaction_source_account_id !== ''
        && formData.value.transaction_source_account_id !== null
        && formData.value.tag_id !== ''
        && formData.value.tag_id !== null
    ) {
        if ((formData.value.status_id == 3 && formData.value.transaction_destination_account_id !== null)
            || (formData.value.status_id !== 3)
        ) {
            formComplete.value = true
        } else {
            formComplete.value = false
        }
        
    } else {
        formComplete.value = false
    }
}

onMounted(() => {
    watchPassedFormData();
})

const submitForm = async () => {
    if (formData.value.transaction_type_id == 2) {
        formData.value.total_amount = amount.value
    } else {
        formData.value.total_amount = -amount.value
    }
    if (props.isEdit == false) {
        await addTransaction(formData.value)
    } else {
        console.log('edit')
    }

    closeDialog()
}

const closeDialog = () => {
    emit('updateDialog', false);
};
</script>