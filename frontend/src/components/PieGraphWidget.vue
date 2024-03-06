<template>
  <div>
    <v-card
      variant="outlined"
      :elevation="4"
      class="bg-white"
      v-if="!isLoading"
    >
      <template v-slot:append>
        <v-menu location="start" :close-on-content-click="false">
          <template v-slot:activator="{ props }">
            <v-btn
              icon="mdi-cog"
              flat
              size="xs"
              v-bind="props"
              :disabled="isLoading"
            >
            </v-btn>
          </template>
          <v-card width="350">
            <v-card-title>Widget {{ props.widget }}</v-card-title>
            <v-card-subtitle>Settings</v-card-subtitle>
            <v-card-text>
              <v-container>
                <v-row dense>
                  <v-col>
                    <v-text-field
                      v-model="formData.graph_name"
                      variant="outlined"
                      label="Graph Name*"
                      :rules="required"
                      @update:model-value="checkFormComplete"
                    ></v-text-field>
                  </v-col>
                </v-row>
              </v-container>
            </v-card-text>
            <v-card-actions
              ><v-btn :disabled="!formComplete" @click="submitForm()"
                >Save</v-btn
              ></v-card-actions
            >
          </v-card>
        </v-menu>
      </template>
      <template v-slot:title>
        <span class="text-subtitle-2 text-secondary">{{
          tag_graph ? tag_graph.datasets[0].label : ""
        }}</span>
      </template>
      <template v-slot:text>
        <Pie :data="tag_graph" :options="options" />
      </template>
    </v-card>
    <v-progress-circular
      color="secondary"
      indeterminate
      :size="300"
      :width="12"
      v-else
      >Loading...</v-progress-circular
    >
  </div>
</template>

<script setup>
import { Pie } from "vue-chartjs";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import { ref, defineProps } from "vue";
import { useGraphs } from "@/composables/tagsComposable";
import { useOptions } from "@/composables/optionsComposable";

const { options: appOptions, editOptions } = useOptions();
const formData = ref(null);
ChartJS.register(ArcElement, Tooltip, Legend);
const props = defineProps({
  widget: {
    type: Number,
    default: 1,
  },
});
if (props.widget == 1) {
  formData.value = {
    graph_name: appOptions.widget1_graph_name,
    month: appOptions.widget1_month,
    tag_id: appOptions.widget1_tag_id,
    expense: appOptions.widget1_expense,
    exlude: appOptions.widget1_exclude,
  };
}
if (props.widget == 2) {
  formData.value = {
    graph_name: appOptions.widget2_graph_name,
    month: appOptions.widget2_month,
    tag_id: appOptions.widget2_tag_id,
    expense: appOptions.widget2_expense,
    exlude: appOptions.widget2_exclude,
  };
}
if (props.widget == 3) {
  formData.value = {
    graph_name: appOptions.widget3_graph_name,
    month: appOptions.widget3_month,
    tag_id: appOptions.widget3_tag_id,
    expense: appOptions.widget3_expense,
    exlude: appOptions.widget3_exclude,
  };
}

const formComplete = ref(false);
const { tag_graph, isLoading } = useGraphs(props.widget);

const options = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: "right",
    },
    tooltip: {
      callbacks: {
        label: function (tooltipItem) {
          var total = tooltipItem.dataset.data.reduce(function (
            previousValue,
            currentValue,
          ) {
            var previousNumber = +previousValue;
            var currentNumber = +currentValue;
            return previousNumber + currentNumber;
          });
          var currentValue = tooltipItem.dataset.data[tooltipItem.dataIndex];
          var percentage = Math.floor((currentValue / total) * 100 + 0.5);
          return "$" + currentValue + " (" + percentage + "%)";
        },
      },
    },
  },
});

const required = [
  value => {
    if (value) return true;

    return "This field is required.";
  },
];

const checkFormComplete = async () => {
  if (
    formData.value.graph_name !== null &&
    formData.value.graph_name !== "" &&
    formData.value.month !== null &&
    formData.value.month !== "" &&
    formData.value.expense !== "" &&
    formData.value.expense !== null
  ) {
    formComplete.value = true;
  } else {
    formComplete.value = false;
  }
};

const submitForm = () => {
  if (props.widget == 1) {
    const updatedOptions = {
      widget1_graph_name: formData.value.graph_name,
      widget1_month: formData.value.month,
      widget1_tag_id: formData.value.tag_id,
      widget1_expense: formData.value.expense,
      widget1_exlude: formData.value.exclude,
    };
    editOptions(updatedOptions);
  } else if (props.widget == 2) {
    const updatedOptions = {
      widget2_graph_name: formData.value.graph_name,
      widget2_month: formData.value.month,
      widget2_tag_id: formData.value.tag_id,
      widget2_expense: formData.value.expense,
      widget2_exlude: formData.value.exclude,
    };
    editOptions(updatedOptions);
  } else if (props.widget == 3) {
    const updatedOptions = {
      widget3_graph_name: formData.value.graph_name,
      widget3_month: formData.value.month,
      widget3_tag_id: formData.value.tag_id,
      widget3_expense: formData.value.expense,
      widget3_exlude: formData.value.exclude,
    };
    editOptions(updatedOptions);
  }
  formComplete.value = false;
};
</script>
