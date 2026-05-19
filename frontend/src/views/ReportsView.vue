<template>
  <v-container fluid>
    <!-- Page header -->
    <v-row>
      <v-col>
        <h4 class="text-h5 font-weight-bold mb-4">Reports</h4>
      </v-col>
    </v-row>

    <v-row>
      <!-- LEFT: Saved reports list -->
      <v-col cols="12" md="3">
        <v-sheet border rounded>
          <v-container>
            <v-row dense align="center">
              <v-col>
                <span class="text-subtitle-1 font-weight-bold">Saved Reports</span>
              </v-col>
              <v-col class="d-flex justify-end">
                <v-btn
                  size="small"
                  color="primary"
                  variant="text"
                  prepend-icon="mdi-plus"
                  @click="startNewReport"
                >New</v-btn>
              </v-col>
            </v-row>

            <v-divider class="mb-2"></v-divider>

            <v-progress-linear indeterminate v-if="isLoading" color="primary"></v-progress-linear>

            <div v-if="!isLoading && (!reports || reports.length === 0)" class="text-body-2 text-medium-emphasis pa-2">
              No saved reports yet. Build one and save it.
            </div>

            <v-list density="compact" nav v-if="reports && reports.length > 0">
              <v-list-item
                v-for="report in reports"
                :key="report.id"
                :active="activeSavedId === report.id"
                color="primary"
                class="pa-1"
                @click="loadSavedReport(report)"
              >
                <v-list-item-title class="text-body-2">{{ report.name }}</v-list-item-title>
                <v-list-item-subtitle class="text-caption">
                  {{ report.report_type }} · {{ report.group_by }}
                </v-list-item-subtitle>
                <template v-slot:append>
                  <v-btn
                    icon="mdi-delete"
                    size="x-small"
                    variant="text"
                    color="error"
                    @click.stop="confirmDelete(report)"
                  ></v-btn>
                </template>
              </v-list-item>
            </v-list>
          </v-container>
        </v-sheet>
      </v-col>

      <!-- RIGHT: Builder + Results -->
      <v-col cols="12" md="9">
        <!-- Report Builder -->
        <v-sheet border rounded class="mb-4">
          <v-container>
            <v-row dense align="center">
              <v-col>
                <span class="text-subtitle-1 font-weight-bold">
                  {{ activeSavedId ? 'Edit Report' : 'Report Builder' }}
                </span>
              </v-col>
            </v-row>

            <v-row dense>
              <!-- Report Type -->
              <v-col cols="12" sm="6" md="3">
                <v-select
                  label="Report Type"
                  v-model="form.report_type"
                  :items="reportTypeOptions"
                  item-title="label"
                  item-value="value"
                  density="comfortable"
                  variant="outlined"
                  hide-details
                ></v-select>
              </v-col>

              <!-- Date Range (TOTALS only) -->
              <template v-if="form.report_type !== 'COMPARISON'">
                <v-col cols="12" sm="6" md="3">
                  <v-select
                    label="Date Range"
                    v-model="form.date_range_type"
                    :items="dateRangeOptions"
                    item-title="label"
                    item-value="value"
                    density="comfortable"
                    variant="outlined"
                    hide-details
                  ></v-select>
                </v-col>

                <!-- Custom date range -->
                <template v-if="form.date_range_type === 'CUSTOM'">
                  <v-col cols="12" sm="6" md="3">
                    <v-text-field
                      label="From"
                      v-model="form.date_from"
                      type="date"
                      density="comfortable"
                      variant="outlined"
                      hide-details
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="6" md="3">
                    <v-text-field
                      label="To"
                      v-model="form.date_to"
                      type="date"
                      density="comfortable"
                      variant="outlined"
                      hide-details
                    ></v-text-field>
                  </v-col>
                </template>
              </template>

              <!-- Year pickers (COMPARISON only) -->
              <template v-if="form.report_type === 'COMPARISON'">
                <v-col cols="12" sm="6" md="3">
                  <v-select
                    label="Year 1 (Primary)"
                    v-model="form.year1"
                    :items="yearOptions"
                    density="comfortable"
                    variant="outlined"
                    hide-details
                  ></v-select>
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-select
                    label="Year 2 (Compare Against)"
                    v-model="form.year2"
                    :items="yearOptions"
                    density="comfortable"
                    variant="outlined"
                    hide-details
                  ></v-select>
                </v-col>
              </template>

              <!-- Group By -->
              <v-col cols="12" sm="6" md="3">
                <v-select
                  label="Group By"
                  v-model="form.group_by"
                  :items="groupByOptions"
                  item-title="label"
                  item-value="value"
                  density="comfortable"
                  variant="outlined"
                  hide-details
                ></v-select>
              </v-col>
            </v-row>

            <v-row dense class="mt-2">
              <!-- Account filter -->
              <v-col cols="12" md="6">
                <v-autocomplete
                  label="Accounts (empty = all)"
                  v-model="form.account_ids"
                  :items="accountItems"
                  item-title="label"
                  item-value="id"
                  multiple
                  chips
                  closable-chips
                  density="comfortable"
                  variant="outlined"
                  hide-details
                  clearable
                ></v-autocomplete>
              </v-col>

              <!-- Tag selector -->
              <v-col cols="12" md="6">
                <v-autocomplete
                  label="Tags (empty = all)"
                  v-model="form.tag_selections"
                  :items="tagItems"
                  item-title="label"
                  item-value="id"
                  :return-object="true"
                  multiple
                  chips
                  closable-chips
                  density="comfortable"
                  variant="outlined"
                  hide-details
                  clearable
                >
                  <template v-slot:chip="{ props, item }">
                    <v-chip v-bind="props" size="small">
                      <template v-slot:prepend>
                        <v-icon
                          :icon="item.raw.is_system ? 'mdi-tag' : 'mdi-tag-outline'"
                          :color="tagColor(item.raw.tag_type_id)"
                          size="x-small"
                          class="mr-1"
                        ></v-icon>
                      </template>
                      {{ item.raw.label }}
                    </v-chip>
                  </template>
                  <template v-slot:item="{ props, item }">
                    <v-list-item v-bind="props">
                      <template v-slot:prepend>
                        <v-icon
                          :icon="item.raw.is_system ? 'mdi-tag' : 'mdi-tag-outline'"
                          :color="tagColor(item.raw.tag_type_id)"
                        ></v-icon>
                      </template>
                    </v-list-item>
                  </template>
                </v-autocomplete>
              </v-col>
            </v-row>

            <v-row dense class="mt-2">
              <v-col cols="auto">
                <v-checkbox
                  v-model="form.show_subtotal"
                  label="Show Subtotal"
                  density="compact"
                  hide-details
                ></v-checkbox>
              </v-col>
              <v-col cols="auto">
                <v-checkbox
                  v-model="form.include_pending"
                  label="Include Pending"
                  density="compact"
                  hide-details
                ></v-checkbox>
              </v-col>
              <v-col cols="auto" v-if="form.report_type === 'TOTALS'">
                <v-checkbox
                  v-model="form.show_transactions"
                  label="Show Transactions"
                  density="compact"
                  hide-details
                ></v-checkbox>
              </v-col>
            </v-row>

            <v-row dense class="mt-3">
              <v-col cols="auto">
                <v-btn
                  color="primary"
                  prepend-icon="mdi-play"
                  :loading="isRunning"
                  @click="executeReport"
                >Run Report</v-btn>
              </v-col>
              <v-col cols="auto" v-if="results">
                <v-btn
                  color="secondary"
                  variant="outlined"
                  :prepend-icon="activeSavedId ? 'mdi-content-save-edit' : 'mdi-content-save'"
                  :loading="isSaving"
                  @click="activeSavedId ? openUpdateDialog() : openSaveDialog()"
                >
                  {{ activeSavedId ? 'Update Report' : 'Save Report' }}
                </v-btn>
              </v-col>
              <v-col cols="auto" v-if="results">
                <v-btn
                  variant="text"
                  prepend-icon="mdi-printer"
                  @click="printResults"
                >Print</v-btn>
              </v-col>
            </v-row>
          </v-container>
        </v-sheet>

        <!-- Results -->
        <v-sheet border rounded v-if="results" id="report-results">
          <v-container>
            <v-row dense align="center">
              <v-col>
                <span class="text-subtitle-1 font-weight-bold">Results</span>
                <span class="text-caption text-medium-emphasis ml-2">
                  {{ formatDateRange(results) }}
                </span>
              </v-col>
            </v-row>

            <!-- TOTALS results -->
            <template v-if="results.report_type === 'TOTALS'">
              <v-data-table
                :headers="totalsHeaders"
                :items="results.rows"
                density="compact"
                :expand-on-click="form.show_transactions"
                show-expand
                v-if="form.show_transactions"
              >
                <template v-slot:item.total="{ item }">
                  <span :class="item.total < 0 ? 'text-error' : 'text-success'">
                    {{ formatCurrency(item.total) }}
                  </span>
                </template>
                <template v-slot:expanded-row="{ columns, item }">
                  <tr v-if="item.transactions && item.transactions.length">
                    <td :colspan="columns.length" class="pa-2">
                      <v-data-table
                        :headers="txHeaders"
                        :items="item.transactions"
                        density="compact"
                        hide-default-footer
                      >
                        <template v-slot:item.amount="{ item: tx }">
                          <span :class="tx.amount < 0 ? 'text-error' : 'text-success'">
                            {{ formatCurrency(tx.amount) }}
                          </span>
                        </template>
                      </v-data-table>
                    </td>
                  </tr>
                  <tr v-else>
                    <td :colspan="columns.length" class="text-caption text-medium-emphasis pa-2">
                      No transactions
                    </td>
                  </tr>
                </template>
                <template v-slot:body.append v-if="results.subtotal !== null && results.subtotal !== undefined">
                  <tr class="font-weight-bold" style="border-top: 2px solid rgba(128,128,128,0.3)">
                    <td></td>
                    <td class="pa-2">Total</td>
                    <td class="text-end pa-2" :class="results.subtotal < 0 ? 'text-error' : 'text-success'">
                      {{ formatCurrency(results.subtotal) }}
                    </td>
                  </tr>
                </template>
              </v-data-table>

              <v-data-table
                :headers="totalsHeaders"
                :items="results.rows"
                density="compact"
                v-else
              >
                <template v-slot:item.total="{ item }">
                  <span :class="item.total < 0 ? 'text-error' : 'text-success'">
                    {{ formatCurrency(item.total) }}
                  </span>
                </template>
                <template v-slot:body.append v-if="results.subtotal !== null && results.subtotal !== undefined">
                  <tr class="font-weight-bold" style="border-top: 2px solid rgba(128,128,128,0.3)">
                    <td class="pa-2">Total</td>
                    <td class="text-end pa-2" :class="results.subtotal < 0 ? 'text-error' : 'text-success'">
                      {{ formatCurrency(results.subtotal) }}
                    </td>
                  </tr>
                </template>
              </v-data-table>
            </template>

            <!-- COMPARISON results -->
            <template v-else-if="results.report_type === 'COMPARISON'">
              <v-data-table
                :headers="comparisonHeaders"
                :items="results.rows"
                density="compact"
              >
                <template v-slot:item.period1_total="{ item }">
                  <span :class="item.period1_total < 0 ? 'text-error' : 'text-success'">
                    {{ formatCurrency(item.period1_total) }}
                  </span>
                </template>
                <template v-slot:item.period2_total="{ item }">
                  <span :class="item.period2_total < 0 ? 'text-error' : 'text-success'">
                    {{ formatCurrency(item.period2_total) }}
                  </span>
                </template>
                <template v-slot:item.difference="{ item }">
                  <span :class="item.difference < 0 ? 'text-error' : 'text-success'">
                    {{ formatCurrency(item.difference) }}
                  </span>
                </template>
                <template v-slot:body.append v-if="results.subtotal !== null && results.subtotal !== undefined">
                  <tr class="font-weight-bold" style="border-top: 2px solid rgba(128,128,128,0.3)">
                    <td class="pa-2">Total</td>
                    <td class="text-end pa-2" :class="results.subtotal < 0 ? 'text-error' : 'text-success'">
                      {{ formatCurrency(results.subtotal) }}
                    </td>
                    <td class="text-end pa-2" :class="results.subtotal2 < 0 ? 'text-error' : 'text-success'">
                      {{ formatCurrency(results.subtotal2) }}
                    </td>
                    <td class="text-end pa-2" :class="(results.subtotal - results.subtotal2) < 0 ? 'text-error' : 'text-success'">
                      {{ formatCurrency(results.subtotal - results.subtotal2) }}
                    </td>
                  </tr>
                </template>
              </v-data-table>
            </template>
          </v-container>
        </v-sheet>
      </v-col>
    </v-row>

    <!-- Save dialog -->
    <v-dialog v-model="saveDialog" max-width="420">
      <v-card>
        <v-card-title class="text-h6">Save Report</v-card-title>
        <v-card-text>
          <v-text-field
            label="Report Name"
            v-model="saveName"
            density="comfortable"
            variant="outlined"
            autofocus
          ></v-text-field>
          <v-textarea
            label="Description (optional)"
            v-model="saveDescription"
            density="comfortable"
            variant="outlined"
            rows="2"
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="saveDialog = false">Cancel</v-btn>
          <v-btn color="primary" :loading="isSaving" @click="doSave">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Update name dialog -->
    <v-dialog v-model="updateDialog" max-width="420">
      <v-card>
        <v-card-title class="text-h6">Update Report</v-card-title>
        <v-card-text>
          <v-text-field
            label="Report Name"
            v-model="saveName"
            density="comfortable"
            variant="outlined"
            autofocus
          ></v-text-field>
          <v-textarea
            label="Description (optional)"
            v-model="saveDescription"
            density="comfortable"
            variant="outlined"
            rows="2"
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="updateDialog = false">Cancel</v-btn>
          <v-btn color="primary" :loading="isSaving" @click="doUpdate">Update</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete confirm -->
    <v-dialog v-model="deleteDialog" max-width="380">
      <v-card>
        <v-card-title class="text-h6">Delete Report</v-card-title>
        <v-card-text>
          Delete <strong>{{ pendingDelete?.name }}</strong>? This cannot be undone.
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
  import { ref, computed } from "vue";
  import { useReports } from "@/composables/reportsComposable";
  import { useAccounts } from "@/composables/accountsComposable";
  import { useTags } from "@/composables/tagsComposable";
  import { useMainStore } from "@/stores/main";

  const mainStore = useMainStore();
  const reportsComposable = useReports();
  const { reports, isLoading, saveReport, updateReport, deleteReport, isSaving, isRunning } = reportsComposable;
  const { accounts } = useAccounts(false);
  const { tags } = useTags();

  // ---------------------------------------------------------------------------
  // Form state
  // ---------------------------------------------------------------------------
  const currentYear = new Date().getFullYear();

  const defaultForm = () => ({
    report_type: "TOTALS",
    date_range_type: "THIS_YEAR",
    date_from: null,
    date_to: null,
    year1: currentYear,
    year2: currentYear - 1,
    group_by: "TAG",
    account_ids: [],
    tag_selections: [],
    show_subtotal: true,
    include_pending: false,
    show_transactions: false,
  });

  const form = ref(defaultForm());
  const results = ref(null);
  const activeSavedId = ref(null);
  const activeSavedName = ref("");
  const activeSavedDescription = ref("");

  const saveDialog = ref(false);
  const updateDialog = ref(false);
  const deleteDialog = ref(false);
  const saveName = ref("");
  const saveDescription = ref("");
  const pendingDelete = ref(null);

  // ---------------------------------------------------------------------------
  // Dropdown options
  // ---------------------------------------------------------------------------
  const reportTypeOptions = [
    { label: "Totals", value: "TOTALS" },
    { label: "Comparison", value: "COMPARISON" },
  ];

  const dateRangeOptions = [
    { label: "This Year", value: "THIS_YEAR" },
    { label: "Last Year", value: "LAST_YEAR" },
    { label: "This Quarter", value: "THIS_QUARTER" },
    { label: "Last Quarter", value: "LAST_QUARTER" },
    { label: "Trailing 12 Months", value: "TRAILING_12" },
    { label: "Custom", value: "CUSTOM" },
  ];

  const yearOptions = Array.from({ length: 10 }, (_, i) => currentYear - i);

  const groupByOptions = computed(() => {
    const opts = [{ label: "Tag", value: "TAG" }];
    if (form.value.report_type === "TOTALS") {
      opts.push({ label: "Month", value: "MONTH" });
    }
    return opts;
  });

  // ---------------------------------------------------------------------------
  // Account items
  // ---------------------------------------------------------------------------
  const accountItems = computed(() =>
    (accounts.value ?? []).map(a => ({ id: a.id, label: a.account_name }))
  );

  // ---------------------------------------------------------------------------
  // Tag items — flat list of leaf tags (tag_name includes parent path)
  // ---------------------------------------------------------------------------
  const tagItems = computed(() =>
    (tags.value ?? []).map(t => ({
      id: t.id,
      label: t.tag_name,
      is_system: t.is_system,
      tag_type_id: t.tag_type?.id ?? null,
    }))
  );

  function tagColor(typeId) {
    if (typeId === 1) return "error";
    if (typeId === 2) return "success";
    return "info";
  }

  // ---------------------------------------------------------------------------
  // Table headers
  // ---------------------------------------------------------------------------
  const totalsHeaders = [
    { title: "Label", key: "label" },
    { title: "Total", key: "total", align: "end" },
  ];

  const txHeaders = [
    { title: "Date", key: "date" },
    { title: "Description", key: "description" },
    { title: "Account", key: "account" },
    { title: "Amount", key: "amount", align: "end" },
  ];

  const comparisonHeaders = computed(() => {
    const p1 = results.value ? formatDateLabel(results.value.date_from, results.value.date_to) : "Period 1";
    const p2 = results.value ? formatDateLabel(results.value.period2_from, results.value.period2_to) : "Period 2";
    return [
      { title: "Label", key: "label" },
      { title: p1, key: "period1_total", align: "end" },
      { title: p2, key: "period2_total", align: "end" },
      { title: "Difference", key: "difference", align: "end" },
    ];
  });

  // ---------------------------------------------------------------------------
  // Actions
  // ---------------------------------------------------------------------------
  function startNewReport() {
    activeSavedId.value = null;
    activeSavedName.value = "";
    activeSavedDescription.value = "";
    form.value = defaultForm();
    results.value = null;
  }

  function loadSavedReport(report) {
    activeSavedId.value = report.id;
    activeSavedName.value = report.name;
    activeSavedDescription.value = report.description ?? "";

    const selItems = (report.tag_selections ?? [])
      .filter(sel => sel.tag_id)
      .map(sel => tagItems.value.find(t => t.id === sel.tag_id))
      .filter(Boolean);

    const isComparison = report.report_type === "COMPARISON";
    form.value = {
      report_type: report.report_type,
      date_range_type: isComparison ? "THIS_YEAR" : report.date_range_type,
      date_from: isComparison ? null : (report.date_from ?? null),
      date_to: isComparison ? null : (report.date_to ?? null),
      year1: isComparison && report.date_from
        ? parseInt(report.date_from.slice(0, 4))
        : currentYear,
      year2: isComparison && report.period2_date_from
        ? parseInt(report.period2_date_from.slice(0, 4))
        : currentYear - 1,
      group_by: report.group_by,
      account_ids: report.account_ids ?? [],
      tag_selections: selItems,
      show_subtotal: report.show_subtotal,
      include_pending: report.include_pending,
      show_transactions: report.show_transactions,
    };
    results.value = null;
  }

  function buildPayload() {
    const isComparison = form.value.report_type === "COMPARISON";
    return {
      report_type: form.value.report_type,
      date_range_type: isComparison ? "CUSTOM" : form.value.date_range_type,
      date_from: isComparison ? `${form.value.year1}-01-01` : (form.value.date_from || null),
      date_to: isComparison ? `${form.value.year1}-12-31` : (form.value.date_to || null),
      period2_date_from: isComparison ? `${form.value.year2}-01-01` : null,
      period2_date_to: isComparison ? `${form.value.year2}-12-31` : null,
      group_by: form.value.group_by,
      account_ids: form.value.account_ids,
      tag_selections: (form.value.tag_selections ?? []).map(sel => ({
        tag_id: sel.id,
        sub_tag_id: null,
        main_tag_id: null,
      })),
      show_subtotal: form.value.show_subtotal,
      include_pending: form.value.include_pending,
      show_transactions: isComparison ? false : form.value.show_transactions,
    };
  }

  async function executeReport() {
    results.value = null;
    try {
      const payload = buildPayload();
      const data = await reportsComposable.runReport(payload);
      results.value = data;
    } catch {
      // error shown by composable
    }
  }

  function openSaveDialog() {
    saveName.value = "";
    saveDescription.value = "";
    saveDialog.value = true;
  }

  function openUpdateDialog() {
    saveName.value = activeSavedName.value;
    saveDescription.value = activeSavedDescription.value;
    updateDialog.value = true;
  }

  function doSave() {
    if (!saveName.value.trim()) {
      mainStore.showSnackbar("Please enter a report name", "warning");
      return;
    }
    const payload = {
      name: saveName.value.trim(),
      description: saveDescription.value.trim(),
      ...buildPayload(),
    };
    saveReport(payload);
    saveDialog.value = false;
  }

  function doUpdate() {
    if (!saveName.value.trim()) {
      mainStore.showSnackbar("Please enter a report name", "warning");
      return;
    }
    const payload = {
      name: saveName.value.trim(),
      description: saveDescription.value.trim(),
      ...buildPayload(),
    };
    updateReport(activeSavedId.value, payload);
    activeSavedName.value = saveName.value.trim();
    activeSavedDescription.value = saveDescription.value.trim();
    updateDialog.value = false;
  }

  function confirmDelete(report) {
    pendingDelete.value = report;
    deleteDialog.value = true;
  }

  function doDelete() {
    deleteReport(pendingDelete.value.id);
    if (activeSavedId.value === pendingDelete.value.id) {
      startNewReport();
    }
    deleteDialog.value = false;
  }

  function printResults() {
    window.print();
  }

  // ---------------------------------------------------------------------------
  // Formatting helpers
  // ---------------------------------------------------------------------------
  function formatCurrency(value) {
    if (value === null || value === undefined) return "—";
    const num = parseFloat(value);
    return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(num);
  }

  function formatDateLabel(from, to) {
    if (!from || !to) return "";
    return `${from} – ${to}`;
  }

  function formatDateRange(result) {
    if (!result) return "";
    const p1 = `${result.date_from} – ${result.date_to}`;
    if (result.report_type === "COMPARISON") {
      return `${p1}  vs  ${result.period2_from} – ${result.period2_to}`;
    }
    return p1;
  }
</script>

<style>
  @media print {
    /* Hide everything except the results panel */
    .v-app-bar,
    .v-navigation-drawer,
    .v-col:first-child,
    .v-sheet:not(#report-results) {
      display: none !important;
    }
    #report-results {
      border: none !important;
      box-shadow: none !important;
    }
  }
</style>
