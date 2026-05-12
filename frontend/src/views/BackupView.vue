<template>
  <v-container fluid>
    <v-row>
      <v-col>
        <h4 class="text-h5 font-weight-bold mb-4">Backup & Restore</h4>
      </v-col>
    </v-row>

    <!-- Backup Configuration -->
    <v-row>
      <v-col cols="12" md="6">
        <v-sheet border rounded>
          <v-container>
            <v-row dense>
              <v-col>
                <h4 class="text-h6 font-weight-bold mb-2">Backup Schedule</h4>
              </v-col>
            </v-row>
            <v-row dense>
              <v-col>
                <v-checkbox
                  v-model="configForm.backup_enabled"
                  label="Enable Automatic Backups"
                ></v-checkbox>
              </v-col>
            </v-row>
            <template v-if="configForm.backup_enabled">
              <v-row dense>
                <v-col>
                  <v-select
                    label="Frequency"
                    :items="frequencyOptions"
                    item-title="label"
                    item-value="value"
                    v-model="configForm.frequency"
                    density="comfortable"
                    variant="outlined"
                  ></v-select>
                </v-col>
                <v-col v-if="configForm.frequency !== 'HOURLY'">
                  <v-text-field
                    label="Time (HH:MM)"
                    v-model="configForm.backup_time"
                    density="comfortable"
                    variant="outlined"
                    placeholder="02:00"
                  ></v-text-field>
                </v-col>
              </v-row>
            </template>
            <v-row dense>
              <v-col>
                <v-text-field
                  label="Copies to Keep"
                  v-model.number="configForm.copies_to_keep"
                  density="comfortable"
                  variant="outlined"
                  type="number"
                  min="1"
                ></v-text-field>
              </v-col>
              <v-col>
                <v-spacer></v-spacer>
              </v-col>
            </v-row>
            <v-row dense>
              <v-col>
                <v-btn color="primary" @click="saveConfig" :loading="isSaving">Save Settings</v-btn>
              </v-col>
            </v-row>
          </v-container>
        </v-sheet>
      </v-col>

      <!-- Manual Backup & Upload Restore -->
      <v-col cols="12" md="6">
        <v-sheet border rounded>
          <v-container>
            <v-row dense>
              <v-col>
                <h4 class="text-h6 font-weight-bold mb-2">Manual Backup</h4>
              </v-col>
            </v-row>
            <v-row dense>
              <v-col>
                <v-btn color="primary" prepend-icon="mdi-database-arrow-up" @click="runBackup">
                  Backup Now
                </v-btn>
              </v-col>
            </v-row>
            <v-row dense class="mt-4">
              <v-col>
                <h4 class="text-h6 font-weight-bold mb-2">Restore from File</h4>
              </v-col>
            </v-row>
            <v-row dense>
              <v-col>
                <v-file-input
                  label="Upload backup file"
                  v-model="uploadFile"
                  density="comfortable"
                  variant="outlined"
                  accept=".json.gz,.json"
                  prepend-icon=""
                  prepend-inner-icon="mdi-upload"
                ></v-file-input>
              </v-col>
            </v-row>
            <v-row dense>
              <v-col>
                <v-btn
                  color="error"
                  prepend-icon="mdi-database-import"
                  :disabled="!uploadFile"
                  @click="confirmRestoreUpload"
                  :loading="isRestoring"
                >
                  Restore from Upload
                </v-btn>
              </v-col>
            </v-row>
          </v-container>
        </v-sheet>
      </v-col>
    </v-row>

    <!-- Backup Files -->
    <v-row class="mt-2">
      <v-col>
        <v-sheet border rounded>
          <v-container>
            <v-row dense>
              <v-col>
                <h4 class="text-h6 font-weight-bold mb-2">Backup Files</h4>
              </v-col>
              <v-col class="d-flex justify-end">
                <v-btn icon="mdi-refresh" size="small" variant="text" @click="refetch"></v-btn>
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <v-data-table
                  :headers="headers"
                  :items="databaseBackups"
                  :loading="filesLoading"
                  density="compact"
                  no-data-text="No backups found"
                >
                  <template v-slot:item.created_at="{ item }">
                    {{ formatDate(item.created_at) }}
                  </template>
                  <template v-slot:item.size="{ item }">
                    {{ formatSize(item.size) }}
                  </template>
                  <template v-slot:item.actions="{ item }">
                    <v-btn
                      icon="mdi-download"
                      size="small"
                      variant="text"
                      @click="downloadBackup(item.filename)"
                    ></v-btn>
                    <v-btn
                      icon="mdi-database-import"
                      size="small"
                      variant="text"
                      color="warning"
                      @click="confirmRestore(item.filename)"
                    ></v-btn>
                    <v-btn
                      icon="mdi-delete"
                      size="small"
                      variant="text"
                      color="error"
                      @click="confirmDelete(item.filename)"
                    ></v-btn>
                  </template>
                </v-data-table>
              </v-col>
            </v-row>
          </v-container>
        </v-sheet>
      </v-col>
    </v-row>

    <!-- Restore Confirm Dialog -->
    <v-dialog v-model="restoreDialog" max-width="480">
      <v-card>
        <v-card-title class="text-h6">Confirm Restore</v-card-title>
        <v-card-text>
          <v-alert type="warning" variant="tonal" class="mb-2">
            This will <strong>replace all current data</strong> with the contents of
            <strong>{{ pendingRestoreFile }}</strong>. The app may be briefly unavailable.
            This cannot be undone.
          </v-alert>
          Are you sure you want to proceed?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="restoreDialog = false">Cancel</v-btn>
          <v-btn color="error" @click="doRestore" :loading="isRestoring">Restore</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirm Dialog -->
    <v-dialog v-model="deleteDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h6">Delete Backup</v-card-title>
        <v-card-text>
          Delete <strong>{{ pendingDeleteFile }}</strong>? This cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="deleteDialog = false">Cancel</v-btn>
          <v-btn color="error" @click="doDelete">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
  import { ref, computed, watch } from "vue";
  import {
    useBackupConfig,
    useBackupFiles,
    downloadBackup,
  } from "@/composables/backupComposable";

  const { backupConfig, editBackupConfig } = useBackupConfig();
  const {
    backupFiles,
    isLoading: filesLoading,
    refetch,
    runBackup,
    deleteBackup,
    restoreDatabase,
    restoreFromUpload,
    isRestoring,
  } = useBackupFiles();

  const configForm = ref({
    backup_enabled: true,
    frequency: "DAILY",
    backup_time: "02:00",
    copies_to_keep: 2,
  });

  const isSaving = ref(false);
  const uploadFile = ref(null);
  const restoreDialog = ref(false);
  const deleteDialog = ref(false);
  const pendingRestoreFile = ref(null);
  const pendingDeleteFile = ref(null);
  const isUploadRestore = ref(false);

  const frequencyOptions = [
    { label: "Hourly", value: "HOURLY" },
    { label: "Daily", value: "DAILY" },
    { label: "Weekly", value: "WEEKLY" },
  ];

  const headers = [
    { title: "Filename", key: "filename" },
    { title: "Date", key: "created_at" },
    { title: "Size", key: "size" },
    { title: "Actions", key: "actions", sortable: false },
  ];

  const databaseBackups = computed(() =>
    (backupFiles.value ?? []).filter(f => f.backup_type === "database"),
  );

  watch(backupConfig, val => {
    if (val) {
      configForm.value = {
        backup_enabled: val.backup_enabled,
        frequency: val.frequency,
        backup_time: val.backup_time,
        copies_to_keep: val.copies_to_keep,
      };
    }
  });

  function saveConfig() {
    isSaving.value = true;
    editBackupConfig({ ...configForm.value });
    setTimeout(() => (isSaving.value = false), 1000);
  }

  function confirmRestore(filename) {
    pendingRestoreFile.value = filename;
    isUploadRestore.value = false;
    restoreDialog.value = true;
  }

  function confirmRestoreUpload() {
    pendingRestoreFile.value = uploadFile.value?.name ?? "uploaded file";
    isUploadRestore.value = true;
    restoreDialog.value = true;
  }

  function doRestore() {
    if (isUploadRestore.value) {
      restoreFromUpload(uploadFile.value);
    } else {
      restoreDatabase(pendingRestoreFile.value);
    }
    restoreDialog.value = false;
  }

  function confirmDelete(filename) {
    pendingDeleteFile.value = filename;
    deleteDialog.value = true;
  }

  function doDelete() {
    deleteBackup(pendingDeleteFile.value);
    deleteDialog.value = false;
  }

  function formatDate(dt) {
    return new Date(dt).toLocaleString();
  }

  function formatSize(bytes) {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / 1048576).toFixed(1) + " MB";
  }
</script>
