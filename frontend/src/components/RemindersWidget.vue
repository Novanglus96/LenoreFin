<template>
  <v-card variant="outlined" :elevation="4" class="bg-surface">
    <v-card-title>
      <span
        class="text-subtitle-2 text-primary"
        v-if="props.variant === 'upcoming'"
      >
        Upcoming Reminders
      </span>
      <span class="text-subtitle-2 text-primary" v-else>Reminders</span>
    </v-card-title>
    <v-card-text class="ma-0 pa-0 ga-0">
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
        :hide-default-footer="props.variant === 'upcoming'"
        width="100%"
        return-object
        v-model="selected_reminder"
        select-strategy="single"
        v-model:page="page"
        :header-props="{ class: 'font-weight-bold bg-secondary' }"
        :row-props="getRowProps"
        class="bg-background"
      >
        <template v-slot:bottom v-if="props.variant != 'upcoming'">
          <div class="text-center pt-2">
            <v-pagination v-model="page" :length="pageCount"></v-pagination>
          </div>
        </template>
        <template v-slot:[`item.next_date`]="{ item }" v-if="mdAndUp">
          <span>{{ formatDate(item.next_date, true) }}</span>
        </template>
        <template v-slot:[`item.amount`]="{ item }" v-if="mdAndUp">
          <span :class="getClassForMoney(item.amount)">
            {{ formatCurrency(item.amount) }}
          </span>
        </template>
        <template v-slot:[`item.tag.tag_name`]="{ item }" v-if="mdAndUp">
          <span class="text-primary">
            {{ item.tag.tag_name }}
          </span>
        </template>
        <template v-slot:[`item.end_date`]="{ item }" v-if="mdAndUp">
          <span>
            <v-icon
              icon="mdi-infinity"
              size="small"
              v-if="!item.end_date"
            ></v-icon>
            {{ item.end_date ? formatDate(item.end_date) : "" }}
          </span>
        </template>
        <template v-slot:[`item.repeat.repeat_name`]="{ item }" v-if="mdAndUp">
          <span class="text-altAccent">
            {{ item.repeat.repeat_name }}
          </span>
        </template>
        <!-- Mobile View -->
        <template v-slot:[`item.mobile`]="{ item }">
          <v-container class="ma-0 pa-0 ga-0">
            <v-row dense class="ma-0 pa-0 ga-0">
              <v-col class="ma-0 pa-0 ga-0" cols="3">
                <span>
                  <v-icon
                    icon="mdi-skip-next-circle"
                    size="small"
                    color="success"
                  ></v-icon>
                  {{ formatDate(item.next_date, true) }}
                </span>
              </v-col>
              <v-col class="ma-0 pa-0 ga-0" cols="5">
                <span v-if="item.end_date">
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
                  <v-icon icon="mdi-infinity" size="small"></v-icon>
                </span>
              </v-col>
              <v-col class="ma-0 pa-0 ga-0 text-right">
                <span :class="getClassForMoney(item.amount)">
                  {{ formatCurrency(item.amount) }}
                </span>
              </v-col>
            </v-row>
            <v-row dense class="ma-0 pa-0 ga-0">
              <v-col class="ma-0 pa-0 ga-0 text-truncate font-weight-bold">
                <span>
                  {{ item.description }}
                </span>
              </v-col>
            </v-row>
            <v-row dense class="ma-0 pa-0 ga-0">
              <v-col
                class="ma-0 pa-0 ga-0 text-primary text-left font-weight-italic text-truncate"
              >
                <span class="text-altAccent">
                  <v-icon
                    icon="mdi-repeat"
                    size="x-small"
                    color="secondary"
                  ></v-icon>
                  {{ item.repeat.repeat_name }}
                </span>
              </v-col>
            </v-row>
            <v-row dense class="ma-0 pa-0 ga-0">
              <v-col class="ma-0 pa-0 ga-0 text-center text-truncate">
                <span class="text-primary">
                  <v-icon
                    icon="mdi-tag"
                    size="x-small"
                    color="secondary"
                  ></v-icon>
                  {{ item.tag.tag_name }}
                </span>
              </v-col>
            </v-row>
          </v-container>
        </template>
        <template v-slot:top v-if="props.allowEdit">
          <v-fab
            key="fab1"
            :app="true"
            color="success"
            location="right bottom"
            size="small"
            icon
            @click="reminderAddFormDialog = true"
            variant="elevated"
            v-if="selected_reminder.length === 0"
          >
            <v-icon icon="mdi-bell-plus"></v-icon>
          </v-fab>
          <ReminderForm
            v-model="reminderAddFormDialog"
            :isEdit="false"
            @update-dialog="updateAddDialog"
            :passedFormData="blankForm"
          />
          <v-fab
            key="fab2"
            :app="true"
            :color="open ? '' : 'secondary'"
            location="right bottom"
            size="small"
            icon
            :disabled="true"
            variant="plain"
          >
            <v-icon></v-icon>
            <v-speed-dial
              v-model="open"
              location="top center"
              transition="scale-transition"
              activator="parent"
              persistent
              :close-on-content-click="false"
            >
              <div key="1">
                <v-tooltip text="Uncheck All" location="left" key="1">
                  <template v-slot:activator="{ props }">
                    <v-btn
                      icon="mdi-checkbox-multiple-marked-outline"
                      key="1"
                      color="warning"
                      @click="uncheck_all"
                      v-bind="props"
                    ></v-btn>
                  </template>
                </v-tooltip>
              </div>
              <div key="2">
                <v-tooltip text="Remove Reminder(s)" location="top">
                  <template v-slot:activator="{ props }">
                    <v-btn
                      icon="mdi-bell-remove"
                      :disabled="selected_reminder.length === 0"
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
              </div>
              <div key="3">
                <v-tooltip text="Edit Reminder" location="top">
                  <template v-slot:activator="{ props }">
                    <v-btn
                      icon="mdi-bell-cog"
                      :disabled="selected_reminder.length === 0"
                      @click="reminderEditFormDialog = true"
                      v-bind="props"
                    ></v-btn>
                  </template>
                </v-tooltip>
              </div>
            </v-speed-dial>
          </v-fab>
          <ReminderForm
            v-model="reminderEditFormDialog"
            :isEdit="true"
            @update-dialog="updateEditDialog"
            :passedFormData="editReminder"
          />
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
  const open = ref(false);
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
    { title: "", key: "status", width: "72px" },
    { title: "Next", key: "next_date", width: "84px" },
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
      color = "text-error";
    } else {
      color = "text-success";
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
        open.value = val.length != 0 ? true : false;
      }
    },
  );

  const formatDate = (input, padDay = false) => {
    let date;

    // If input is already a Date object, trust it
    if (input instanceof Date) {
      date = input;
    } else if (typeof input === "string" && /^\d{4}-\d{2}-\d{2}$/.test(input)) {
      // Manual parse YYYY-MM-DD to LOCAL date (no timezone shift)
      const [y, m, d] = input.split("-").map(Number);
      date = new Date(y, m - 1, d);
    } else {
      date = new Date(input); // fallback for timestamps
    }

    if (isNaN(date)) {
      console.warn("Invalid date:", input);
      return "";
    }

    const month = date.toLocaleString("en-US", { month: "short" });
    const day = date.getDate();

    return `${month}-${padDay ? String(day).padStart(2, "0") : day}`;
  };
  const uncheck_all = () => {
    selected_reminder.value = [];
    open.value = false;
  };

  function getRowProps({ item }) {
    let rowformat = "text-body-2";
    const isSelected = selected_reminder.value.some(sel => sel.id === item.id);
    if (isSelected) {
      rowformat += " bg-primary-lighten-3";
    }
    return {
      class: rowformat,
    };
  }
</script>
