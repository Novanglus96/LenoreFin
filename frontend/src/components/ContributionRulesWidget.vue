<template>
  <v-card variant="outlined" :elevation="4" class="bg-surface">
    <v-card-title class="text-left">
      <span class="text-subtitle-2 text-secondary">
        Per Paycheck Overage Rules
      </span>
      <v-tooltip text="Add Overage Rule" location="top">
        <template v-slot:activator="{ props }">
          <v-btn
            icon="mdi-water-plus"
            flat
            variant="plain"
            v-bind="props"
            @click="addContributionRuleDialog = true"
            size="small"
            color="grey"
          ></v-btn>
        </template>
      </v-tooltip>
      <ContributionRuleForm
        v-model="addContributionRuleDialog"
        key="0"
        :isEdit="false"
        @update-dialog="updateAddDialog"
        @add-contribution-rule="clickAddContributionRule"
        :passedFormData="newContributionRuleData"
      />
    </v-card-title>
    <v-card-text class="ma-0 pa-0 ga-0">
      <v-data-table
        :headers="displayHeaders"
        :items="contributionRules ? contributionRules : []"
        :items-length="contributionRules ? contributionRules.length : 0"
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
        :show-select="true"
        fixed-footer
        striped="odd"
        density="compact"
        :hide-default-header="mdAndUp ? false : true"
        width="100%"
        :header-props="{ class: 'font-weight-bold bg-primary' }"
        v-model="selectedContributionRule"
        select-strategy="single"
        return-object
      >
        <template v-slot:top>
          <div class="d-flex align-center">
            <v-btn
              variant="plain"
              icon
              @click="editContributionRuleDialog = true"
              :disabled="selectedContributionRule.length === 0"
            >
              <v-icon icon="mdi-pencil"></v-icon>
            </v-btn>
            <ContributionRuleForm
              v-model="editContributionRuleDialog"
              :key="editRule ? editRule.id : 0"
              :isEdit="true"
              @update-dialog="updateEditDialog"
              :passedFormData="editRule"
              @edit-contribution-rule="clickEditContributionRule"
            />
            <v-btn
              variant="plain"
              icon
              :disabled="selectedContributionRule.length == 0"
            >
              <v-icon
                icon="mdi-delete"
                @click="deleteContributionRuleDialog = true"
                color="error"
              ></v-icon>
            </v-btn>
            <v-dialog
              v-model="deleteContributionRuleDialog"
              :key="editRule ? editRule.id : 0"
              width="400"
            >
              <v-card>
                <v-card-title>Delete Rule?</v-card-title>
                <v-card-text>
                  <span>{{ editRule.rule }}</span>
                </v-card-text>
                <v-card-actions>
                  <v-btn @click="deleteContributionRuleDialog = false">
                    Close
                  </v-btn>
                  <v-btn @click="clickDeleteContributionRule(editRule)">
                    Delete
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
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
  import { useContributionRules } from "@/composables/contributionsComposable";
  import ContributionRuleForm from "@/components/ContributionRuleForm.vue";
  import { useDisplay } from "vuetify";

  const page = ref(1);
  const itemsPerPage = ref(3);
  const { mdAndUp } = useDisplay();
  const editRule = ref({ id: 0 });
  const editContributionRuleDialog = ref(false);
  const addContributionRuleDialog = ref(false);
  const deleteContributionRuleDialog = ref(false);
  const selectedContributionRule = ref([]);
  const newContributionRuleData = ref({
    id: 0,
    rule: null,
    order: 1,
    cap: null,
  });

  const {
    contributionRules,
    isLoading,
    addContributionRule,
    editContributionRule,
    removeContributionRule,
  } = useContributionRules();

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
    addContributionRuleDialog.value = false;
  };

  const updateEditDialog = () => {
    editContributionRuleDialog.value = false;
  };

  const clickEditContributionRule = contributionRule => {
    editContributionRule(contributionRule);
    editContributionRuleDialog.value = false;
    selectedContributionRule.value = [];
  };

  const clickDeleteContributionRule = contributionRule => {
    removeContributionRule(contributionRule);
    deleteContributionRuleDialog.value = false;
    selectedContributionRule.value = [];
  };

  const clickAddContributionRule = contributionRule => {
    addContributionRule(contributionRule);
    addContributionRuleDialog.value = false;
  };

  const pageCount = computed(() =>
    contributionRules.value && itemsPerPage.value
      ? Math.ceil(contributionRules.value.length / itemsPerPage.value)
      : 1,
  );

  watch(
    () => selectedContributionRule.value,
    val => {
      if (val) {
        editRule.value = val[0];
      }
    },
  );
</script>
