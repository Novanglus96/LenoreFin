<template>
    <div>
        <v-row class="pa-1 ga-1" no-gutters>
            <v-col class="rounded">
                <ForecastHeaderWidget @update-account="updateAccount"/>
            </v-col>
        </v-row>
        <v-row class="pa-1 ga-1" no-gutters>
            <v-col class="rounded text-center">
                <AccountForecastWidget :key="account_id" :account="account_id" :start_integer="0" :end_integer="90" v-if="account_id"/>
            </v-col>
        </v-row>
        <v-row class="pa-1 ga-1 rounded" no-gutters>
            <v-col class="rounded">
                <AccountTransactionsWidget :key="account_id" :account="account_id" :maxdays="90" :forecast="true" v-if="account_id"/>
            </v-col>
        </v-row>
    </div>
</template>
<script setup>
import AccountForecastWidget from '@/components/AccountForecastWidget.vue'
import AccountTransactionsWidget from '@/components/AccountTransactionsWidget.vue'
import ForecastHeaderWidget from '@/components/ForecastHeaderWidget.vue'
import { ref } from 'vue'

const account_id = ref(null)

const updateAccount = (account) => {
    account_id.value = account
}
</script>