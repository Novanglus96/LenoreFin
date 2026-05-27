<template>
  <v-container fluid>
    <v-row>
      <v-col>
        <h4 class="text-h5 font-weight-bold mb-2">Recurring Detections</h4>
        <p class="text-body-2 text-medium-emphasis mb-4">
          Patterns detected from your transaction history. Create a reminder or ignore to stop seeing a suggestion.
        </p>
      </v-col>
    </v-row>

    <v-progress-linear indeterminate v-if="isFetching" color="primary" class="mb-4"></v-progress-linear>

    <v-row v-if="!isLoading && detections.length === 0">
      <v-col>
        <v-sheet border rounded class="pa-6 text-center text-medium-emphasis">
          <v-icon icon="mdi-check-circle-outline" size="48" class="mb-2"></v-icon>
          <div class="text-body-1">No recurring patterns detected yet.</div>
          <div class="text-body-2 mt-1">Detection runs weekly — check back after more transactions are recorded.</div>
        </v-sheet>
      </v-col>
    </v-row>

    <v-row>
      <v-col
        cols="12"
        md="6"
        lg="4"
        v-for="detection in detections"
        :key="detection.id"
      >
        <v-card variant="outlined" :elevation="2" class="bg-surface h-100">
          <v-card-title class="text-subtitle-1 font-weight-bold text-truncate pb-0">
            {{ detection.description }}
          </v-card-title>
          <v-card-text class="pt-2">
            <v-row dense>
              <v-col cols="6">
                <div class="text-caption text-medium-emphasis">Avg Amount</div>
                <div class="text-body-1 font-weight-bold text-success">
                  {{ formatCurrency(detection.estimated_amount) }}
                </div>
              </v-col>
              <v-col cols="6">
                <div class="text-caption text-medium-emphasis">Frequency</div>
                <div class="text-body-2">{{ detection.repeat_name ?? "Unknown" }}</div>
              </v-col>
              <v-col cols="6" class="mt-1">
                <div class="text-caption text-medium-emphasis">Next Expected</div>
                <div class="text-body-2">{{ detection.next_estimated_date }}</div>
              </v-col>
              <v-col cols="6" class="mt-1">
                <div class="text-caption text-medium-emphasis">Occurrences</div>
                <div class="text-body-2">{{ detection.transaction_ids.length }} in last 120 days</div>
              </v-col>
            </v-row>
          </v-card-text>
          <v-card-actions>
            <v-btn
              color="primary"
              variant="tonal"
              size="small"
              prepend-icon="mdi-bell-plus"
              @click="openReminderForm(detection)"
              :disabled="!isOnline"
            >Create Reminder</v-btn>
            <v-spacer></v-spacer>
            <v-btn
              color="error"
              variant="text"
              size="small"
              prepend-icon="mdi-eye-off"
              @click="confirmIgnore(detection)"
              :disabled="!isOnline"
            >Ignore</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- Reminder form dialog -->
    <ReminderForm
      v-model="reminderDialog"
      :isEdit="false"
      @update-dialog="onReminderSaved"
      :passedFormData="reminderFormData"
    />

    <!-- Ignore confirm dialog -->
    <v-dialog v-model="ignoreDialog" max-width="380">
      <v-card>
        <v-card-title class="text-h6">Ignore Detection</v-card-title>
        <v-card-text>
          Stop suggesting <strong>{{ pendingIgnore?.description }}</strong> as a recurring reminder?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="ignoreDialog = false">Cancel</v-btn>
          <v-btn color="error" @click="doIgnore">Ignore</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
  import { ref } from "vue";
  import { useDetections } from "@/composables/detectionsComposable";
  import { useOnlineStatus } from "@/composables/useOnlineStatus";
  import ReminderForm from "@/components/ReminderForm.vue";

  const { isOnline } = useOnlineStatus();
  const { detections, isLoading, isFetching, ignoreDetection, deleteDetection } = useDetections();

  const reminderDialog = ref(false);
  const reminderFormData = ref(null);
  const activeDetectionId = ref(null);

  const ignoreDialog = ref(false);
  const pendingIgnore = ref(null);

  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(today.getDate() + 1);
  const tomorrowStr = `${tomorrow.getFullYear()}-${String(tomorrow.getMonth() + 1).padStart(2, "0")}-${String(tomorrow.getDate()).padStart(2, "0")}`;

  function openReminderForm(detection) {
    activeDetectionId.value = detection.id;
    reminderFormData.value = {
      id: 0,
      tag: { id: null },
      amount: detection.estimated_amount,
      reminder_source_account: { id: null },
      reminder_destination_account: { id: null },
      description: detection.description,
      transaction_type: { id: 1 },
      start_date: detection.next_estimated_date ?? tomorrowStr,
      next_date: detection.next_estimated_date ?? tomorrowStr,
      end_date: null,
      repeat: { id: detection.repeat_id ?? null },
      auto_add: true,
    };
    reminderDialog.value = true;
  }

  function onReminderSaved() {
    reminderDialog.value = false;
    if (activeDetectionId.value) {
      deleteDetection(activeDetectionId.value);
      activeDetectionId.value = null;
    }
  }

  function confirmIgnore(detection) {
    pendingIgnore.value = detection;
    ignoreDialog.value = true;
  }

  function doIgnore() {
    ignoreDetection(pendingIgnore.value.id);
    ignoreDialog.value = false;
    pendingIgnore.value = null;
  }

  function formatCurrency(value) {
    if (value === null || value === undefined) return "—";
    return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(parseFloat(value));
  }
</script>
