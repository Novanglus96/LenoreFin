<template>
  <v-card variant="outlined" :elevation="4" class="bg-white">
    <template v-slot:append>
      <v-tooltip text="Add Overage Rule" location="top">
        <template v-slot:activator="{ props }">
          <v-btn
            icon="mdi-water-plus"
            flat
            variant="plain"
            v-bind="props"
            @click="addContributionRuleDialog = true"
          ></v-btn>
        </template>
      </v-tooltip>
    </template>
    <ContributionRuleForm
      v-model="addContributionRuleDialog"
      key="0"
      :isEdit="false"
      @update-dialog="updateAddDialog"
      @add-contribution-rule="clickAddContributionRule"
      :passedFormData="newContributionRuleData"
    />
    <template v-slot:title>
      <span class="text-subtitle-2 text-secondary"
        >Per Paycheck Overage Rules</span
      >
    </template>
    <template v-slot:text>
      <v-data-iterator
        :items="contributionRules ? contributionRules : []"
        :loading="isLoading"
        items-per-page="10"
      >
        <template v-slot:default="{ items }">
          <template v-for="(item, i) in items" :key="i">
            <v-card class="flex ma-0 pa-0 ga-0"
              ><v-card-text
                ><v-container class="flex ma-0 pa-0 ga-0"
                  ><v-row dense
                    ><v-col
                      class="d-flex justify-center align-center font-weight-bold"
                      cols="1"
                      >{{ item.raw.order }}</v-col
                    ><v-col
                      ><v-container
                        ><v-row dense
                          ><v-col cols="2" class="font-weight-bold text-right"
                            >rule</v-col
                          ><v-col>{{ item.raw.rule }}</v-col></v-row
                        ><v-row dense
                          ><v-col cols="2" class="font-weight-bold text-right"
                            >cap</v-col
                          ><v-col>{{ item.raw.cap }}</v-col></v-row
                        ></v-container
                      ></v-col
                    ></v-row
                  ></v-container
                ></v-card-text
              ><v-card-actions
                ><v-spacer></v-spacer
                ><v-btn @click="clickEditButton(i, item.raw)">Edit</v-btn
                ><ContributionRuleForm
                  v-model="editContributionRuleDialog[i]"
                  :key="item.raw.id"
                  :isEdit="true"
                  @update-dialog="clickEditButton(i)"
                  :passedFormData="selectedContributionRule"
                  @edit-contribution-rule="clickEditContributionRule"
                />
                <v-btn @click="clickDeleteButton(i, item.raw)">Delete</v-btn
                ><v-dialog
                  v-model="deleteContributionRuleDialog[i]"
                  :key="item.raw.id"
                  width="400"
                  ><v-card
                    ><v-card-title>Delete Rule?</v-card-title
                    ><v-card-text
                      ><span>{{
                        selectedContributionRule.rule
                      }}</span></v-card-text
                    >
                    <v-card-actions
                      ><v-btn @click="clickDeleteButton(i)">Close</v-btn
                      ><v-btn
                        @click="
                          clickDeleteContributionRule(
                            selectedContributionRule,
                            i,
                          )
                        "
                        >Delete</v-btn
                      ></v-card-actions
                    ></v-card
                  ></v-dialog
                ></v-card-actions
              ></v-card
            >
            <br />
          </template>
        </template>
        <template v-slot:loader
          ><v-skeleton-loader
            class="border"
            type="paragraph"
          ></v-skeleton-loader
        ></template>
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
import { ref } from "vue";
import { useContributionRules } from "@/composables/contributionsComposable";
import ContributionRuleForm from "@/components/ContributionRuleForm.vue";

const editContributionRuleDialog = ref({});
const addContributionRuleDialog = ref(false);
const deleteContributionRuleDialog = ref({});
const selectedContributionRule = ref(null);
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

const updateAddDialog = () => {
  addContributionRuleDialog.value = false;
};

const clickEditButton = (index, contributionRule) => {
  if (contributionRule) {
    selectedContributionRule.value = contributionRule;
  }
  editContributionRuleDialog.value[index] =
    !editContributionRuleDialog.value[index];
};

const clickDeleteButton = (index, contributionRule) => {
  if (contributionRule) {
    selectedContributionRule.value = contributionRule;
  }
  deleteContributionRuleDialog.value[index] =
    !deleteContributionRuleDialog.value[index];
};

const clickEditContributionRule = contributionRule => {
  editContributionRule(contributionRule);
};

const clickDeleteContributionRule = contributionRule => {
  removeContributionRule(contributionRule);
};

const clickAddContributionRule = contributionRule => {
  addContributionRule(contributionRule);
  addContributionRuleDialog.value = false;
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

.icon-with-text {
  position: relative;
  display: inline-block;
}

.icon-text {
  position: absolute;
  top: 0;
  right: 1;
  color: black;
  padding: 4px 1px;
  font-size: 0.7rem;
}
</style>
