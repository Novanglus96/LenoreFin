<template>
    <v-dialog
        width="400"
    >
        <v-card>
            <v-card-title>{{ account.active ? 'Disable/Delete' : 'Enable' }} Account?</v-card-title>
            <v-card-subtitle>Do you want to {{ account.active ? 'disable or delete ' + account.account_name : 'enable ' + account.account_name }}?</v-card-subtitle>
            <v-card-text>
                <v-container v-if="account.active">
                    <v-row density>
                        <v-col>
                            <v-btn-toggle
                                v-model="disableAccount"
                                rounded="0"
                                color="accent"
                                group
                            >
                                <v-btn :value="true">
                                    Disable
                                </v-btn>
                                <v-btn :value="false">
                                    Delete
                                </v-btn>
                            </v-btn-toggle>
                        </v-col>
                    </v-row>
                </v-container>
            </v-card-text>
            <v-card-actions><v-spacer></v-spacer><v-btn @click="emit('updateDialog', false)" color="accent">Close</v-btn><v-btn @click="clickRemoveAccount()" color="accent" :disabled="deleteSubmit">{{ displayButtonText() }}</v-btn></v-card-actions>
        </v-card>
    </v-dialog>
</template>
<script setup>
import { useRouter } from 'vue-router'
import { useAccountByID } from '@/composables/accountsComposable'
import { ref, defineEmits, defineProps } from 'vue'

const props = defineProps({
    account: Object
})
const emit = defineEmits(['updateDialog'])
const { removeAccount, editAccount } = useAccountByID(props.account.id)
const disableAccount = ref(true)
const router = useRouter()
const clickRemoveAccount = async () => {
    if (props.account.active) {
        if (disableAccount.value == false) {
            removeAccount(props.account.id)
            emit('updateDialog', false)
            router.push('/')
        } else {
            const data = {
                id: props.account.id,
                active: false
            }
            editAccount(data)
            emit('updateDialog', false)
        }
    } else {
        const data = {
            id: props.account.id,
            active: true
        }
        editAccount(data)
        emit('updateDialog', false)
    }
}

const displayButtonText = () => {
    if (!props.account.active) {
        return 'Enable'
    } else {
        if (disableAccount.value) {
            return 'Disable'
        } else {
            return 'Delete'
        }
    }
}
</script>