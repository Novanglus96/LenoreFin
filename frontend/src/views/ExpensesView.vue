<template>
  <v-container>
    <v-row class="pa-1 ga-1" no-gutters v-if="!isLoading">
      <v-col class="rounded text-center">
        <v-btn
          icon="mdi-cog"
          flat
          size="xs"
          :disabled="isActive"
          @click="showOptions = true"
        ></v-btn>
        <v-dialog width="300" v-model="showOptions">
          <v-card>
            <form @submit.prevent="submit">
              <v-card-title
                ><span class="text-secondary text-h6"
                  >Choose Expenses</span
                ></v-card-title
              >
              <v-card-text>
                <v-autocomplete
                  clearable
                  chips
                  multiple
                  label="Main Report Tags"
                  :items="parent_tags"
                  variant="outlined"
                  :loading="parent_tags_isLoading"
                  item-title="tag_name"
                  item-value="id"
                  v-model="main_report_tags.value.value"
                  density="compact"
                  :error-messages="main_report_tags.errorMessage.value"
                ></v-autocomplete
                ><v-autocomplete
                  clearable
                  chips
                  multiple
                  label="Individual Report Tags"
                  :items="parent_tags"
                  variant="outlined"
                  :loading="parent_tags_isLoading"
                  item-title="tag_name"
                  item-value="id"
                  v-model="individual_report_tags.value.value"
                  density="compact"
                  :error-messages="individual_report_tags.errorMessage.value"
                ></v-autocomplete
              ></v-card-text>
              <v-card-actions
                ><v-spacer></v-spacer
                ><v-btn color="secondary" type="submit"
                  >Save Changes</v-btn
                ></v-card-actions
              >
            </form>
          </v-card>
        </v-dialog>
        <v-tabs v-model="main_tab" color="accent">
          <v-tab
            v-for="(main, index) in expenses"
            :key="index"
            :value="main.title"
            >{{ main.title }}</v-tab
          >
        </v-tabs>
        <v-window v-model="main_tab">
          <v-window-item
            v-for="(main_window, main_index) in expenses"
            :key="main_index"
            :value="main_window.title"
          >
            <v-tabs v-model="tab[main_index]" color="accent">
              <v-tab
                v-for="(sub_window, sub_index) in main_window.data"
                :key="sub_index"
                :value="sub_window.key_name"
                >{{ sub_window.pretty_name }}</v-tab
              >
            </v-tabs>
            <v-window v-model="tab[main_index]">
              <v-window-item
                v-for="(sub_window, sub_index) in main_window.data"
                :key="sub_index"
                :value="sub_window.key_name"
              >
                <ReportGraphWidget
                  :data="sub_window"
                  :graphName="sub_window.pretty_name"
                  :key="sub_index"
                  :isLoading="isLoading"
                  v-if="!isMobile" />
                <ReportGraphWidgetMobile
                  :data="sub_window"
                  :graphName="sub_window.pretty_name"
                  :key="sub_index"
                  :isLoading="isLoading"
                  v-if="isMobile"
              /></v-window-item>
              <ReportTableWidget
                :isLoading="isLoading"
                :data="main_window.data"
            /></v-window>
          </v-window-item>
        </v-window> </v-col
    ></v-row>
    <div v-else>
      <v-row
        ><v-col cols="3"></v-col
        ><v-col
          class="text-subtitle-2 text-uppercase text-center font-italic text-accent"
        >
          Loading Data...</v-col
        ><v-col cols="3"></v-col
      ></v-row>
      <v-row
        ><v-col cols="3"></v-col
        ><v-col>
          <v-progress-linear
            color="accent"
            height="6"
            indeterminate
            rounded
          ></v-progress-linear> </v-col
        ><v-col cols="3"></v-col
      ></v-row>
    </div>
  </v-container>
</template>
<script setup>
import { ref, watch } from "vue";
import ReportGraphWidget from "@/components/ReportGraphWidget.vue";
import ReportGraphWidgetMobile from "@/components/ReportGraphWidgetMobile.vue";
import ReportTableWidget from "@/components/ReportTableWidget.vue";
import { useExpenseGraph } from "@/composables/planningGraphComposable";
import { useField, useForm } from "vee-validate";
import { useOptions } from "@/composables/optionsComposable";
import { useParentTags } from "@/composables/tagsComposable";
import { useDisplay } from "vuetify";

const { smAndDown } = useDisplay();
const isMobile = smAndDown;

const { options: appOptions, editOptions } = useOptions();
const { expense_graph: expenses, isLoading } = useExpenseGraph();
const { parent_tags, isLoading: parent_tags_isLoading } = useParentTags(1);

const { handleSubmit } = useForm({
  validationSchema: {
    main_report_tags(value) {
      if (value && value.length > 0) return true;

      return "Must select at least 1 tag.";
    },
  },
});

const main_report_tags = useField("main_report_tags");
const individual_report_tags = useField("individual_report_tags");
watch(
  appOptions,
  newOptions => {
    if (newOptions) {
      individual_report_tags.value.value = JSON.parse(
        newOptions.report_individual,
      );
      main_report_tags.value.value = JSON.parse(newOptions.report_main);
    }
  },
  { immediate: true },
);

const main_tab = ref(0);
const showOptions = ref(false);

const tab = ref(Array(expenses.length).fill(0));

const submit = handleSubmit(values => {
  let data = {
    report_main: JSON.stringify(values.main_report_tags),
    report_individual: JSON.stringify(values.individual_report_tags),
  };
  editOptions(data);
  showOptions.value = false;
});
</script>
