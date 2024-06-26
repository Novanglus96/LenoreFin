<template>
  <v-sheet
    border
    rounded
    :height="200 + props.noItems * 40"
    :color="verifyTagTotal() ? 'white' : 'red-lighten-5'"
  >
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
                @click="clickTagRemove()"
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
        <v-col cols="4">
          <v-text-field
            v-model="tagAmount"
            variant="outlined"
            label="Amount"
            prefix="$"
            @update:model-value="checkTagComplete"
            type="number"
            step="1.00"
            density="compact"
          ></v-text-field>
        </v-col>
        <v-col cols="1">
          <v-tooltip text="Add New Tag" location="top">
            <template v-slot:activator="{ props }">
              <v-btn
                icon="mdi-tag-plus"
                flat
                variant="plain"
                color="success"
                @click="clickTagAdd()"
                v-bind="props"
                :disabled="!tagComplete && !verifyTagTotal()"
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
      :pageSize="props.noItems"
      :hasCheckbox="true"
      :stickyHeader="true"
      noDataContent="No Tags"
      search=""
      @rowSelect="rowSelected()"
      ref="tag_table"
      :height="35 + props.noItems * 40 + 'px'"
      skin="bh-table-striped bh-table-compact"
      :pageSizeOptions="[props.noItems]"
      :showPageSize="false"
      paginationInfo="{0} to {1} of {2}"
      class="alt-pagination"
    >
      <template #tag_name="row">
        <v-icon icon="mdi-tag"></v-icon>
        <span class="font-weight-bold text-black">{{
          row.value.tag_name
        }}</span>
      </template>
      <template #tag_amount="row">
        <span class="font-weight-bold text-black"
          >${{ row.value.tag_amount }}</span
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

// Define table columns...
const columns = ref([
  { field: "tag_id", title: "ID", isUnique: true, hide: true },
  { field: "tag_name", title: "Tag" },
  { field: "tag_amount", title: "Amount", type: "number", width: "100px" },
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
    }
  });
};

/**
 * `verifyTagTotal` Verifies the total of tags equals total amount.
 * @returns - Returns True if totals match
 */
const verifyTagTotal = () => {
  let tagtotal = 0;
  if (local_tags.value) {
    local_tags.value.forEach(tag => {
      tagtotal += parseFloat(tag.tag_amount);
    });
  }
  if (tagtotal == local_amount.value) {
    return true;
  } else {
    return false;
  }
};

/**
 * `checkTagComplete` Checks if tag and amount are selected to add to table.
 */
const checkTagComplete = () => {
  if (
    tagAmount.value !== null &&
    tagAmount.value !== "" &&
    tagToAdd.value !== null &&
    tagToAdd.value !== ""
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
  let pretty_name = "";
  if (tagToAdd.value.parent) {
    pretty_name =
      tagToAdd.value.parent.tag_name + " : " + tagToAdd.value.tag_name;
  } else {
    pretty_name = tagToAdd.value.tag_name;
  }
  let tag_row = {
    tag_id: tagToAdd.value.id,
    tag_amount: parseFloat(Math.abs(tagAmount.value)).toFixed(2),
    tag_name: pretty_name,
  };
  local_tags.value.push(tag_row);
  tag_table.value.reset();
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
