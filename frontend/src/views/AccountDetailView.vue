<template>
    <div>
        <v-row class="pa-1 ga-1" no-gutters>
            <v-col class="rounded">
                <AccountHeaderWidget :key="account_id" :account="account_id"/>
            </v-col>
        </v-row>
        <v-row class="pa-1 ga-1" no-gutters>
            <v-col class="rounded text-center">
                <AccountForecastWidget/>
            </v-col>
        </v-row>
        <v-row class="pa-1 ga-1 rounded" no-gutters>
            <v-col class="rounded">
                <AccountTransactionsWidget :key="account_id" :account="account_id"/>
            </v-col>
        </v-row>
    </div>
</template>
<script setup>
import AccountForecastWidget from '@/components/AccountForecastWidget.vue'
import AccountTransactionsWidget from '@/components/AccountTransactionsWidget.vue'
import AccountHeaderWidget from '@/components/AccountHeaderWidget.vue'
import { useRoute } from 'vue-router'
import { ref, watch } from 'vue'

const route = useRoute()
const account_id = ref(route.params.accountID)

watch(() => route.params.accountID, (newAccountID) => {
    // Update the account_id ref with the new value
    account_id.value = newAccountID
})

</script>