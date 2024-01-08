<template>
    <div>
        <v-row class="pa-1 ga-1" no-gutters>
            <v-col class="rounded">
                <v-card
                    variant="outlined"
                    :elevation="4"
                    class="bg-accent"
                >
                    <template v-slot:append>
                        <v-btn icon="mdi-cash-edit" flat variant="plain"/>
                        <v-btn icon="mdi-application-edit" flat variant="plain"/>
                        <v-btn icon="mdi-bank-remove" color="red" flat variant="plain"/>
                    </template>
                    <template v-slot:title>
                        Account Name
                    </template>
                    <template v-slot:subtitle>
                        $1000.00
                    </template>
                    <template v-slot:text>
                        <v-row desnity="compact">
                            <v-col col="2" class="text-right text-black font-weight-bold">Statement Ending:</v-col><v-col col="2">1/1/24</v-col>
                            <v-col col="2" class="text-right text-black font-weight-bold">Last Statement:</v-col><v-col col="2">$1000.00</v-col>
                            <v-col col="2" class="text-right text-black font-weight-bold">Rewards:</v-col><v-col col="2">$10.00</v-col>
                            <v-col col="2" class="text-right text-black font-weight-bold">Available Credit:</v-col><v-col col="2">$1000.00</v-col>
                        </v-row>
                    </template>
                </v-card>
            </v-col>
        </v-row>
        <v-row class="pa-1 ga-1" no-gutters>
            <v-col class="rounded text-center">
                <AccountForecastWidget/>
            </v-col>
        </v-row>
        <v-row class="pa-1 ga-1 rounded" no-gutters>
            <v-col class="rounded">
                <AccountTransactionsWidget/>
            </v-col>
        </v-row>
    </div>
</template>
<script setup>
import AccountForecastWidget from '@/components/AccountForecastWidget.vue'
import AccountTransactionsWidget from '@/components/AccountTransactionsWidget.vue'

</script>