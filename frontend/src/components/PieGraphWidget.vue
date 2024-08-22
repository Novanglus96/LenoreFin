<template>
  <div>
    <v-card
      variant="outlined"
      :elevation="4"
      class="bg-white"
      v-if="!isLoading"
    >
      <template v-slot:append>
        <v-menu
          location="start"
          :close-on-content-click="false"
          v-model="menu"
          @update:model-value="onMenuStateChange"
        >
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
          <v-form v-model="formValid" ref="form">
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
                  <v-row dense>
                    <v-col
                      ><v-radio-group
                        title="Graph Type"
                        v-model="formData.graph_type"
                        @update:model-value="checkFormComplete"
                      >
                        <v-radio label="All Expenses" :value="1"></v-radio>
                        <v-radio label="All Income" :value="2"></v-radio>
                        <v-radio label="Untagged" :value="3"></v-radio>
                        <v-radio
                          label="Custom"
                          :value="4"
                        ></v-radio> </v-radio-group
                    ></v-col>
                  </v-row>
                  <v-row dense v-if="formData.graph_type == 4"
                    ><v-col>
                      <v-autocomplete
                        clearable
                        label="Choose a main tag"
                        :items="parent_tags"
                        item-title="tag_name"
                        item-value="id"
                        variant="outlined"
                        :loading="parent_tags_isLoading"
                        v-model="formData.tag_id"
                        :rules="required"
                        @update:model-value="checkFormComplete"
                        density="compact"
                      ></v-autocomplete> </v-col
                  ></v-row>
                  <v-row dense v-if="formData.graph_type != 3"
                    ><v-col>
                      <v-autocomplete
                        clearable
                        chips
                        multiple
                        label="Excluded tags"
                        :items="tags"
                        item-title="tag_name"
                        item-value="id"
                        variant="outlined"
                        :loading="tags_isLoading"
                        v-model="formData.exclude"
                        @update:model-value="checkFormComplete"
                        density="compact"
                      ></v-autocomplete> </v-col
                  ></v-row>
                </v-container>
              </v-card-text>
              <v-card-actions>
                <v-btn @click="resetForm">Reset</v-btn>
                <v-btn
                  :disabled="!formComplete"
                  @click="submitForm()"
                  type="submit"
                  >Save</v-btn
                ></v-card-actions
              >
            </v-card>
          </v-form>
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
import { ref, defineProps, watch } from "vue";
import { useGraphs } from "@/composables/tagsComposable";
import { useOptions } from "@/composables/optionsComposable";
import { useTags, useParentTags } from "@/composables/tagsComposable";

const { options: appOptions, editOptions } = useOptions();
const { tags, isLoading: tags_isLoading } = useTags();
const { parent_tags, isLoading: parent_tags_isLoading } = useParentTags();
const formData = ref(null);
const formValid = ref(false);
const menu = ref(false);
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
    graph_type: appOptions.widget1_type ? appOptions.widget1_type.id : 1,
    exclude: appOptions.widget1_exclude
      ? JSON.parse(appOptions.widget1_exclude)
      : [],
  };
}
if (props.widget == 2) {
  formData.value = {
    graph_name: appOptions.widget2_graph_name,
    month: appOptions.widget2_month,
    tag_id: appOptions.widget2_tag_id,
    graph_type: appOptions.widget2_type ? appOptions.widget2_type.id : 1,
    exclude: appOptions.widget2_exclude
      ? JSON.parse(appOptions.widget2_exclude)
      : [],
  };
}
if (props.widget == 3) {
  formData.value = {
    graph_name: appOptions.widget3_graph_name,
    month: appOptions.widget3_month,
    tag_id: appOptions.widget3_tag_id,
    graph_type: appOptions.widget3_type ? appOptions.widget2_type.id : 1,
    exclude: appOptions.widget3_exclude
      ? JSON.parse(appOptions.widget3_exclude)
      : [],
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

// Populate formData once appOptions are loaded
watch(
  appOptions,
  newOptions => {
    if (newOptions) {
      if (props.widget == 1) {
        formData.value = {
          graph_name: newOptions.widget1_graph_name,
          month: newOptions.widget1_month,
          tag_id: newOptions.widget1_tag_id,
          graph_type: newOptions.widget1_type ? newOptions.widget1_type.id : 1,
          exclude: newOptions.widget1_exclude
            ? JSON.parse(newOptions.widget1_exclude)
            : [],
        };
      }
      if (props.widget == 2) {
        formData.value = {
          graph_name: newOptions.widget2_graph_name,
          month: newOptions.widget2_month,
          tag_id: newOptions.widget2_tag_id,
          graph_type: newOptions.widget2_type ? newOptions.widget2_type.id : 1,
          exclude: newOptions.widget2_exclude
            ? JSON.parse(newOptions.widget2_exclude)
            : [],
        };
      }
      if (props.widget == 3) {
        formData.value = {
          graph_name: newOptions.widget3_graph_name,
          month: newOptions.widget3_month,
          tag_id: newOptions.widget3_tag_id,
          graph_type: newOptions.widget3_type ? newOptions.widget3_type.id : 1,
          exclude: newOptions.widget3_exclude
            ? JSON.parse(newOptions.widget3_exclude)
            : [],
        };
      }
    }
  },
  { immediate: true },
);

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
      widget1_type_id: formData.value.graph_type,
      widget1_exclude: JSON.stringify(formData.value.exclude),
    };
    editOptions(updatedOptions);
  } else if (props.widget == 2) {
    const updatedOptions = {
      widget2_graph_name: formData.value.graph_name,
      widget2_month: formData.value.month,
      widget2_tag_id: formData.value.tag_id,
      widget2_type_id: formData.value.graph_type,
      widget2_exclude: JSON.stringify(formData.value.exclude),
    };
    editOptions(updatedOptions);
  } else if (props.widget == 3) {
    const updatedOptions = {
      widget3_graph_name: formData.value.graph_name,
      widget3_month: formData.value.month,
      widget3_tag_id: formData.value.tag_id,
      widget3_type_id: formData.value.graph_type,
      widget3_exclude: JSON.stringify(formData.value.exclude),
    };
    editOptions(updatedOptions);
  }
  formComplete.value = false;
  menu.value = false;
};

const onMenuStateChange = isOpen => {
  if (!isOpen) {
    resetForm();
  }
};

const resetForm = () => {};
</script>
