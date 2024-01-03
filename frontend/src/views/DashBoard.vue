<template>
    <div>
        <v-row class="bg-accent pa-1 ga-1">
            <v-col class="bg-white rounded custom-height text-center">
                <MainExpensesWidget />
            </v-col>
            <v-col class="bg-white rounded custom-height text-center"> <KidsExpensesWidget/> </v-col>
            <v-col class="bg-white rounded custom-height text-center"> <MoneyPileExpensesWidget/> </v-col>
        </v-row>
        <v-row class="bg-accent pa-1 ga-1 rounded">
            <v-col class="bg-white rounded"> <RemindersWidget/> </v-col>
        </v-row>
        <v-row class="bg-accent pa-1 ga-1 rounded">
            <v-col class="bg-white rounded"> <UpcomingTransactionsWidget/> </v-col>
        </v-row>
    </div>
</template>
<script setup>
import KidsExpensesWidget from '@/components/KidsExpensesWidget.vue'
import MainExpensesWidget from '@/components/MainExpensesWidget.vue'
import MoneyPileExpensesWidget from '@/components/MoneyPileExpensesWidget.vue'
import RemindersWidget from '@/components/RemindersWidget.vue'
import UpcomingTransactionsWidget from '@/components/UpcomingTransactionsWidget.vue'

</script>
<style scoped>
.custom-height {
    height: 350px;
    /* Adjust the height as needed */
    overflow-y: hidden;
    /* Add this if you want a vertical scrollbar for overflow */
}
</style>