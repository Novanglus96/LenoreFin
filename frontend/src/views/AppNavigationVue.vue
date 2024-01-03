<template>
    <v-app-bar color="primary" density="compact">
        <v-btn icon="mdi-view-dashboard" to="/"></v-btn>
        <v-menu>
            <template v-slot:activator="{ props }">
                <v-btn prepend-icon="mdi-checkbook" v-bind="props">Checking</v-btn>
            </template>

            <v-list>
                <v-list-item title="No Accounts" v-if="checking_accounts.length == 0"></v-list-item>
                <v-list-item v-for="(account, i) in checking_accounts" :key="i" :to="'/accounts/' + account.id" prepend-icon="mdi-checkbook" color="green" v-else>
                    <v-list-item-title>{{ account.account_name }} </v-list-item-title>
                    <v-list-item-subtitle><span :class="account.balance >= 0 ? 'text-green' : 'text-red'">${{ account.balance }}</span></v-list-item-subtitle>
                </v-list-item>
                <v-divider></v-divider>
                <v-list-item prepend-icon="mdi-plus-circle" base-color="accent" :to="add_account_link">
                    <v-list-item-title>Add Account</v-list-item-title>
                </v-list-item>
            </v-list>
        </v-menu>
        <v-menu>
            <template v-slot:activator="{ props }">
                <v-btn prepend-icon="mdi-piggy-bank" v-bind="props">Savings</v-btn>
            </template>

            <v-list>
                <v-list-item title="No Accounts" v-if="savings_accounts.length == 0"></v-list-item>
                <v-list-item v-for="(account, i) in savings_accounts" :key="i" :to="'/accounts/' + account.id" prepend-icon="mdi-piggy-bank" v-else>
                    <v-list-item-title>{{ account.account_name }} </v-list-item-title>
                    <v-list-item-subtitle><span :class="account.balance >= 0 ? 'text-green' : 'text-red'">${{ account.balance }}</span></v-list-item-subtitle>
                </v-list-item>
                <v-divider></v-divider>
                <v-list-item prepend-icon="mdi-plus-circle" base-color="accent" :to="add_account_link">
                    <v-list-item-title>Add Account</v-list-item-title>
                </v-list-item>
            </v-list>
        </v-menu>
        <v-menu>
            <template v-slot:activator="{ props }">
                <v-btn prepend-icon="mdi-credit-card" v-bind="props">Credit Cards</v-btn>
            </template>

            <v-list>
                <v-list-item title="No Accounts" v-if="cc_accounts.length == 0"></v-list-item>
                <v-list-item v-for="(account, i) in cc_accounts" :key="i" :to="'/accounts/' + account.id" prepend-icon="mdi-credit-card" v-else>
                    <v-list-item-title>{{ account.account_name }} </v-list-item-title>
                    <v-list-item-subtitle><span :class="account.balance >= 0 ? 'text-green' : 'text-red'">${{ account.balance }}</span></v-list-item-subtitle>
                </v-list-item>
                <v-divider></v-divider>
                <v-list-item prepend-icon="mdi-plus-circle" base-color="accent" :to="add_account_link">
                    <v-list-item-title>Add Account</v-list-item-title>
                </v-list-item>
            </v-list>
        </v-menu>
        <v-menu>
            <template v-slot:activator="{ props }">
                <v-btn prepend-icon="mdi-finance" v-bind="props">Investments</v-btn>
            </template>

            <v-list>
                <v-list-item title="No Accounts" v-if="investment_accounts.length == 0"></v-list-item>
                <v-list-item v-for="(account, i) in investment_accounts" :key="i" :to="'/accounts/' + account.id" prepend-icon="mdi-finance" v-else>
                    <v-list-item-title>{{ account.account_name }} </v-list-item-title>
                    <v-list-item-subtitle><span :class="account.balance >= 0 ? 'text-green' : 'text-red'">${{ account.balance }}</span></v-list-item-subtitle>
                </v-list-item>
                <v-divider></v-divider>
                <v-list-item prepend-icon="mdi-plus-circle" base-color="accent" :to="add_account_link">
                    <v-list-item-title>Add Account</v-list-item-title>
                </v-list-item>
            </v-list>
        </v-menu>
        <v-menu>
            <template v-slot:activator="{ props }">
                <v-btn prepend-icon="mdi-car-back" v-bind="props">Loans</v-btn>
            </template>

            <v-list>
                <v-list-item title="No Accounts" v-if="loan_accounts.length == 0"></v-list-item>
                <v-list-item v-for="(account, i) in loan_accounts" :key="i" :to="'/accounts/' + account.id" prepend-icon="mdi-car-back" v-else>
                    <v-list-item-title>{{ account.account_name }} </v-list-item-title>
                    <v-list-item-subtitle><span :class="account.balance >= 0 ? 'text-green' : 'text-red'">${{ account.balance }}</span></v-list-item-subtitle>
                </v-list-item>
                <v-divider></v-divider>
                <v-list-item prepend-icon="mdi-plus-circle" base-color="accent" :to="add_account_link">
                    <v-list-item-title>Add Account</v-list-item-title>
                </v-list-item>
            </v-list>
        </v-menu>
        <v-btn prepend-icon="mdi-chart-bar" to="/forecast">Forecast</v-btn>
        <v-btn prepend-icon="mdi-bell" to="/reminders">Reminders</v-btn>
        <v-menu>
            <template v-slot:activator="{ props }">
                <v-btn prepend-icon="mdi-folder" v-bind="props">Planning</v-btn>
            </template>

            <v-list>
                <v-list-item v-for="(planning_item, i) in planning_menu" :key="i" :prepend-icon="planning_item.icon" :to="planning_item.link">
                    <v-list-item-title>{{ planning_item.title }}</v-list-item-title>
                </v-list-item>
            </v-list>
        </v-menu>
        <v-btn prepend-icon="mdi-tag" to="/tags">Tags</v-btn>
        <v-btn prepend-icon="mdi-cog" to="/settings">Settings</v-btn>
        <v-spacer></v-spacer>
        <v-btn icon="mdi-calculator" to="/calculator"></v-btn>
    </v-app-bar>
</template>
<script setup>
import { ref } from 'vue'

const add_account_link = ref("/accounts/add")
const checking_accounts = ref([])
const savings_accounts = ref([])
const cc_accounts = ref([])
const investment_accounts = ref([])
const loan_accounts = ref([])
const planning_menu = ref([
    {
        title: 'Pay',
        link: "/planning/pay",
        icon: "mdi-checkbook"
    },
    {
        title: 'Expenses',
        link: "/planning/expenses",
        icon: "mdi-cash"
    },
    {
        title: 'Contributions',
        link: "/planning/contributions",
        icon: "mdi-pail"
    },
    {
        title: 'Retirement',
        link: "/planning/retirement",
        icon: "mdi-piggy-bank"
    },
    {
        title: 'Christmas',
        link: "/planning/christmas",
        icon: "mdi-pine-tree"
    },
    {
        title: 'Notes',
        link: "/planning/notes",
        icon: "mdi-note"
    },
])
</script>
