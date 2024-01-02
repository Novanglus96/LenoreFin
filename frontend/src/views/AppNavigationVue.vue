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
                            <v-list-item-title>{{ account.account_name }} </v-list-item-title>
                            <v-list-item-subtitle>{{ account.balance }}</v-list-item-subtitle>
                        </v-list-item>
                        <v-divider></v-divider>
                        <v-list-item prepend-icon="mdi-plus-circle" base-color="accent">
                            <v-list-item-title>Add Account</v-list-item-title>
                        </v-list-item>
                    </v-list>
                </v-menu>
                <v-menu>
                    <template v-slot:activator="{ props }">
                        <v-btn prepend-icon="mdi-piggy-bank" v-bind="props">Savings</v-btn>
                    </template>

                    <v-list>
                        <v-list-item v-for="(account, i) in savings_accounts" :key="i">
                            <v-list-item-title>{{ account.account_name }} </v-list-item-title>
                            <v-list-item-subtitle>{{ account.balance }}</v-list-item-subtitle>
                        </v-list-item>
                        <v-divider></v-divider>
                        <v-list-item prepend-icon="mdi-plus-circle" base-color="accent">
                            <v-list-item-title>Add Account</v-list-item-title>
                        </v-list-item>
                    </v-list>
                </v-menu>
                <v-menu>
                    <template v-slot:activator="{ props }">
                        <v-btn prepend-icon="mdi-credit-card" v-bind="props">Credit Cards</v-btn>
                    </template>

                    <v-list>
                        <v-list-item v-for="(account, i) in cc_accounts" :key="i">
                            <v-list-item-title>{{ account.account_name }} </v-list-item-title>
                            <v-list-item-subtitle>{{ account.balance }}</v-list-item-subtitle>
                        </v-list-item>
                        <v-divider></v-divider>
                        <v-list-item prepend-icon="mdi-plus-circle" base-color="accent">
                            <v-list-item-title>Add Account</v-list-item-title>
                        </v-list-item>
                    </v-list>
                </v-menu>
                <v-menu>
                    <template v-slot:activator="{ props }">
                        <v-btn prepend-icon="mdi-finance" v-bind="props">Investments</v-btn>
                    </template>

                    <v-list>
                        <v-list-item v-for="(account, i) in investment_accounts" :key="i">
                            <v-list-item-title>{{ account.account_name }} </v-list-item-title>
                            <v-list-item-subtitle>{{ account.balance }}</v-list-item-subtitle>
                        </v-list-item>
                        <v-divider></v-divider>
                        <v-list-item prepend-icon="mdi-plus-circle" base-color="accent">
                            <v-list-item-title>Add Account</v-list-item-title>
                        </v-list-item>
                    </v-list>
                </v-menu>
                <v-menu>
                    <template v-slot:activator="{ props }">
                        <v-btn prepend-icon="mdi-car-back" v-bind="props">Loans</v-btn>
                    </template>

                    <v-list>
                        <v-list-item v-for="(account, i) in loan_accounts" :key="i">
                            <v-list-item-title>{{ account.account_name }} </v-list-item-title>
                            <v-list-item-subtitle>{{ account.balance }}</v-list-item-subtitle>
                        </v-list-item>
                        <v-divider></v-divider>
                        <v-list-item prepend-icon="mdi-plus-circle" base-color="accent">
                            <v-list-item-title>Add Account</v-list-item-title>
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
        id: 1,
        account_name: 'Checking Account # 1',
        balance: "$1,000"
    },
    {
        id: 2,
        account_name: 'Checking Account # 2',
        balance: "$1,100"
    },
    {
        id: 3,
        account_name: 'Checking Account # 3',
        balance: "$1,200"
    },
])
const savings_accounts = ref([
    {
        id: 1,
        account_name: 'Savings Account # 1',
        balance: "$2,000"
    },
    {
        id: 2,
        account_name: 'Savings Account # 2',
        balance: "$2,100"
    },
    {
        id: 3,
        account_name: 'Savings Account # 3',
        balance: "-$2,200"
    },
])
const cc_accounts = ref([
    {
        id: 1,
        account_name: 'Credit Card # 1',
        balance: "$3,000"
    },
    {
        id: 2,
        account_name: 'Credit Card # 2',
        balance: "$3,100"
    },
    {
        id: 3,
        account_name: 'Credit Card # 3',
        balance: "-$3,200"
    },
])
const investment_accounts = ref([
    {
        id: 1,
        account_name: 'Investment Account # 1',
        balance: "$4,000"
    },
    {
        id: 2,
        account_name: 'Investment Account # 2',
        balance: "$4,100"
    },
    {
        id: 3,
        account_name: 'Investment Account # 3',
        balance: "-$4,200"
    },
])
const loan_accounts = ref([
    {
        id: 1,
        account_name: 'Loan Account # 1',
        balance: "$5,000"
    },
    {
        id: 2,
        account_name: 'Loan Account # 2',
        balance: "$5,100"
    },
    {
        id: 3,
        account_name: 'Loan Account # 3',
        balance: "-$5,200"
    },
])
const planning_menu = ref([
    {
        title: 'Pay',
        link: "/"
    },
    {
        title: 'Expenses',
        link: "/"
    },
    {
        title: 'Contributions',
        link: "/"
    },
    {
        title: 'Retirement',
        link: "/"
    },
    {
        title: 'Christmas',
        link: "/"
    },
    {
        title: 'Notes',
        link: "/"
    },
])
</script>
