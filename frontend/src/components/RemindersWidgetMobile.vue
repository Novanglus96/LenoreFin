<template>
  <v-card variant="outlined" :elevation="4" class="bg-white">
    <template v-slot:title>
      <span class="text-subtitle-2 text-secondary" v-if="!props.allowEdit"
        >Upcoming Reminders</span
      >
      <span class="text-subtitle-2 text-secondary" v-else>Reminders</span>
    </template>
    <template v-slot:text>
      <div v-if="props.allowEdit">
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
        <ReminderFormMobile
          v-model="reminderAddFormDialog"
          :isEdit="false"
          @update-dialog="updateAddDialog"
          :passedFormData="blankForm"
        />
      </div>
      <v-data-iterator
        :items="reminders"
        :loading="isLoading"
        items-per-page="3"
      >
        <template v-slot:default="{ items }">
          <template v-for="(item, i) in items" :key="i">
            <v-card
              class="flex ma-0 pa-0 ga-0"
              hover
              ripple
              role="button"
              @click="toggleMore(i)"
              ><v-card-text
                ><v-container class="flex ma-0 pa-0 ga-0"
                  ><v-row dense
                    ><v-col cols="7">
                      <v-container
                        ><v-row dense
                          ><v-col
                            class="text-truncate text-subtitle-2 font-weight-bold"
                            >{{ item.raw.description }}</v-col
                          ></v-row
                        ><v-row dense
                          ><v-col class="font-italic">{{
                            item.raw.next_date
                          }}</v-col></v-row
                        ></v-container
                      ></v-col
                    ><v-col cols="4" class="d-flex justify-center align-center"
                      ><span :class="getClassForMoney(item.raw.amount)">{{
                        formatCurrency(item.raw.amount)
                      }}</span></v-col
                    ><v-col cols="1" class="d-flex justify-center align-center"
                      ><v-icon
                        :icon="
                          !showMore[i] ? 'mdi-chevron-down' : 'mdi-chevron-up'
                        "
                        variant="plain"
                      ></v-icon></v-col></v-row></v-container></v-card-text
              ><v-card-actions v-if="props.allowEdit"
                ><v-spacer></v-spacer
                ><v-btn
                  color="secondary"
                  @click="toggleReminderEdit(i, item.raw)"
                  >edit</v-btn
                ><ReminderFormMobile
                  v-model="reminderEditFormDialog[i]"
                  :isEdit="true"
                  :key="i"
                  :passedFormData="editReminder"
                  @update-dialog="toggleReminderEdit(i)"
                />
                <v-btn color="error" @click="toggleDelete(i)">delete</v-btn>
                <v-dialog width="500" v-model="showDeleteDialog[i]" :key="i">
                  <v-card>
                    <v-card-title>{{ item.raw.description }}</v-card-title>
                    <v-card-text>
                      Are you sure you want to delete this reminder?
                    </v-card-text>

                    <v-card-actions>
                      <v-spacer></v-spacer>

                      <v-btn
                        text="Confirm"
                        @click="
                          clickRemoveReminder(item.raw.id);
                          showDeleteDialog[i] = false;
                        "
                      ></v-btn>
                    </v-card-actions>
                  </v-card>
                </v-dialog> </v-card-actions></v-card
            ><v-expand-transition
              ><v-card
                v-if="showMore[i]"
                color="grey-lighten-2"
                class="flex ma-0 pa-0 ga-0"
                ><v-card-text
                  ><v-container class="flex ma-0 pa-0 ga-0"
                    ><v-row dense
                      ><v-col
                        ><v-container
                          ><v-row dense
                            ><v-col
                              ><v-tooltip text="Repeats" location="top">
                                <template #activator="{ props }"
                                  ><v-icon
                                    icon="mdi-repeat"
                                    v-bind="props"
                                  ></v-icon></template
                              ></v-tooltip>
                              {{ item.raw.repeat.repeat_name }}</v-col
                            ><v-col
                              ><v-tooltip text="End Date" location="top">
                                <template #activator="{ props }"
                                  ><v-icon
                                    icon="mdi-timer-stop"
                                    v-bind="props"
                                  ></v-icon></template
                              ></v-tooltip>
                              {{
                                item.raw.end_date ? item.raw.end_date : "none"
                              }}</v-col
                            ></v-row
                          ><v-row dense
                            ><v-col
                              ><v-icon icon="mdi-tag" color="black"></v-icon>
                              <span class="font-weight-bold text-black">{{
                                item.raw.tag.tag_name
                              }}</span></v-col
                            ></v-row
                          ></v-container
                        ></v-col
                      ></v-row
                    ></v-container
                  ></v-card-text
                ></v-card
              ></v-expand-transition
            >

            <br />
          </template>
        </template>
        <template v-slot:footer="{ page, pageCount, prevPage, nextPage }">
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
    </template>
  </v-card>
</template>
<script setup>
import { defineProps, ref } from "vue";
import { useReminders } from "@/composables/remindersComposable";
import ReminderFormMobile from "@/components/ReminderFormMobile.vue";

const showMore = ref({});
const today = new Date();
const tomorrow = new Date(today);
tomorrow.setDate(today.getDate() + 1);
const year = tomorrow.getFullYear();
const month = String(tomorrow.getMonth() + 1).padStart(2, "0");
const day = String(tomorrow.getDate()).padStart(2, "0");
const formattedDate = `${year}-${month}-${day}`;
const start_date = ref(formattedDate);
const selected = ref([]);
const showDeleteDialog = ref({});
const reminderAddFormDialog = ref(false);
const reminderEditFormDialog = ref({});
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

const toggleMore = index => {
  showMore.value[index] = !showMore.value[index];
};

const toggleDelete = index => {
  showDeleteDialog.value[index] = !showDeleteDialog.value[index];
};

const toggleReminderEdit = (index, reminder) => {
  if (!reminder) {
    editReminder.value = {
      id: reminder ? reminder.id : 0,
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
    };
  } else {
    editReminder.value = reminder;
  }
  reminderEditFormDialog.value[index] = !reminderEditFormDialog.value[index];
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

const getClassForMoney = amount => {
  let color = "";
  let font = "";

  font = "font-weight-bold";
  if (amount < 0) {
    color = "text-red";
  } else {
    color = "text-green";
  }

  return color + " " + font + " text-h6";
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
.text-truncate {
  white-space: nowrap; /* Prevent text from wrapping to the next line */
  overflow: hidden; /* Hide overflow content */
  text-overflow: ellipsis; /* Show "..." for overflow text */
}
</style>
