<template>
  <v-sheet border rounded :height="300" color="white">
    <v-container class="pa-0 ma-1">
      <v-row dense>
        <v-col cols="1">
          <v-tooltip text="Delete Tag(s)" location="top">
            <template v-slot:activator="{ props }">
              <v-btn
                icon="mdi-tag-minus"
                flat
                variant="plain"
                color="error"
                @click="clickTagRemove"
                v-bind="props"
                :disabled="selected && selected.length === 0"
              ></v-btn>
            </template>
          </v-tooltip>
        </v-col>
        <v-col>
          <v-autocomplete
            clearable
            label="Tag"
            :items="tags"
            variant="outlined"
            :loading="tags_isLoading"
            item-title="tag_name"
            v-model="tagToAdd"
            @update:model-value="checkTagComplete"
            density="compact"
            return-object
          >
            <template v-slot:item="{ props, item }">
              <v-list-item
                v-bind="props"
                :title="
                  item.raw.parent ? item.raw.parent.tag_name : item.raw.tag_name
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
            </template>
          </v-autocomplete>
        </v-col>
        <v-col cols="3">
          <v-text-field
            v-model="tagAmount"
            variant="outlined"
            label="Amount"
            prefix="$"
            @update:model-value="checkTagComplete"
            type="number"
            density="compact"
            :max="local_amount"
            :disabled="local_full_toggle"
          ></v-text-field>
        </v-col>
        <v-col cols="1">
          <v-tooltip text="Full Amount" location="top">
            <template v-slot:activator="{ props }"
              ><v-checkbox
                v-bind="props"
                v-model="local_full_toggle"
              ></v-checkbox></template></v-tooltip
        ></v-col>
        <v-col cols="1">
          <v-tooltip text="Add New Tag" location="top">
            <template v-slot:activator="{ props }">
              <v-btn
                icon="mdi-tag-plus"
                flat
                variant="plain"
                color="success"
                @click="clickTagAdd"
                v-bind="props"
                :disabled="!tagComplete"
              ></v-btn>
            </template>
          </v-tooltip>
        </v-col>
      </v-row>
      <v-row dense>
        <v-col
          ><span
            class="text-error text-subtitle-2 font-italic"
            v-if="!verifyTagTotal()"
            >* Tags must equal total</span
          ></v-col
        >
      </v-row>
    </v-container>
    <vue3-datatable
      :rows="local_tags"
      :columns="columns"
      :totalRows="local_tags ? local_tags.length : 0"
      :isServerMode="false"
      pageSize="4"
      :hasCheckbox="true"
      :stickyHeader="true"
      noDataContent="No Tags"
      search=""
      @rowSelect="rowSelected"
      ref="tag_table"
      height="210px"
      skin="bh-table-striped bh-table-compact"
      :pageSizeOptions="[4]"
      :showPageSize="false"
      paginationInfo="{0} to {1} of {2}"
      class="alt-pagination"
    >
      <template #tag_pretty_name="row">
        <v-icon icon="mdi-tag"></v-icon>
        <span class="font-weight-bold text-black">{{
          row.value.tag_pretty_name
        }}</span>
      </template>
      <template #tag_amt="row">
        <span
          class="font-weight-bold text-black"
          v-if="!row.value.tag_full_toggle"
          >${{ row.value.tag_amt }}</span
        >
        <span class="font-weight-bold text-black font-italic" v-else
          >(Full)</span
        >
      </template>
    </vue3-datatable>
  </v-sheet>
</template>
<script setup>
import { ref, defineEmits, defineProps, onMounted, watchEffect } from "vue";
import { useTags } from "@/composables/tagsComposable";
import Vue3Datatable from "@bhplugin/vue3-datatable";
import "@bhplugin/vue3-datatable/dist/style.css";

// Define props...
const props = defineProps({
  tags: {
    type: Array,
  },
  totalAmount: {
    type: Number,
  },
  noItems: {
    type: Number,
  },
  transID: {
    type: Number,
    default: 0,
  },
});

// Define emits
const emit = defineEmits(["tagTableUpdated"]);

// Define reactive variables...
const tagToAdd = ref(null); // Tag object to add to tag list
const tagAmount = ref(null); // Tag amount to add to tag list
const tagComplete = ref(false); // True when tag/amount are filled out, enables add button
const selected = ref([]); // The objects of the rows selected in table
const tag_table = ref(null); // The reference to the table
const local_tags = ref([]); // Mutable tags array
const local_amount = ref(null); // Mutable amount
const local_full_toggle = ref(true);

// Define table columns...
const columns = ref([
  { field: "tag_id", title: "ID", isUnique: true, hide: true },
  { field: "tag_pretty_name", title: "Tag" },
  { field: "tag_amt", title: "Amount", type: "number", width: "100px" },
  {
    field: "tag_full_toggle",
    title: "Full Amount",
    type: "boolean",
    hide: true,
  },
]);

// API calls and data retrieval...
const { tags, isLoading: tags_isLoading } = useTags();

// Define functions...

/**
 * `watchpassedProps` Watches for changes to props and updates
 * local variables as appropiate.
 */
const watchPassedProps = () => {
  watchEffect(() => {
    if (props.tags) {
      local_tags.value = props.tags;
    }
    if (props.totalAmount) {
      local_amount.value = props.totalAmount;
      checkTagComplete();
    }
  });
};

/**
 * `verifyTagTotal` Verifies the total of tags equals total amount.
 * @returns - Returns True if totals match
 */
const verifyTagTotal = () => {
  return true;
};

/**
 * `checkTagComplete` Checks if tag and amount are selected to add to table.
 */
const checkTagComplete = () => {
  if (
    tagAmount.value !== null &&
    tagAmount.value !== "" &&
    Math.abs(parseFloat(tagAmount.value)) <= parseFloat(local_amount.value) &&
    tagToAdd.value !== null &&
    tagToAdd.value !== "" &&
    !local_tags.value.some(tag => tag.tag_id === tagToAdd.value.id)
  ) {
    tagComplete.value = true;
  } else {
    tagComplete.value = false;
  }
};

/**
 * `clickTagAdd` Adds a tag to the tag table.
 */
const clickTagAdd = () => {
  let tag_row = {
    tag_id: tagToAdd.value.id,
    tag_amt: parseFloat(Math.abs(tagAmount.value)).toFixed(2),
    tag_pretty_name: tagToAdd.value.tag_name,
    tag_full_toggle: local_full_toggle.value,
  };
  local_tags.value.push(tag_row);
  tag_table.value.reset();
  tagComplete.value = false;
  emit("tagTableUpdated", { transID: props.transID, tags: local_tags.value });
};

/**
 * `clickTagRemove` Removes a tag from the tag table.
 */
const clickTagRemove = () => {
  if (selected.value) {
    for (const tag of selected.value) {
      local_tags.value = local_tags.value.filter(item => item.tag_id !== tag);
    }
  }
  emit("tagTableUpdated", { transID: props.transID, tags: local_tags.value });
};

// Define functions...
/**
 * `rowSelected` Populates selected variable with selected rows in table.
 */
const rowSelected = () => {
  selected.value = [];
  let selectedrows = tag_table.value.getSelectedRows();
  for (const selectedrow of selectedrows) {
    selected.value.push(selectedrow.tag_id);
  }
};

/**
 * `tagColor` Sets the tag color based on tag type.
 * @param {int} typeID - The tag type ID.
 * @return {color} - The color of the tag.
 */
const tagColor = typeID => {
  if (typeID == 1) {
    return "red";
  } else if (typeID == 2) {
    return "green";
  } else if (typeID == 3) {
    return "grey";
  }
};

// Lifecycle hook...

onMounted(() => {
  // Perform actions on mount
  watchPassedProps();
});
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
