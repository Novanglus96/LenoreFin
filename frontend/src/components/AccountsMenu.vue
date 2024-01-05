<template>
    <div>
        <v-list density="compact" nav>
            <v-list-item prepend-icon="mdi-plus-circle" base-color="accent" :to="add_account_link">
                <v-list-item-title>Add Account</v-list-item-title>
            </v-list-item>
        </v-list>
        <v-list density="compact">
            <v-list-subheader><v-icon icon="mdi-checkbook"></v-icon> CHECKING</v-list-subheader>
            <v-list-item title="No Accounts" v-if="checking_accounts.length == 0"></v-list-item>
            <v-list-item v-for="(account, i) in checking_accounts" :key="i" :to="'/accounts/' + account.id" v-else>
                <v-list-item-title>{{ account.account_name }} </v-list-item-title>
                <v-list-item-subtitle><span
                        :class="account.balance >= 0 ? 'text-green font-weight-bold' : 'text-red font-weight-bold'">${{
                            account.balance }}</span></v-list-item-subtitle>
            </v-list-item>
        </v-list>
        <v-divider></v-divider>
        <v-list density="compact" nav>
            <v-list-subheader><v-icon icon="mdi-piggy-bank"></v-icon> SAVINGS</v-list-subheader>
            <v-list-item title="No Accounts" v-if="savings_accounts.length == 0"></v-list-item>
            <v-list-item v-for="(account, i) in savings_accounts" :key="i" :to="'/accounts/' + account.id" v-else>
                <v-list-item-title>{{ account.account_name }} </v-list-item-title>
                <v-list-item-subtitle><span
                        :class="account.balance >= 0 ? 'text-green font-weight-bold' : 'text-red font-weight-bold'">${{
                            account.balance }}</span></v-list-item-subtitle>
            </v-list-item>
        </v-list>
        <v-divider></v-divider>
        <v-list density="compact" nav>
            <v-list-subheader><v-icon icon="mdi-credit-card"></v-icon> CREDIT CARD</v-list-subheader>
            <v-list-item title="No Accounts" v-if="cc_accounts.length == 0"></v-list-item>
            <v-list-item v-for="(account, i) in cc_accounts" :key="i" :to="'/accounts/' + account.id" v-else>
                <v-list-item-title>{{ account.account_name }} </v-list-item-title>
                <v-list-item-subtitle><span
                        :class="account.balance >= 0 ? 'text-green font-weight-bold' : 'text-red font-weight-bold'">${{
                            account.balance }}</span></v-list-item-subtitle>
            </v-list-item>
        </v-list>
        <v-divider></v-divider>
        <v-list density="compact" nav>
            <v-list-subheader><v-icon icon="mdi-finance"></v-icon> INVESTMENT</v-list-subheader>
            <v-list-item title="No Accounts" v-if="investment_accounts.length == 0"></v-list-item>
            <v-list-item v-for="(account, i) in investment_accounts" :key="i" :to="'/accounts/' + account.id" v-else>
                <v-list-item-title>{{ account.account_name }} </v-list-item-title>
                <v-list-item-subtitle><span
                        :class="account.balance >= 0 ? 'text-green font-weight-bold' : 'text-red font-weight-bold'">${{
                            account.balance }}</span></v-list-item-subtitle>
            </v-list-item>
        </v-list>
        <v-divider></v-divider>
        <v-list density="compact" nav>
            <v-list-subheader><v-icon icon="mdi-car-back"></v-icon> LOAN</v-list-subheader>
            <v-list-item title="No Accounts" v-if="loan_accounts.length == 0"></v-list-item>
            <v-list-item v-for="(account, i) in loan_accounts" :key="i" :to="'/accounts/' + account.id" v-else>
                <v-list-item-title>{{ account.account_name }} </v-list-item-title>
                <v-list-item-subtitle><span
                        :class="account.balance >= 0 ? 'text-green font-weight-bold' : 'text-red font-weight-bold'">${{
                            account.balance }}</span></v-list-item-subtitle>
            </v-list-item>
        </v-list>
</div></template>
<script setup>
import { useAccounts } from '@/composables/accountsComposable'
import { ref } from 'vue'

const { checking_accounts, cc_accounts, savings_accounts, investment_accounts, loan_accounts } = useAccounts()
const add_account_link = ref("/accounts/add")
</script>