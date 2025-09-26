<template>
  <v-card variant="outlined" :elevation="4" class="bg-white">
    <v-card-title>
      <span
        class="text-subtitle-2 text-secondary"
        v-if="props.variant === 'upcoming'"
      >
        Upcoming Reminders
      </span>
      <span class="text-subtitle-2 text-secondary" v-else>Reminders</span>
    </v-card-title>
    <v-card-text class="ma-0 pa-0 ga-0">
      <div v-if="props.allowEdit">
        <v-tooltip text="Edit Reminder" location="top">
          <template v-slot:activator="{ props }">
            <v-btn
              icon="mdi-bell-cog"
              flat
              :disabled="selected_reminder.length === 0"
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
              :disabled="selected_reminder.length === 0"
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
              Are you sure you want to delete this reminder?
            </v-card-text>

            <v-card-actions>
              <v-spacer></v-spacer>

              <v-btn
                text="Confirm"
                @click="
                  clickRemoveReminder();
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
      <v-data-table
        :headers="displayHeaders"
        :items="reminders ? reminders : []"
        :items-length="reminders ? reminders.length : 0"
        :loading="isLoading"
        item-value="id"
        v-model:items-per-page="itemsPerPage"
        :items-per-page-options="[
          {
            value: 5,
            title: 5,
          },
        ]"
        items-per-page-text="Reminders per page"
        no-data-text="No reminders!"
        loading-text="Loading reminders..."
        disable-sort
        :show-select="props.variant === 'full'"
        fixed-footer
        striped="odd"
        density="compact"
        :hide-default-header="mdAndUp ? false : true"
        :hide-default-footer="props.variant === 'upcoming'"
        width="100%"
        return-object
        v-model="selected_reminder"
        select-strategy="single"
        v-model:page="page"
        :header-props="{ class: 'font-weight-bold' }"
        :row-props="{ class: 'text-body-2' }"
      >
        <template v-slot:bottom v-if="props.variant != 'upcoming'">
          <div class="text-center pt-2">
            <v-pagination v-model="page" :length="pageCount"></v-pagination>
          </div>
        </template>
        <template v-slot:[`item.amount`]="{ item }" v-if="mdAndUp">
          <span :class="getClassForMoney(item.amount)">
            {{ formatCurrency(item.amount) }}
          </span>
        </template>
        <template v-slot:[`item.tag.tag_name`]="{ item }" v-if="mdAndUp">
          <span>
            <v-icon icon="mdi-tag" color="black" size="x-small"></v-icon>
            {{ item.tag.tag_name }}
          </span>
        </template>
        <template v-slot:[`item.end_date`]="{ item }" v-if="mdAndUp">
          <span>
            <v-icon
              icon="mdi-infinity"
              color="black"
              size="small"
              v-if="!item.end_date"
            ></v-icon>
            {{ item.end_date }}
          </span>
        </template>
        <!-- Mobile View -->
        <template v-slot:[`item.mobile`]="{ item }">
          <v-container class="ma-0 pa-0 ga-0">
            <v-row dense class="ma-0 pa-0 ga-0">
              <v-col class="ma-0 pa-0 ga-0" cols="4">
                <span class="font-weight-bold">
                  <v-icon
                    icon="mdi-skip-next-circle"
                    size="small"
                    color="success"
                  ></v-icon>
                  {{ formatDate(item.next_date, true) }}
                </span>
              </v-col>
              <v-col class="ma-0 pa-0 ga-0" cols="4">
                <span v-if="item.end_date" class="font-weight-bold">
                  <v-icon
                    icon="mdi-stop-circle"
                    size="small"
                    color="error"
                  ></v-icon>
                  {{ formatDate(item.end_date, true) }}
                </span>
                <span v-else>
                  <v-icon
                    icon="mdi-stop-circle"
                    size="small"
                    color="error"
                  ></v-icon>
                  &nbsp;
                  <v-icon
                    icon="mdi-infinity"
                    size="small"
                    color="black"
                  ></v-icon>
                </span>
              </v-col>
              <v-col class="ma-0 pa-0 ga-0 text-right font-weight-bold">
                <span :class="getClassForMoney(item.amount)">
                  {{ formatCurrency(item.amount) }}
                </span>
              </v-col>
            </v-row>
            <v-row dense class="ma-0 pa-0 ga-0">
              <v-col class="ma-0 pa-0 ga-0 font-weight-bold text-truncate">
                <span>
                  {{ item.description }}
                </span>
              </v-col>
            </v-row>
            <v-row dense class="ma-0 pa-0 ga-0">
              <v-col
                class="ma-0 pa-0 ga-0 text-secondary text-left font-weight-italic text-truncate"
              >
                <span>
                  <v-icon
                    icon="mdi-repeat"
                    size="x-small"
                    color="black"
                  ></v-icon>
                  {{ item.repeat.repeat_name }}
                </span>
              </v-col>
            </v-row>
            <v-row dense class="ma-0 pa-0 ga-0">
              <v-col class="ma-0 pa-0 ga-0 text-center text-truncate">
                <span>
                  <v-icon icon="mdi-tag" size="x-small" color="black"></v-icon>
                  {{ item.tag.tag_name }}
                </span>
              </v-col>
            </v-row>
          </v-container>
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>
<script setup>
  import { defineProps, ref, computed, watch } from "vue";
  import { useReminders } from "@/composables/remindersComposable";
  import ReminderForm from "@/components/ReminderForm.vue";
  import { useDisplay } from "vuetify";

  const selected_reminder = ref([]);
  const { mdAndUp } = useDisplay();
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(today.getDate() + 1);
  const year = tomorrow.getFullYear();
  const month = String(tomorrow.getMonth() + 1).padStart(2, "0");
  const day = String(tomorrow.getDate()).padStart(2, "0");
  const formattedDate = `${year}-${month}-${day}`;
  const start_date = ref(formattedDate);
  const showDeleteDialog = ref(false);
  const reminderAddFormDialog = ref(false);
  const reminderEditFormDialog = ref(false);
  const { reminders, isLoading, removeReminder } = useReminders();
  const page = ref(1);
  const itemsPerPage = computed(() => {
    if (props.variant === "full") {
      return 20;
    }
    return 5;
  });
  const pageCount = computed(() =>
    reminders.value && itemsPerPage.value
      ? Math.ceil(reminders.value.length / itemsPerPage.value)
      : 1,
  );
  const props = defineProps({
    allowEdit: {
      type: Boolean,
      default: false,
    },
    variant: { type: String, default: "full" },
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

  const headers = ref([
    { title: "Next Date", key: "next_date", width: "120px" },
    { title: "Amount", key: "amount", width: "100px" },
    { title: "Reminder", key: "description" },
    { title: "Tag", key: "tag.tag_name", width: "200px" },
    { title: "End Date", key: "end_date", width: "120px" },
    { title: "Repeat", key: "repeat.repeat_name", width: "150px" },
  ]);
  const displayHeaders = computed(() => {
    if (mdAndUp.value) {
      return headers.value;
    }
    // For small screens, use your single mobile column
    return [{ title: "", key: "mobile" }];
  });
  const getClassForMoney = amount => {
    let color = "";

    if (amount < 0) {
      color = "text-red";
    } else {
      color = "text-green";
    }

    return color;
  };

  const clickRemoveReminder = () => {
    removeReminder(selected_reminder.value[0].id);
    selected_reminder.value = [];
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

  watch(
    () => selected_reminder.value,
    val => {
      if (val) {
        editReminder.value = val[0];
      }
    },
  );

  const formatDate = (input, padDay = false) => {
    // Normalize input to a Date object
    const date = input instanceof Date ? input : new Date(input);

    if (isNaN(date)) {
      console.warn("Invalid date:", input);
      return "";
    }

    const month = date.toLocaleString("en-US", { month: "short" }); // 'Sep'
    const day = date.getDate(); // 16

    return `${month}-${padDay ? String(day).padStart(2, "0") : day}`;
  };
</script>
