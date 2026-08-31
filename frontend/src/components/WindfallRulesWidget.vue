<template>
  <v-card variant="outlined" :elevation="4" class="bg-surface">
    <v-card-title class="text-left">
      <span class="text-subtitle-2 text-primary">
        Per Paycheck Overage Rules
      </span>
      <v-tooltip text="Add Overage Rule" location="top" v-if="authStore.isFullAccess">
        <template v-slot:activator="{ props }">
          <v-btn
            icon="mdi-water-plus"
            flat
            variant="plain"
            v-bind="props"
            @click="addWindfallRuleDialog = true"
            size="small"
            :disabled="!isOnline"
          ></v-btn>
        </template>
      </v-tooltip>
      <WindfallRuleForm
        v-model="addWindfallRuleDialog"
        key="0"
        :isEdit="false"
        @update-dialog="updateAddDialog"
        @add-bucket-rule="clickAddBucketRule"
        :passedFormData="newWindfallRuleData"
      />
    </v-card-title>
    <v-card-text class="ma-0 pa-0 ga-0">
      <v-data-table
        :headers="displayHeaders"
        :items="windfallRules ? windfallRules : []"
        :items-length="windfallRules ? windfallRules.length : 0"
        :loading="isLoading"
        item-value="id"
        v-model:items-per-page="itemsPerPage"
        v-model:page="page"
        :items-per-page-options="[
          {
            value: 3,
            title: 3,
          },
        ]"
        items-per-page-text="Rules per page"
        no-data-text="No rules!"
        loading-text="Loading rules..."
        disable-sort
        :show-select="authStore.isFullAccess"
        fixed-footer
        striped="odd"
        density="compact"
        :hide-default-header="mdAndUp ? false : true"
        width="100%"
        :header-props="{ class: 'font-weight-bold bg-secondary' }"
        v-model="selectedBucketRule"
        select-strategy="single"
        return-object
        :row-props="getRowProps"
        class="bg-background"
      >
        <template v-slot:top>
          <div class="d-flex align-center">
            <template v-if="authStore.isFullAccess">
              <v-btn
                variant="plain"
                icon
                @click="editWindfallRuleDialog = true"
                :disabled="selectedBucketRule.length === 0 || !isOnline"
              >
                <v-icon icon="mdi-pencil"></v-icon>
              </v-btn>
              <WindfallRuleForm
                v-model="editWindfallRuleDialog"
                :key="editRule ? editRule.id : 0"
                :isEdit="true"
                @update-dialog="updateEditDialog"
                :passedFormData="editRule"
                @edit-bucket-rule="clickEditBucketRule"
              />
              <v-btn
                variant="plain"
                icon
                :disabled="selectedBucketRule.length === 0 || !isOnline"
              >
                <v-icon
                  icon="mdi-delete"
                  @click="deleteBucketRuleDialog = true"
                  color="error"
                ></v-icon>
              </v-btn>
              <v-dialog
                v-model="deleteBucketRuleDialog"
                :key="editRule ? editRule.id : 0"
                width="400"
              >
                <v-card>
                  <v-card-title>Delete Rule?</v-card-title>
                  <v-card-text>
                    <span>{{ editRule.rule }}</span>
                  </v-card-text>
                  <v-card-actions>
                    <v-btn @click="deleteBucketRuleDialog = false">
                      Close
                    </v-btn>
                    <v-btn @click="clickDeleteBucketRule(editRule)" :disabled="!isOnline">
                      Delete
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>
            </template>
          </div>
        </template>
        <template v-slot:bottom>
          <div class="text-center pt-2">
            <v-pagination v-model="page" :length="pageCount"></v-pagination>
          </div>
        </template>
        <template v-slot:[`header.order`] v-if="mdAndUp">
          <div class="text-center">Order</div>
        </template>
        <template v-slot:[`item.order`]="{ item }" v-if="mdAndUp">
          <div class="text-center">
            <span class="font-weight-bold">#{{ item.order }}</span>
          </div>
        </template>
        <template v-slot:[`item.rule`]="{ item }" v-if="mdAndUp">
          <div>
            <span>{{ item.rule }}</span>
          </div>
        </template>
        <template v-slot:[`item.cap`]="{ item }" v-if="mdAndUp">
          <div>
            <span>{{ item.cap }}</span>
          </div>
        </template>
        <!-- Mobile View -->
        <template v-slot:[`item.mobile`]="{ item }">
          <v-container class="ma-0 pa-0 ga-0">
            <v-row dense class="ma-0 pa-0 ga-0">
              <v-col
                class="ma-0 pa-0 ga-0 font-weight-bold text-center"
                cols="1"
              >
                #{{ item.order }}
              </v-col>
              <v-col
                class="ma-0 pa-0 ga-0 font-weight-bold text-right"
                cols="2"
              >
                Rule &bull;
              </v-col>
              <v-col class="ma-0 pa-0 ga-0" cols="9">
                {{ item.rule }}
              </v-col>
            </v-row>
            <v-row dense class="ma-0 pa-0 ga-0">
              <v-col class="ma-0 pa-0 ga-0 font-weight-bold" cols="1"></v-col>
              <v-col
                class="ma-0 pa-0 ga-0 font-weight-bold text-right"
                cols="2"
              >
                Cap &bull;
              </v-col>
              <v-col class="ma-0 pa-0 ga-0" cols="9">
                {{ item.cap }}
              </v-col>
            </v-row>
          </v-container>
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>
<script setup>
  import { ref, computed, watch } from "vue";
  import { useWindfallRules } from "@/composables/bucketsComposable";
  import WindfallRuleForm from "@/components/WindfallRuleForm.vue";
  import { useDisplay } from "vuetify";
  import { useAuthStore } from "@/stores/auth";
  import { useOnlineStatus } from "@/composables/useOnlineStatus";
  const { isOnline } = useOnlineStatus();

  const page = ref(1);
  const itemsPerPage = ref(3);
  const { mdAndUp } = useDisplay();
  const authStore = useAuthStore();
  const editRule = ref({ id: 0 });
  const editWindfallRuleDialog = ref(false);
  const addWindfallRuleDialog = ref(false);
  const deleteBucketRuleDialog = ref(false);
  const selectedBucketRule = ref([]);
  const newWindfallRuleData = ref({
    id: 0,
    rule: null,
    order: 1,
    cap: null,
  });

  const {
    windfallRules,
    isLoading,
    addWindfallRule,
    editWindfallRule,
    removeWindfallRule,
  } = useWindfallRules();

  const headers = ref([
    { title: "Order", key: "order", width: "20px" },
    { title: "Rule", key: "rule" },
    { title: "Cap", key: "cap" },
  ]);
  const displayHeaders = computed(() => {
    if (mdAndUp.value) {
      return headers.value;
    }
    // For small screens, use your single mobile column
    return [{ title: "", key: "mobile" }];
  });

  const updateAddDialog = () => {
    addWindfallRuleDialog.value = false;
  };

  const updateEditDialog = () => {
    editWindfallRuleDialog.value = false;
  };

  const clickEditBucketRule = windfallRule => {
    editWindfallRule(windfallRule);
    editWindfallRuleDialog.value = false;
    selectedBucketRule.value = [];
  };

  const clickDeleteBucketRule = windfallRule => {
    removeWindfallRule(windfallRule);
    deleteBucketRuleDialog.value = false;
    selectedBucketRule.value = [];
  };

  const clickAddBucketRule = windfallRule => {
    addWindfallRule(windfallRule);
    addWindfallRuleDialog.value = false;
  };

  const pageCount = computed(() =>
    windfallRules.value && itemsPerPage.value
      ? Math.ceil(windfallRules.value.length / itemsPerPage.value)
      : 1,
  );

  watch(
    () => selectedBucketRule.value,
    val => {
      if (val) {
        editRule.value = val[0];
      }
    },
  );
  function getRowProps({ item }) {
    let rowformat = "";
    const isSelected = selectedBucketRule.value.some(
      sel => sel.id === item.id,
    );
    if (isSelected) {
      rowformat += "bg-primary-lighten-3";
    }
    return {
      class: rowformat,
    };
  }
</script>
