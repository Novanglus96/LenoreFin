<template>
  <form @submit.prevent="submit">
    <v-card variant="outlined" :elevation="4" class="bg-white ma-0 pa-0 ga-0">
      <template v-slot:title
        ><div
          class="d-flex align-center justify-space-between"
          v-if="props.edit"
        >
          <span class="text-secondary text-h6" v-if="!canEdit">{{
            props.budget ? props.budget.name : ""
          }}</span>
          <v-spacer></v-spacer>
          <v-btn
            color="error"
            prepend-icon="mdi-delete"
            :disabled="canEdit || !props.budget"
            @click="showConfirmDelete = true"
            size="small"
            variant="text"
            >delete</v-btn
          >
          <v-dialog v-model="showConfirmDelete" width="auto"
            ><v-card
              variant="outlined"
              :elevation="4"
              class="bg-white ma-0 pa-0 ga-0"
              width="400"
              ><v-card-title>Delete this Budget?</v-card-title>
              <v-card-text
                >Are you sure you want to delete this budget (<span
                  class="text-accent"
                  >{{ props.budget.name }}</span
                >)?</v-card-text
              ><v-card-actions
                ><v-btn color="secondary" @click="showConfirmDelete = false"
                  >Cancel</v-btn
                ><v-btn color="secondary" @click="deleteClicked"
                  >Delete</v-btn
                ></v-card-actions
              ></v-card
            ></v-dialog
          >
          <v-btn
            color="secondary"
            prepend-icon="mdi-pencil"
            :disabled="canEdit || !props.budget"
            @click="canEdit = true"
            size="small"
            variant="text"
            >edit</v-btn
          >
        </div></template
      >
      <template v-slot:text>
        <v-expand-transition>
          <v-container v-if="!props.edit || canEdit"
            ><v-row dense
              ><v-col cols="8"
                ><v-text-field
                  clearable
                  label="Name"
                  variant="outlined"
                  v-model="name.value.value"
                  :error-messages="name.errorMessage.value"
                  :counter="254"
                  density="compact"
                  :disabled="!canEdit"
                ></v-text-field></v-col></v-row
            ><v-row dense
              ><v-col
                ><v-checkbox
                  label="Active"
                  v-model="active.value.value"
                  density="compact"
                  :disabled="!canEdit"
                ></v-checkbox></v-col
              ><v-col
                ><v-checkbox
                  label="Dashboard"
                  v-model="widget.value.value"
                  density="compact"
                  :disabled="!canEdit"
                ></v-checkbox></v-col
            ></v-row>
            <v-row dense
              ><v-col
                ><v-text-field
                  v-model="amount.value.value"
                  variant="outlined"
                  label="Amount"
                  prefix="$"
                  type="number"
                  step="1.00"
                  density="compact"
                  :disabled="!canEdit"
                  :error-messages="amount.errorMessage.value"
                ></v-text-field></v-col></v-row
            ><v-row dense
              ><v-col
                ><v-autocomplete
                  clearable
                  chips
                  multiple
                  label="Tag(s)"
                  :items="tag_items"
                  variant="outlined"
                  :loading="tags_isLoading"
                  item-title="tag_name"
                  item-value="id"
                  v-model="tag_ids.value.value"
                  density="compact"
                  :error-messages="tag_ids.errorMessage.value"
                  :disabled="!canEdit"
                >
                  <template v-slot:item="{ props, item }">
                    <v-list-item
                      v-bind="props"
                      :title="
                        item.raw.parent
                          ? item.raw.parent.tag_name
                          : item.raw.tag_name
                      "
                      :subtitle="item.raw.parent ? item.raw.tag_name : null"
                    >
                      <template v-slot:prepend>
                        <v-icon
                          icon="mdi-tag"
                          :color="tagColor(item.raw.tag_type.id)"
                        ></v-icon>
                      </template>
                    </v-list-item>
                  </template> </v-autocomplete></v-col
            ></v-row>
            <v-row dense
              ><v-col cols="8"
                ><v-autocomplete
                  clearable
                  label="Repeat"
                  :items="repeats"
                  variant="outlined"
                  :loading="repeats_isLoading"
                  item-title="repeat_name"
                  v-model="repeat.value.value"
                  density="compact"
                  :error-messages="repeat.errorMessage.value"
                  return-object
                  :disabled="!canEdit"
                  @update:model-value="updateNextDate"
                ></v-autocomplete></v-col
              ><v-col cols="4"
                ><v-checkbox
                  label="Roll Over"
                  v-model="roll_over.value.value"
                  density="compact"
                  :disabled="!canEdit"
                ></v-checkbox></v-col
            ></v-row>
            <v-row dense
              ><v-col
                ><v-date-input
                  label="Start Date"
                  prepend-icon=""
                  prepend-inner-icon="$calendar"
                  variant="outlined"
                  :error-messages="start_date.errorMessage.value"
                  v-model="start_date.value.value"
                  density="compact"
                  :disabled="!canEdit"
                  clearable
                  @click:clear="start_date.value.value = null"
                  @update:model-value="updateNextDate"
                ></v-date-input></v-col></v-row
            ><v-row dense>
              <v-col
                ><v-date-input
                  label="Next Date"
                  prepend-icon=""
                  prepend-inner-icon="$calendar"
                  variant="outlined"
                  :error-messages="next_date.errorMessage.value"
                  v-model="next_date.value.value"
                  density="compact"
                  :disabled="true"
                ></v-date-input></v-col></v-row></v-container></v-expand-transition
      ></template>
      <v-card-actions v-if="!props.edit || canEdit"
        ><v-spacer></v-spacer
        ><v-btn color="secondary" :disabled="!canEdit" @click="resetForm">{{
          props.edit ? "Cancel" : "Close"
        }}</v-btn
        ><v-btn color="secondary" type="submit" :disabled="!canEdit">{{
          props.edit ? "Save Changes" : "Add Budget"
        }}</v-btn></v-card-actions
      >
    </v-card>
  </form>
</template>
<script setup>
import { defineProps, watchEffect, onMounted, ref, defineEmits } from "vue";
import { useField, useForm } from "vee-validate";
import { useTags } from "@/composables/tagsComposable";
import { useRepeats } from "@/composables/repeatsComposable";
import { useBudgets } from "@/composables/budgetsComposable";

const emit = defineEmits(["updateDialog"]);
const { tags: tag_items, isLoading: tags_isLoading } = useTags();
const { repeats, isLoading: repeats_isLoading } = useRepeats();
const { addBudget, removeBudget, editBudget } = useBudgets();
const props = defineProps({
  budget: Object,
  edit: Boolean,
});
const canEdit = ref(props.edit ? false : true);
const showConfirmDelete = ref(false);
const { handleSubmit } = useForm({
  validationSchema: {
    name(value) {
      if (value?.length >= 2 && value?.length <= 254) return true;

      return "Name needs to be at least 2 characters, and less than 254.";
    },
    start_date(value) {
      if (value) {
        return true;
      }

      return "Must provide a date.";
    },
    next_date(value) {
      if (value) return true;

      return "Must provide a date.";
    },
    amount(value) {
      if (value > 0) return true;

      return "Must provide a postive amount.";
    },
    tag_ids(value) {
      if (value && value.length > 0) return true;

      return "Must select at least 1 tag.";
    },
    repeat(value) {
      if (value) return true;

      return "Must select a repeat";
    },
  },
});

const id = useField("id");
const start_date = useField("start_date");
const next_date = useField("next_date");
const name = useField("name");
const widget = useField("widget");
const active = useField("active");
const amount = useField("amount");
const tag_ids = useField("tag_ids");
const roll_over = useField("roll_over");
const repeat = useField("repeat");

const watchPassedFormData = () => {
  watchEffect(() => {
    if (props.budget) {
      id.value.value = props.budget.id;
      start_date.value.value = parseDateAsLocal(props.budget.start_day);
      next_date.value.value = parseDateAsLocal(props.budget.next_start);
      name.value.value = props.budget.name;
      active.value.value = props.budget.active;
      widget.value.value = props.budget.widget;
      amount.value.value = props.budget.amount;
      tag_ids.value.value = props.budget.tag_ids
        ? JSON.parse(props.budget.tag_ids)
        : [];
      roll_over.value.value = props.budget.roll_over;
      repeat.value.value = props.budget.repeat;
    }
  });
};
const resetForm = () => {
  if (props.edit) {
    id.value.value = props.budget.id;
    start_date.value.value = parseDateAsLocal(props.budget.start_day);
    next_date.value.value = parseDateAsLocal(props.budget.next_start);
    name.value.value = props.budget.name;
    active.value.value = props.budget.active;
    widget.value.value = props.budget.widget;
    amount.value.value = props.budget.amount;
    tag_ids.value.value = props.budget.tag_ids
      ? JSON.parse(props.budget.tag_ids)
      : [];
    roll_over.value.value = props.budget.roll_over;
    repeat.value.value = props.budget.repeat;
    canEdit.value = false;
  } else {
    emit("updateDialog", false);
  }
};
const updateNextDate = () => {
  if (!start_date.value.value || !repeat.value.value) {
    next_date.value.value = null;
  }
  if (start_date.value.value && repeat.value.value) {
    let newDate = addToDate(start_date.value.value, {
      days: repeat.value.value.days,
      weeks: repeat.value.value.weeks,
      months: repeat.value.value.months,
      years: repeat.value.value.years,
    });
    next_date.value.value = newDate;
  }
};
const tagColor = typeID => {
  if (typeID == 1) {
    return "red";
  } else if (typeID == 2) {
    return "green";
  } else if (typeID == 3) {
    return "grey";
  }
};

const deleteClicked = () => {
  removeBudget(props.budget);
  emit("updateDialog", false);
  showConfirmDelete.value = false;
};

const submit = handleSubmit(values => {
  if (props.edit) {
    editBudget(values);
  } else {
    addBudget(values);
  }
  emit("updateDialog", false);
  canEdit.value = false;
});
onMounted(() => {
  watchPassedFormData();
});

function parseDateAsLocal(dateString) {
  if (!dateString) {
    console.error("parseDateAsLocal: Received null or undefined dateString");
    return null; // Or handle appropriately
  }
  const [year, month, day] = dateString.split("-").map(Number);
  return new Date(year, month - 1, day); // No timezone adjustment
}

function addToDate(date, { days = 0, weeks = 0, months = 0, years = 0 }) {
  const newDate = new Date(date);

  // Add days
  newDate.setDate(newDate.getDate() + days + weeks * 7);

  // Add months
  newDate.setMonth(newDate.getMonth() + months);

  // Add years
  newDate.setFullYear(newDate.getFullYear() + years);

  return newDate;
}
</script>
