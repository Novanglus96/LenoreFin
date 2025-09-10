<template>
  <v-card variant="outlined" :elevation="4" class="bg-white">
    <template v-slot:title>
      <span class="text-subtitle-2 text-secondary" v-if="!props.allowEdit">
        Upcoming Reminders
      </span>
      <span class="text-subtitle-2 text-secondary" v-else>Reminders</span>
    </template>
    <template v-slot:text>
      <div v-if="props.allowEdit">
        <v-tooltip text="Edit Reminder" location="top">
          <template v-slot:activator="{ props }">
            <v-btn
              icon="mdi-bell-cog"
              flat
              :disabled="
                (selected && selected.length === 0) || selected.length > 1
              "
              variant="plain"
              @click="reminderEditFormDialog = true"
              v-bind="props"
            ></v-btn>
          </template>
        </v-tooltip>
        <ReminderForm
          v-model="reminderEditFormDialog"
          :isEdit="true"
          @update-dialog="updateEditDialog"
          :passedFormData="editReminder"
        />

        <v-tooltip text="Remove Reminder(s)" location="top">
          <template v-slot:activator="{ props }">
            <v-btn
              icon="mdi-bell-remove"
              flat
              :disabled="selected && selected.length === 0"
              variant="plain"
              color="error"
              v-bind="props"
              @click="showDeleteDialog = true"
            ></v-btn>
          </template>
        </v-tooltip>
        <v-dialog width="500" v-model="showDeleteDialog">
          <v-card title="Dialog">
            <v-card-text>
              Are you sure you want to delete these
              {{ selected.length }} reminders?
            </v-card-text>

            <v-card-actions>
              <v-spacer></v-spacer>

              <v-btn
                text="Confirm"
                @click="
                  clickRemoveReminder(selected);
                  showDeleteDialog = false;
                "
              ></v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
        <v-tooltip text="Add New Reminder" location="top">
          <template v-slot:activator="{ props }">
            <v-btn
              icon="mdi-bell-plus"
              flat
              variant="plain"
              color="success"
              @click="reminderAddFormDialog = true"
              v-bind="props"
            ></v-btn>
          </template>
        </v-tooltip>
        <ReminderForm
          v-model="reminderAddFormDialog"
          :isEdit="false"
          @update-dialog="updateAddDialog"
          :passedFormData="blankForm"
        />
      </div>
      <!-- Large Display View -->
      <vue3-datatable
        :rows="reminders"
        :columns="columns"
        :loading="isLoading"
        :totalRows="reminders ? reminders.length : 0"
        :isServerMode="false"
        :pageSize="props.allowEdit ? 20 : 5"
        :hasCheckbox="props.allowEdit"
        noDataContent="No reminders"
        ref="reminders_table"
        skin="bh-table-striped bh-table-compact"
        :pageSizeOptions="props.allowEdit ? [5, 10, 20] : [5]"
        :showPageSize="props.allowEdit"
        paginationInfo="Showing {0} to {1} of {2} reminders"
        class="alt-pagination"
        @rowSelect="rowSelected"
        :sortable="false"
        sortColumn="next_date"
        sortDirection="asc"
        v-if="!smAndDown"
      >
        <!--height="280px"-->
        <template #next_date="row">
          <span class="font-weight-bold text-black">
            {{ row.value.next_date }}
          </span>
        </template>
        <template #amount="row">
          <span :class="getClassForMoney(row.value.amount)">
            {{ formatCurrency(row.value.amount) }}
          </span>
        </template>
        <template #description="row">
          <span class="font-weight-bold text-black">
            {{ row.value.description }}
          </span>
        </template>
        <template #tag.tag_name="row">
          <v-icon icon="mdi-tag" color="black"></v-icon>
          <span class="font-weight-bold text-black">
            {{ row.value.tag.tag_name }}
          </span>
        </template>
        <template #end_date="row">
          <span class="font-weight-bold text-black">
            {{ row.value.end_date }}
          </span>
        </template>
        <template #repeat.repeat_name="row">
          <span class="font-weight-bold text-black">
            {{ row.value.repeat.repeat_name }}
          </span>
        </template>
      </vue3-datatable>
      <!-- Small Display View -->
      <v-list v-if="!isLoading && smAndDown" density="compact">
        <v-data-iterator
          :items="reminders"
          :loading="isLoading"
          items-per-page="5"
        >
          <template v-slot:default="{ items }">
            <template v-for="(item, i) in items" :key="i">
              <v-list-item class="border-thin" rounded elevation="1">
                <v-list-item-title class="font-weight-bold text-truncate">
                  {{ item.raw.description }}
                </v-list-item-title>
                <v-list-item-subtitle>
                  <v-container class="ma-0 pa-0 ga-0">
                    <v-row dense class="ma-0 pa-0 ga-0">
                      <v-col class="ma-0 pa-0 ga-0">
                        {{ item.raw.next_date }}
                      </v-col>
                      <v-col class="ma-0 pa-0 ga-0 text-right">
                        <span :class="getClassForMoney(item.raw.amount)">
                          {{ formatCurrency(item.raw.amount) }}
                        </span>
                      </v-col>
                    </v-row>
                    <v-row dense class="ma-0 pa-0 ga-0">
                      <v-col class="ma-0 pa-0 ga-0">
                        <v-tooltip text="Repeats" location="top">
                          <template #activator="{ props }">
                            <v-icon icon="mdi-repeat" v-bind="props"></v-icon>
                          </template>
                        </v-tooltip>
                        {{ item.raw.repeat.repeat_name }}
                      </v-col>
                      <v-col class="ma-0 pa-0 ga-0 text-right">
                        <v-tooltip text="End Date" location="top">
                          <template #activator="{ props }">
                            <v-icon
                              icon="mdi-timer-stop"
                              v-bind="props"
                            ></v-icon>
                          </template>
                        </v-tooltip>
                        {{ item.raw.end_date ? item.raw.end_date : "none" }}
                      </v-col>
                    </v-row>
                    <v-row dense class="ma-0 pa-0 ga-0">
                      <v-col class="ma-0 pa-0 ga-0 text-center text-truncate">
                        <v-icon
                          icon="mdi-tag"
                          color="black"
                          size="x-small"
                        ></v-icon>
                        <span class="font-weight-bold text-black">
                          {{ item.raw.tag.tag_name }}
                        </span>
                      </v-col>
                    </v-row>
                  </v-container>
                </v-list-item-subtitle>
              </v-list-item>
            </template>
          </template>
          <template v-slot:loader>
            <v-skeleton-loader
              class="border"
              type="paragraph"
            ></v-skeleton-loader>
          </template>
          <template
            v-slot:footer="{ page, pageCount, prevPage, nextPage }"
            v-if="props.allowEdit"
          >
            <div class="d-flex align-center justify-center pa-4">
              <v-btn
                :disabled="page === 1"
                density="comfortable"
                icon="mdi-arrow-left"
                variant="tonal"
                rounded
                @click="prevPage"
              ></v-btn>

              <div class="mx-2 text-caption">
                Page {{ page }} of {{ pageCount }}
              </div>

              <v-btn
                :disabled="page >= pageCount"
                density="comfortable"
                icon="mdi-arrow-right"
                variant="tonal"
                rounded
                @click="nextPage"
              ></v-btn>
            </div>
          </template>
        </v-data-iterator>
      </v-list>
    </template>
  </v-card>
</template>
<script setup>
  import Vue3Datatable from "@bhplugin/vue3-datatable";
  import "@bhplugin/vue3-datatable/dist/style.css";
  import { defineProps, ref } from "vue";
  import { useReminders } from "@/composables/remindersComposable";
  import ReminderForm from "@/components/ReminderForm.vue";
  import { useDisplay } from "vuetify";

  const { smAndDown } = useDisplay();
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(today.getDate() + 1);
  const year = tomorrow.getFullYear();
  const month = String(tomorrow.getMonth() + 1).padStart(2, "0");
  const day = String(tomorrow.getDate()).padStart(2, "0");
  const formattedDate = `${year}-${month}-${day}`;
  const start_date = ref(formattedDate);
  const selected = ref([]);
  const showDeleteDialog = ref(false);
  const reminderAddFormDialog = ref(false);
  const reminderEditFormDialog = ref(false);
  const { reminders, isLoading, removeReminder } = useReminders();
  const props = defineProps({
    allowEdit: {
      type: Boolean,
      default: false,
    },
  });

  const editReminder = ref({
    id: 0,
    tag: {
      id: null,
    },
    amount: null,
    reminder_source_account: {
      id: null,
    },
    reminder_destination_account: {
      id: null,
    },
    description: null,
    transaction_type: {
      id: 1,
    },
    start_date: start_date.value,
    next_date: start_date.value,
    end_date: null,
    repeat: {
      id: null,
    },
    auto_add: true,
  });

  const rowSelected = () => {
    selected.value = [];
    let selectedrows = reminders_table.value.getSelectedRows();
    for (const selectedrow of selectedrows) {
      selected.value.push(selectedrow.id);
      editReminder.value = selectedrow;
    }
  };
  const blankForm = ref({
    id: 0,
    tag: {
      id: null,
    },
    amount: null,
    reminder_source_account: {
      id: null,
    },
    reminder_destination_account: {
      id: null,
    },
    description: null,
    transaction_type: {
      id: 1,
    },
    start_date: start_date.value,
    next_date: start_date.value,
    end_date: null,
    repeat: {
      id: null,
    },
    auto_add: true,
  });
  const reminders_table = ref(null);
  const columns = ref([
    { field: "next_date", title: "Next Date", type: "date", width: "120px" },
    { field: "amount", title: "Amount", type: "number", width: "100px" },
    { field: "description", title: "Reminder" },
    { field: "tag.tag_name", title: "Tag", width: "200px" },
    { field: "end_date", title: "End Date", type: "date", width: "120px" },
    { field: "repeat.repeat_name", title: "Repeat", width: "120px" },
  ]);
  const getClassForMoney = amount => {
    let color = "";
    let font = "";

    font = "font-weight-bold";
    if (amount < 0) {
      color = "text-red";
    } else {
      color = "text-green";
    }

    return color + " " + font;
  };

  const clickRemoveReminder = async reminders => {
    reminders.forEach(reminder => {
      removeReminder(reminder);
      selected.value = [];
    });
  };

  const updateAddDialog = () => {
    reminderAddFormDialog.value = false;
  };

  const updateEditDialog = () => {
    reminderEditFormDialog.value = false;
  };
  const formatCurrency = value => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };
</script>
<style>
  /* alt-pagination */
  .alt-pagination .bh-pagination .bh-page-item {
    width: auto; /* equivalent to w-max */
    min-width: 32px;
    border-radius: 0.25rem; /* equivalent to rounded */
  }
  /* Customize the color of the selected page number */
  .alt-pagination .bh-pagination .bh-page-item.bh-active {
    background-color: #06966a; /* Change this to your desired color */
    border-color: black;
    font-weight: bold; /* Optional: Make the text bold */
  }
  .alt-pagination .bh-pagination .bh-page-item:not(.bh-active):hover {
    background-color: #ff5900;
    border-color: black;
  }
</style>
