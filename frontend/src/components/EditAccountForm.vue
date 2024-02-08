<template>
    <v-dialog
        width="800"
    >
        <v-card>
            <v-card-title>Edit Account</v-card-title>
            <v-card-text>
                <v-container>
                    <v-row density>
                        <v-col>
                            {{ props.account.account_name }}
                        </v-col>
                    </v-row>
                </v-container>
            </v-card-text>
            <v-card-actions><v-spacer></v-spacer><v-btn @click="emit('updateDialog', false)" color="accent">Close</v-btn><v-btn @click="clickEditAccount()" color="accent" :disabled="editSubmit">Save</v-btn></v-card-actions>
        </v-card>
    </v-dialog>
</template>
<script setup>
import { defineEmits, defineProps } from 'vue';

//const { editAccount } = useAccountByID(props.account.id)
const emit = defineEmits(['updateDialog'])
const props = defineProps({
    account: Object
})

const clickEditAccount = () => {
    emit('updateDialog', false)
}
</script>