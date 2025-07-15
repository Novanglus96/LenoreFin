<template>
  <v-card variant="outlined" :elevation="4" class="bg-white ma-0 pa-0 ga-0">
    <template v-slot:title>
      <span class="text-subtitle-2 text-secondary">Budgets</span>
      <v-tooltip text="Add Budget" v-if="!props.widget">
        <template v-slot:activator="{ props }">
          <v-btn
            icon="mdi-plus-circle"
            variant="plain"
            size="small"
            @click="showAddForm = true"
            v-bind="props"
          ></v-btn>
        </template>
      </v-tooltip>
      <AddBudgetForm
        v-model="showAddForm"
        @update-dialog="closeAddForm"
        v-if="!isMobile"
      />
      <AddBudgetFormMobile
        v-model="showAddForm"
        @update-dialog="closeAddForm"
        v-if="isMobile"
      />
    </template>

    <template v-slot:text>
      <v-slide-group
        v-model="budget_selected"
        class="pa-4"
        show-arrows
        selected-class="bg-grey-lighten-2"
        center-active
        mobile-breakpoint="sm"
      >
        <v-slide-group-item :key="-1" v-if="isLoading">
          <v-skeleton-loader
            type="card"
            height="200"
            width="150"
            v-if="isLoading"
          ></v-skeleton-loader>
        </v-slide-group-item>
        <v-slide-group-item
          v-for="budget in budgets"
          :key="budget.budget.id"
          v-slot="{ toggle, selectedClass }"
          @group:selected="clickSelectBudget"
          :value="budget"
          :disabled="props.widget"
        >
          <v-card
            :class="['ma-4 text-center', selectedClass]"
            height="200"
            @click="toggle"
          >
            <v-card-text>
              <div class="text-subtitle-2 text-center font-weight-bold">
                {{ budget.budget.name }}
              </div>
              <v-progress-circular
                :model-value="budget.used_percentage"
                :size="100"
                :width="12"
                :color="graphColor(budget.used_percentage)"
              >
                {{
                  formatCurrency(
                    parseFloat(budget.budget.amount) +
                      parseFloat(budget.budget.roll_over_amt) -
                      parseFloat(Math.abs(budget.used_total)),
                  )
                }}
              </v-progress-circular>
              <div class="text-subtitle-2 text-center">
                Budget:
                {{
                  formatCurrency(
                    parseFloat(budget.budget.amount) +
                      parseFloat(budget.budget.roll_over_amt),
                  )
                }}
                <span
                  :class="
                    budget.budget.roll_over_amt < 0 ? 'text-red' : 'text-green'
                  "
                  v-if="budget.budget.roll_over"
                >
                  ({{ formatCurrency(budget.budget.roll_over_amt) }})
                </span>
              </div>
              <div class="text-subtitle-2 text-center">
                Used: {{ formatCurrency(Math.abs(budget.used_total)) }}
              </div>
            </v-card-text>
          </v-card>
        </v-slide-group-item>
        <v-slide-group-item v-if="budgets && budgets.length == 0" :key="-2">
          <v-card class="ma-4 text-center">
            <v-card-text>
              <div class="text-subtitle-2 text-center font-weight-bold">
                No Budgets
              </div>
            </v-card-text>
          </v-card>
        </v-slide-group-item>
      </v-slide-group>
    </template>
  </v-card>
</template>
<script setup>
  import { defineProps, ref, defineEmits } from "vue";
  import { useBudgets } from "@/composables/budgetsComposable";
  import AddBudgetForm from "./AddBudgetForm.vue";
  import AddBudgetFormMobile from "./AddBudgetFormMobile.vue";
  import { useDisplay } from "vuetify";

  const { smAndDown } = useDisplay();
  const isMobile = smAndDown;

  const props = defineProps({
    widget: Boolean,
  });
  const budget_selected = ref(null);
  const emit = defineEmits(["budgetSelected"]);
  const { budgets, isLoading } = useBudgets(props.widget);
  const showAddForm = ref(false);

  const formatCurrency = value => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };
  const graphColor = value => {
    const thresholds = [
      { limit: 10, color: "green" },
      { limit: 20, color: "green-darken-1" },
      { limit: 30, color: "green-darken-2" },
      { limit: 40, color: "green-darken-3" },
      { limit: 50, color: "green-darken-4" },
      { limit: 60, color: "yellow" },
      { limit: 70, color: "yellow-darken-1" },
      { limit: 80, color: "yellow-darken-2" },
      { limit: 90, color: "yellow-darken-3" },
      { limit: 100, color: "yellow-darken-4" },
    ];

    for (const { limit, color } of thresholds) {
      if (value <= limit) return color;
    }

    return "error";
  };

  const clickSelectBudget = () => {
    emit("budgetSelected", budget_selected.value);
  };

  const closeAddForm = () => {
    showAddForm.value = false;
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
</style>
