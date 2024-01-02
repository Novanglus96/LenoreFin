<template>
    <v-app>
        <v-container>
            <v-app-bar color="primary">
                <v-menu>
                    <template v-slot:activator="{ props }">
                        <v-btn prepend-icon="mdi-checkbook" v-bind="props">Checking</v-btn>
                    </template>

                    <v-list>
                        <v-list-item v-for="(account, i) in checking_accounts" :key="i">
                            <v-list-item-title>{{ account.account_name }} {{ account.balance }} </v-list-item-title>
                        </v-list-item>
                    </v-list>
                </v-menu>
                <v-menu>
                    <template v-slot:activator="{ props }">
                        <v-btn prepend-icon="mdi-piggy-bank" v-bind="props">Savings</v-btn>
                    </template>

                    <v-list>
                        <v-list-item v-for="(account, i) in savings_accounts" :key="i">
                            <v-list-item-title>{{ account.account_name }} {{ account.balance }}</v-list-item-title>
                        </v-list-item>
                    </v-list>
                </v-menu>
                <v-menu>
                    <template v-slot:activator="{ props }">
                        <v-btn prepend-icon="mdi-credit-card" v-bind="props">Credit Cards</v-btn>
                    </template>

                    <v-list>
                        <v-list-item v-for="(account, i) in cc_accounts" :key="i">
                            <v-list-item-title>{{ account.account_name }} {{ account.balance }}</v-list-item-title>
                        </v-list-item>
                    </v-list>
                </v-menu>
                <v-menu>
                    <template v-slot:activator="{ props }">
                        <v-btn prepend-icon="mdi-finance" v-bind="props">Investments</v-btn>
                    </template>

                    <v-list>
                        <v-list-item v-for="(account, i) in investment_accounts" :key="i">
                            <v-list-item-title>{{ account.account_name }} {{ account.balance }}</v-list-item-title>
                        </v-list-item>
                    </v-list>
                </v-menu>
                <v-menu>
                    <template v-slot:activator="{ props }">
                        <v-btn prepend-icon="mdi-car-back" v-bind="props">Loans</v-btn>
                    </template>

                    <v-list>
                        <v-list-item v-for="(account, i) in loan_accounts" :key="i">
                            <v-list-item-title>{{ account.account_name }} {{ account.balance }}</v-list-item-title>
                        </v-list-item>
                    </v-list>
                </v-menu>
                <v-btn prepend-icon="mdi-chart-bar">Forecast</v-btn>
                <v-btn prepend-icon="mdi-bell">Reminders</v-btn>
                <v-menu>
                    <template v-slot:activator="{ props }">
                        <v-btn prepend-icon="mdi-folder" v-bind="props">Planning</v-btn>
                    </template>

                    <v-list>
                        <v-list-item v-for="(planning_item, i) in planning_menu" :key="i">
                            <v-list-item-title>{{ planning_item.title }}</v-list-item-title>
                        </v-list-item>
                    </v-list>
                </v-menu>
                <v-btn prepend-icon="mdi-tag">Tags</v-btn>
                <v-btn prepend-icon="mdi-cog">Settings</v-btn>
                <v-spacer></v-spacer>
                <v-btn icon="mdi-calculator"></v-btn>
            </v-app-bar>
        </v-container>
    </v-app>
</template>
<script setup>
import { ref } from 'vue'
const checking_accounts = ref([
    {
        account_name: 'Checking Account',
        balance: "$1,000"
    },
])
const savings_accounts = ref([
    {
        account_name: 'Savings Account',
        balance: "$2,000"
    },
])
const cc_accounts = ref([
    {
        account_name: 'Credit Card',
        balance: "$3,000"
    },
])
const investment_accounts = ref([
    {
        account_name: 'Investment Account',
        balance: "$4,000"
    },
])
const loan_accounts = ref([
    {
        account_name: 'Loan Account',
        balance: "$5,000"
    },
])
const planning_menu = ref([
    {
        title: 'Pay'
    },
    {
        title: 'Expenses'
    },
    {
        title: 'Contributions'
    },
    {
        title: 'Retirement'
    },
    {
        title: 'Christmas'
    },
    {
        title: 'Notes'
    },
])
</script>
