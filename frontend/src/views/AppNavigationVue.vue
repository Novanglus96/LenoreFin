<template>
    <div>
    <v-app-bar color="primary" density="compact">
        <v-app-bar-nav-icon><v-img
                    :width="32"
                    aspect-ratio="1/1"
                    cover
                    src="Logo.png"
                ></v-img></v-app-bar-nav-icon>
        <v-app-bar-title>Money v1.0</v-app-bar-title>
    </v-app-bar>
    <v-navigation-drawer color="accent" rail permanent v-if="!mdAndUp">
        <v-list density="compact" nav>
            <v-list-item prepend-icon="mdi-view-dashboard" to="/"></v-list-item>
            <v-list-item prepend-icon="mdi-bank" to="/accounts" ></v-list-item>
            <v-list-item prepend-icon="mdi-chart-bar" to="/forecast"></v-list-item>
            <v-list-item prepend-icon="mdi-bell" to="/reminders"></v-list-item>
            <v-list-item prepend-icon="mdi-folder" to="/planning"></v-list-item>
            <v-list-item prepend-icon="mdi-tag" to="/tags"></v-list-item>
            <v-list-item prepend-icon="mdi-cog" to="/settings"></v-list-item>
        </v-list>
    </v-navigation-drawer>
    <v-navigation-drawer color="accent" rail permanent v-if="mdAndUp">
        <v-list density="compact" nav>
            <v-list-item prepend-icon="mdi-view-dashboard" to="/"></v-list-item>
            <v-list-item
            prepend-icon="mdi-bank"
            @click="nav_toggle = true"
            ></v-list-item>

            <v-list-item prepend-icon="mdi-chart-bar" to="/forecast"></v-list-item>
            <v-list-item prepend-icon="mdi-bell" to="/reminders"></v-list-item>
            <v-list-item prepend-icon="mdi-folder" @click="nav_toggle = false"></v-list-item>
            <v-list-item prepend-icon="mdi-tag" to="/tags"></v-list-item>
            <v-list-item prepend-icon="mdi-cog" to="/settings"></v-list-item>
        </v-list>
        </v-navigation-drawer>

        <v-navigation-drawer permanent widht="250" color="primary" v-if="mdAndUp">
        <v-list density="compact" nav v-if="nav_toggle">
            <v-list-item prepend-icon="mdi-plus-circle" base-color="accent" :to="add_account_link">
                <v-list-item-title>Add Account</v-list-item-title>
            </v-list-item>
        </v-list>
        <v-list density="compact" nav v-if="nav_toggle">
            <v-list-subheader><v-icon icon="mdi-checkbook"></v-icon> CHECKING</v-list-subheader>
            <v-list-item title="No Accounts" v-if="checking_accounts.length == 0"></v-list-item>
            <v-list-item v-for="(account, i) in checking_accounts" :key="i" :to="'/accounts/' + account.id" v-else>
                <v-list-item-title>{{ account.account_name }} </v-list-item-title>
                <v-list-item-subtitle><span :class="account.balance >= 0 ? 'text-green font-weight-bold' : 'text-red font-weight-bold'">${{ account.balance }}</span></v-list-item-subtitle>
            </v-list-item>
        </v-list>
        <v-divider></v-divider>
        <v-list density="compact" nav v-if="nav_toggle">
            <v-list-subheader><v-icon icon="mdi-piggy-bank"></v-icon> SAVINGS</v-list-subheader>
            <v-list-item title="No Accounts" v-if="savings_accounts.length == 0"></v-list-item>
            <v-list-item v-for="(account, i) in savings_accounts" :key="i" :to="'/accounts/' + account.id" v-else>
                <v-list-item-title>{{ account.account_name }} </v-list-item-title>
                <v-list-item-subtitle><span :class="account.balance >= 0 ? 'text-green font-weight-bold' : 'text-red font-weight-bold'">${{ account.balance }}</span></v-list-item-subtitle>
            </v-list-item>
        </v-list>
        <v-divider></v-divider>
        <v-list density="compact" nav v-if="nav_toggle">
            <v-list-subheader><v-icon icon="mdi-credit-card"></v-icon> CREDIT CARD</v-list-subheader>
            <v-list-item title="No Accounts" v-if="cc_accounts.length == 0"></v-list-item>
            <v-list-item v-for="(account, i) in cc_accounts" :key="i" :to="'/accounts/' + account.id" v-else>
                <v-list-item-title>{{ account.account_name }} </v-list-item-title>
                <v-list-item-subtitle><span :class="account.balance >= 0 ? 'text-green font-weight-bold' : 'text-red font-weight-bold'">${{ account.balance }}</span></v-list-item-subtitle>
            </v-list-item>
        </v-list>
        <v-divider></v-divider>
        <v-list density="compact" nav v-if="nav_toggle">
            <v-list-subheader><v-icon icon="mdi-finance"></v-icon> INVESTMENT</v-list-subheader>
            <v-list-item title="No Accounts" v-if="investment_accounts.length == 0"></v-list-item>
            <v-list-item v-for="(account, i) in investment_accounts" :key="i" :to="'/accounts/' + account.id" v-else>
                <v-list-item-title>{{ account.account_name }} </v-list-item-title>
                <v-list-item-subtitle><span :class="account.balance >= 0 ? 'text-green font-weight-bold' : 'text-red font-weight-bold'">${{ account.balance }}</span></v-list-item-subtitle>
            </v-list-item>
        </v-list>
        <v-divider></v-divider>
        <v-list density="compact" nav v-if="nav_toggle">
            <v-list-subheader><v-icon icon="mdi-car-back"></v-icon> LOAN</v-list-subheader>
            <v-list-item title="No Accounts" v-if="loan_accounts.length == 0"></v-list-item>
            <v-list-item v-for="(account, i) in loan_accounts" :key="i" :to="'/accounts/' + account.id" v-else>
                <v-list-item-title>{{ account.account_name }} </v-list-item-title>
                <v-list-item-subtitle><span :class="account.balance >= 0 ? 'text-green font-weight-bold' : 'text-red font-weight-bold'">${{ account.balance }}</span></v-list-item-subtitle>
            </v-list-item>
        </v-list>
        <v-list density="compact" nav v-if="!nav_toggle">
            <v-list-subheader><v-icon icon="mdi-folder"></v-icon> PLANNING</v-list-subheader>
            <v-list-item v-for="(planning_item, i) in planning_menu" :key="i" :prepend-icon="planning_item.icon" :to="planning_item.link">
                <v-list-item-title>{{ planning_item.title }}</v-list-item-title>
            </v-list-item>
        </v-list>
    </v-navigation-drawer>
</div>
</template>
<script setup>
import { ref } from 'vue'
import { useAccounts } from '@/composables/accountsComposable'
import { useDisplay } from 'vuetify'

const { mdAndUp } = useDisplay()
const nav_toggle = ref(true)
const { checking_accounts, cc_accounts, savings_accounts, investment_accounts, loan_accounts } = useAccounts()
const add_account_link = ref("/accounts/add")
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
    {
        title: 'Calculator',
        link: "/planning/calculator",
        icon: "mdi-calculator"
    },
])
</script>
