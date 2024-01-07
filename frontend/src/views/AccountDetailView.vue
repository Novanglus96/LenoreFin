<template>
    <div>
        <v-row class="pa-1 ga-1" no-gutters>
            <v-col class="rounded">
                <v-toolbar density="compact" color="accent" rounded>
                    <v-toolbar-title>Account Name</v-toolbar-title>
                    <span class="text-subtitle-2 text-black">Balance:</span> <span class="text-subtitle">$1000.00</span>
                    <v-spacer></v-spacer>
                    <v-btn icon>
                        <v-icon>mdi-cash-edit</v-icon>
                    </v-btn>

                    <v-btn icon>
                        <v-icon>mdi-application-edit</v-icon>
                    </v-btn>

                    <v-btn icon>
                        <v-icon color="red">mdi-bank-remove</v-icon>
                    </v-btn>
                </v-toolbar>
            </v-col>
        </v-row>
        <v-row class="pa-1 ga-1" no-gutters>
            <v-col class="rounded text-center">
                <AccountForecastWidget/>
            </v-col>
        </v-row>
        <v-row class="pa-1 ga-1" no-gutters>
            <v-col class="rounded bg-white">
                <v-toolbar density="compact" color="accent" rounded elevation="2">
                    <v-spacer></v-spacer>
                        <span class="text-subtitle-2 text-black">Statement Ending:</span> <span class="text-subtitle-2">1/1/24</span>
                    <v-spacer></v-spacer>
                        <span class="text-subtitle-2 text-black">Last Statement:</span> <span class="text-subtitle-2">$1000.00</span>
                    <v-spacer></v-spacer>
                        <span class="text-subtitle-2 text-black">Rewards:</span> <span class="text-subtitle-2">$10.00</span>
                    <v-spacer></v-spacer>
                </v-toolbar>
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