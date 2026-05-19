<template>
  <v-container fluid>
    <v-row>
      <v-col>
        <h4 class="text-h5 font-weight-bold mb-2">Application Logs</h4>
      </v-col>
      <v-col class="d-flex justify-end align-center">
        <v-btn
          prepend-icon="mdi-download"
          variant="outlined"
          size="small"
          :loading="isDownloading"
          @click="handleDownloadBundle"
          :disabled="!isOnline"
        >
          Download Log Bundle
        </v-btn>
      </v-col>
    </v-row>

    <!-- Log type tabs -->
    <v-tabs v-model="activeTab" color="primary" class="mb-4">
      <v-tab value="error">
        <v-icon start>mdi-alert-circle</v-icon>
        Error
      </v-tab>
      <v-tab value="api">
        <v-icon start>mdi-api</v-icon>
        API
      </v-tab>
      <v-tab value="task">
        <v-icon start>mdi-cog-play</v-icon>
        Task
      </v-tab>
    </v-tabs>

    <!-- Filters -->
    <v-row dense class="mb-2">
      <v-col cols="12" sm="4" md="3">
        <v-select
          v-model="selectedLevel"
          label="Level"
          :items="levelOptions"
          item-title="label"
          item-value="value"
          density="compact"
          variant="outlined"
          multiple
          clearable
          hide-details
        ></v-select>
      </v-col>
      <v-col cols="12" sm="6" md="5">
        <v-text-field
          v-model="searchText"
          label="Search"
          density="compact"
          variant="outlined"
          prepend-inner-icon="mdi-magnify"
          clearable
          hide-details
          @keyup.enter="applySearch"
          @click:clear="clearSearch"
        ></v-text-field>
      </v-col>
      <v-col cols="auto" class="d-flex align-center">
        <v-btn size="small" variant="text" icon="mdi-refresh" @click="refetch"></v-btn>
      </v-col>
    </v-row>

    <!-- Log table -->
    <v-sheet border rounded>
      <v-data-table
        :headers="headers"
        :items="entries"
        :loading="isLoading"
        density="compact"
        no-data-text="No log entries found"
        :items-per-page="-1"
        hide-default-footer
        @click:row="(_, { item }) => openDetail(item)"
      >
        <template v-slot:item.timestamp="{ item }">
          <span class="text-caption text-no-wrap">{{ item.timestamp }}</span>
        </template>
        <template v-slot:item.level="{ item }">
          <v-chip :color="levelColor(item.level)" size="x-small" label>
            {{ item.level }}
          </v-chip>
        </template>
        <template v-slot:item.message="{ item }">
          <span class="text-caption" style="font-family: monospace; white-space: pre-wrap">{{
            truncate(item.message)
          }}</span>
        </template>
      </v-data-table>
    </v-sheet>

    <!-- Pagination -->
    <v-row class="mt-2" v-if="logPage">
      <v-col class="d-flex justify-center">
        <v-pagination
          v-model="currentPage"
          :length="logPage.pages"
          :total-visible="7"
          density="compact"
        ></v-pagination>
      </v-col>
      <v-col cols="auto" class="d-flex align-center text-caption text-medium-emphasis">
        {{ logPage.total }} entries
      </v-col>
    </v-row>

    <!-- Detail dialog -->
    <v-dialog v-model="detailDialog" max-width="800">
      <v-card v-if="selectedEntry">
        <v-card-title class="d-flex align-center ga-2">
          <v-chip :color="levelColor(selectedEntry.level)" size="small" label>
            {{ selectedEntry.level }}
          </v-chip>
          <span class="text-caption text-medium-emphasis">{{ selectedEntry.timestamp }}</span>
        </v-card-title>
        <v-card-text>
          <pre class="text-caption pa-3 bg-surface-variant rounded" style="white-space: pre-wrap; overflow-x: auto">{{
            selectedEntry.message
          }}</pre>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="detailDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
  import { ref, computed, watch } from "vue";
  import { useLogs, downloadLogBundle } from "@/composables/logentriesComposable";
  import { useOnlineStatus } from "@/composables/useOnlineStatus";
  const { isOnline } = useOnlineStatus();

  const activeTab = ref("error");
  const currentPage = ref(1);
  const selectedLevel = ref([]);
  const searchText = ref("");
  const appliedSearch = ref("");
  const isDownloading = ref(false);
  const detailDialog = ref(false);
  const selectedEntry = ref(null);

  const levelOptions = [
    { label: "DEBUG", value: "DEBUG" },
    { label: "INFO", value: "INFO" },
    { label: "WARNING", value: "WARNING" },
    { label: "ERROR", value: "ERROR" },
    { label: "CRITICAL", value: "CRITICAL" },
  ];

  const headers = [
    { title: "Timestamp", key: "timestamp", width: "200px" },
    { title: "Level", key: "level", width: "100px" },
    { title: "Message", key: "message" },
  ];

  const { logPage, isLoading, refetch } = useLogs({
    logType: activeTab,
    page: currentPage,
    pageSize: ref(100),
    level: selectedLevel,
    search: appliedSearch,
  });

  const entries = computed(() => logPage.value?.entries ?? []);

  watch(activeTab, () => {
    currentPage.value = 1;
    selectedLevel.value = [];
    searchText.value = "";
    appliedSearch.value = "";
  });

  watch(selectedLevel, () => {
    currentPage.value = 1;
  });

  function applySearch() {
    appliedSearch.value = searchText.value;
    currentPage.value = 1;
  }

  function clearSearch() {
    searchText.value = "";
    appliedSearch.value = "";
    currentPage.value = 1;
  }

  function openDetail(entry) {
    selectedEntry.value = entry;
    detailDialog.value = true;
  }

  async function handleDownloadBundle() {
    isDownloading.value = true;
    await downloadLogBundle();
    isDownloading.value = false;
  }

  function levelColor(level) {
    const map = {
      DEBUG: "grey",
      INFO: "info",
      WARNING: "warning",
      ERROR: "error",
      CRITICAL: "deep-purple",
    };
    return map[level] ?? "grey";
  }

  function truncate(msg, max = 200) {
    if (!msg) return "";
    const first = msg.split("\n")[0];
    return first.length > max ? first.slice(0, max) + "…" : first;
  }
</script>
