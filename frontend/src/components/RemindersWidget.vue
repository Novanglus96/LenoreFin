<template>
    <v-card
        variant="outlined"
        :elevation="4"
        class="bg-white"
    >
        <template v-slot:append>
            <v-menu location="start">
                <template v-slot:activator="{ props }">
                    <v-btn
                    icon="mdi-cog"
                    flat
                    size="xs"
                    v-bind="props"
                    >
                    </v-btn>
                </template>
                <v-card width="100">
                    <v-card-text>Test</v-card-text>
                </v-card>
            </v-menu>
        </template>
        <template v-slot:title>
            <span class="text-subtitle-2 text-accent" v-if="!props.allowEdit">Upcoming Reminders</span>
            <span class="text-subtitle-2 text-accent" v-else>Reminders</span>
        </template>
        <template v-slot:text>
            <div v-if="props.allowEdit">
                <v-tooltip text="Edit Reminder" location="top">
                    <template v-slot:activator="{ props }">
                        <v-btn icon="mdi-bell-cog" flat :disabled="selected && selected.length === 0 || selected.length > 1" variant="plain" @click="reminderEditFormDialog = true" v-bind="props"></v-btn>
                    </template>
                </v-tooltip>
                <ReminderForm v-model="reminderEditFormDialog" @add-reminder="clickAddReminder" @edit-reminder="clickEditReminder" :isEdit="true" @update-dialog="updateEditDialog" :passedFormData="editReminder"/>
            
                <v-tooltip text="Remove Reminder(s)" location="top">
                    <template v-slot:activator="{ props }">
                        <v-btn icon="mdi-bell-remove" flat :disabled="selected && selected.length === 0" variant="plain" color="error" v-bind="props" @click="showDeleteDialog = true"></v-btn>
                    </template>
                </v-tooltip>
                <v-dialog width="500" v-model="showDeleteDialog">
                        <v-card title="Dialog">
                        <v-card-text>
                            Are you sure you want to delete these {{ selected.length }} reminders?
                        </v-card-text>

                        <v-card-actions>
                            <v-spacer></v-spacer>

                            <v-btn
                            text="Confirm"
                            @click="clickRemoveReminder(selected); showDeleteDialog = false"
                            ></v-btn>
                        </v-card-actions>
                        </v-card>
                </v-dialog>
                <v-tooltip text="Add New Reminder" location="top">
                    <template v-slot:activator="{ props }">
                        <v-btn icon="mdi-bell-plus" flat variant="plain" color="success" @click="reminderAddFormDialog = true" v-bind="props"></v-btn>
                    </template>
                </v-tooltip>
                <ReminderForm v-model="reminderAddFormDialog" @add-reminder="clickAddReminder" @edit-reminder="clickEditReminder" :isEdit="false" @update-dialog="updateAddDialog" :passedFormData="blankForm"/>
            </div>
            <vue3-datatable 
                :rows="reminders"
                :columns="columns"
                :loading="isLoading"
                :totalRows="reminders ? reminders.length : 0"
                :isServerMode="false"
                :pageSize="props.allowEdit ? 20 : 5"
                :hasCheckbox="props.allowEdit"
                :stickyHeader="true"
                noDataContent="No reminders"
                ref="reminders_table"
                :height="props.allowEdit ? '880px' : '220px'"
                skin="bh-table-striped bh-table-compact"
                :pageSizeOptions="props.allowEdit ? [5, 10, 20] : [5]"
                :showPageSize="props.allowEdit"
                paginationInfo="Showing {0} to {1} of {2} reminders"
                class="alt-pagination"
                @rowSelect="rowSelected"
            ><!--height="280px"-->
                <template #next_date="row"><!-- eslint-disable-line -->
                    <span class="font-weight-bold text-black">{{ row.value.next_date }}</span>
                </template>
                <template #amount="row"><!-- eslint-disable-line -->
                    <span :class="getClassForMoney(row.value.amount)">${{ row.value.amount }}</span>
                </template>
                <template #description="row"><!-- eslint-disable-line -->
                    <span class="font-weight-bold text-black">{{ row.value.description }}</span>
                </template>
            </vue3-datatable>
        </template>
    </v-card>
</template>
<script setup>
import Vue3Datatable from '@bhplugin/vue3-datatable'
import '@bhplugin/vue3-datatable/dist/style.css'
import { defineProps, ref } from 'vue'
import { useReminders } from '@/composables/remindersComposable'
import ReminderForm from '@/components/ReminderForm.vue'

const today = new Date();
const year = today.getFullYear();
const month = String(today.getMonth() + 1).padStart(2, '0');
const day = String(today.getDate()).padStart(2, '0');
const formattedDate = `${year}-${month}-${day}`;
const start_date = ref(formattedDate)
const selected = ref([])
const showDeleteDialog = ref(false)
const reminderAddFormDialog = ref(false)
const reminderEditFormDialog = ref(false)
const { reminders, isLoading, removeReminder } = useReminders()
const props = defineProps({
    allowEdit: {
        type: Boolean,
        default: false
    }
})

const editReminder = ref({
    id: 0,
    tag: {
        id: null
    },
    amount: null,
    reminder_source_account: {
        id: null
    },
    reminder_destination_account: {
        id: null
    },
    description: null,
    transaction_type: {
        id: 1
    },
    start_date: start_date.value,
    next_date: start_date.value,
    end_date: null,
    repeat: {
        id: null
    },
    auto_add: true
})

const rowSelected = () => {
    selected.value = []
    let selectedrows = reminders_table.value.getSelectedRows()
    for (const selectedrow of selectedrows) {
        selected.value.push(selectedrow.id)
        editReminder.value = selectedrow
    }

}
const blankForm = ref({
    id: 0,
    tag: {
        id: null
    },
    amount: null,
    reminder_source_account: {
        id: null
    },
    reminder_destination_account: {
        id: null
    },
    description: null,
    transaction_type: {
        id: 1
    },
    start_date: start_date.value,
    next_date: start_date.value,
    end_date: null,
    repeat: {
        id: null
    },
    auto_add: true
})
const reminders_table = ref(null);
const columns = ref([
    { field: 'next_date', title: 'Date', type: 'date', width: '120px' },
    { field: 'amount', title: 'Amount', type: 'number', width: '100px' },
    { field: 'description', title: 'Reminder' },
])
const getClassForMoney = (amount) => {
    let color = ''
    let font = ''

    font = "font-weight-bold"
    if (amount < 0) {
        color = 'text-red'
    } else {
        color = 'text-green'
    }

    return color + ' ' + font
}

const clickRemoveReminder = async (reminders) => {
    reminders.forEach(reminder => {
        removeReminder(reminder)
        selected.value = []
    })
}

const updateAddDialog = () => {
    reminderAddFormDialog.value = false
}

const updateEditDialog = () => {
    reminderEditFormDialog.value = false
}

</script>
<style>
.alt-pagination .bh-pagination .bh-page-item {
       background-color: #06966A;
       color: white;
}
</style>