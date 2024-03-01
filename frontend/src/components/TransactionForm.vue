<template>
  <v-dialog v-model="show" persistent width="1024">
    <v-card>
      <v-card-title>
        <span class="text-h5" v-if="props.isEdit == false"
          >Add Transaction</span
        >
        <span class="text-h5" v-else>Edit Transaction</span>
      </v-card-title>
      <v-card-text>
        <v-container>
          <v-row>
            <v-col>
              <VueDatePicker
                v-model="formData.transaction_date"
                timezone="America/New_York"
                model-type="yyyy-MM-dd"
                :enable-time-picker="false"
                auto-apply
                format="yyyy-MM-dd"
              ></VueDatePicker>
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-autocomplete
                clearable
                label="Transaction Type*"
                :items="transaction_types"
                variant="outlined"
                :loading="transaction_types_isLoading"
                item-title="transaction_type"
                item-value="id"
                v-model="formData.transaction_type_id"
                :rules="required"
                @update:model-value="checkFormComplete"
                :disabled="props.isEdit"
              ></v-autocomplete>
            </v-col>
            <v-col>
              <v-autocomplete
                clearable
                label="Transaction Status*"
                :items="transaction_statuses"
                variant="outlined"
                :loading="transaction_statuses_isLoading"
                item-title="transaction_status"
                item-value="id"
                v-model="formData.status_id"
                :rules="required"
                @update:model-value="checkFormComplete"
              ></v-autocomplete>
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-text-field
                v-model="amount"
                variant="outlined"
                label="Amount*"
                :rules="required"
                prefix="$"
                @update:model-value="checkFormComplete"
                type="number"
                step="1.00"
                @update:focused="reformatNumberToMoney"
              ></v-text-field>
            </v-col>
            <v-col>
              <v-text-field
                v-model="formData.description"
                variant="outlined"
                label="Description*"
                :rules="required"
                @update:model-value="checkFormComplete"
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-autocomplete
                clearable
                label="Source Account*"
                :items="accounts"
                variant="outlined"
                :loading="accounts_isLoading"
                item-title="account_name"
                item-value="id"
                v-model="formData.source_account_id"
                :rules="required"
                @update:model-value="checkFormComplete"
              >
                <template v-slot:item="{ props, item }">
                  <v-list-item
                    v-bind="props"
                    :title="item.raw.account_name"
                    :subtitle="item.raw.bank.bank_name"
                  >
                    <template v-slot:prepend>
                      <v-icon :icon="item.raw.account_type.icon"></v-icon>
                    </template>
                  </v-list-item>
                </template>
              </v-autocomplete>
            </v-col>
            <v-col>
              <v-autocomplete
                clearable
                label="Destination Account*"
                :items="accounts"
                variant="outlined"
                :loading="accounts_isLoading"
                item-title="account_name"
                item-value="id"
                v-model="formData.destination_account_id"
                :rules="required"
                @update:model-value="checkFormComplete"
                v-if="formData.transaction_type_id == 3"
              >
                <template v-slot:item="{ props, item }">
                  <v-list-item
                    v-bind="props"
                    :title="item.raw.account_name"
                    :subtitle="item.raw.bank.bank_name"
                  >
                    <template v-slot:prepend>
                      <v-icon :icon="item.raw.account_type.icon"></v-icon>
                    </template>
                  </v-list-item>
                </template>
              </v-autocomplete>
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <!-- TODO: Enable adding tags here -->
              <v-autocomplete
                clearable
                label="Tag*"
                :items="tags"
                variant="outlined"
                :loading="tags_isLoading"
                item-title="tag_name"
                item-value="id"
                v-model="formData.tag_id"
                v-if="!isEdit"
                :rules="required"
                @update:model-value="checkFormComplete"
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
                </template>
              </v-autocomplete>
              <v-sheet
                border
                rounded
                v-if="isEdit && formData.transaction_type_id != 3"
                :height="300"
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
                              item.raw.parent
                                ? item.raw.parent.tag_name
                                : item.raw.tag_name
                            "
                            :subtitle="
                              item.raw.parent ? item.raw.tag_name : null
                            "
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
                        @update:focused="reformatNumberToMoney"
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
                      ><span class="text-error text-subtitle-2 font-italic"
                        >* Tags must equal total</span
                      ></v-col
                    >
                  </v-row>
                </v-container>
                <vue3-datatable
                  :rows="formData.details"
                  :columns="columns"
                  :totalRows="formData.details ? formData.details.length : 0"
                  :isServerMode="false"
                  pageSize="4"
                  :hasCheckbox="true"
                  :stickyHeader="true"
                  noDataContent="No Tags"
                  search=""
                  @rowSelect="rowSelected"
                  ref="details_table"
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
                    <span class="font-weight-bold text-black"
                      >${{ row.value.tag_amt }}</span
                    >
                  </template>
                </vue3-datatable>
              </v-sheet>
            </v-col>
            <v-col>
              <v-textarea
                clearable
                label="Memo"
                variant="outlined"
                v-model="formData.memo"
                :rows="11"
                no-resize
              ></v-textarea>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="accent" variant="text" @click="closeDialog">
          Close
        </v-btn>
        <v-btn
          color="accent"
          variant="text"
          @click="submitForm"
          :disabled="!formComplete"
        >
          Save
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
<script setup>
import { ref, defineEmits, defineProps, onMounted, watchEffect } from "vue";
import { useTransactionTypes } from "@/composables/transactionTypesComposable";
import { useTransactionStatuses } from "@/composables/transactionStatusesComposable";
import { useAccounts } from "@/composables/accountsComposable";
import { useTags } from "@/composables/tagsComposable";
import { useTransactions } from "@/composables/transactionsComposable";
import VueDatePicker from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css";
import Vue3Datatable from "@bhplugin/vue3-datatable";
import "@bhplugin/vue3-datatable/dist/style.css";

const tagToAdd = ref(null);
const tagAmount = ref(null);
const tagComplete = ref(false);
const today = new Date();
const year = today.getFullYear();
const month = String(today.getMonth() + 1).padStart(2, "0");
const day = String(today.getDate()).padStart(2, "0");
const { accounts, isLoading: accounts_isLoading } = useAccounts();
const formattedDate = `${year}-${month}-${day}`;
const formComplete = ref(false);
const { transaction_types, isLoading: transaction_types_isLoading } =
  useTransactionTypes();
const { transaction_statuses, isLoading: transaction_statuses_isLoading } =
  useTransactionStatuses();
const { addTransaction } = useTransactions();
const props = defineProps({
  itemFormDialog: {
    type: Boolean,
    default: false,
  },
  isEdit: {
    type: Boolean,
    default: false,
  },
  passedFormData: Object,
  account_id: {
    type: Number,
    default: 1,
  },
});
const formData = ref({
  id: props.passedFormData ? props.passedFormData.id : 0,
  status_id: props.passedFormData.status.id || 1,
  transaction_type_id: props.passedFormData.transaction_type.id || 1,
  transaction_date: props.passedFormData.transaction_date || formattedDate,
  memo: props.passedFormData.memo || "",
  source_account_id: props.passedFormData.source_account_id || null,
  destination_account_id: props.passedFormData.destination_account_id || null,
  edit_date: formattedDate,
  add_date: props.passedFormData.add_date || formattedDate,
  tag_id: props.passedFormData.tag_id || 1,
  total_amount: props.passedFormData.total_amount || 0,
  description: props.passedFormData.description || null,
  details: [],
});
const { tags, isLoading: tags_isLoading } = useTags();
const amount = ref(
  props.passedFormData.total_amount
    ? parseFloat(Math.abs(props.passedFormData.total_amount)).toFixed(2)
    : null,
);

const columns = ref([
  { field: "tag_id", title: "ID", isUnique: true, hide: true },
  { field: "tag_pretty_name", title: "Tag" },
  { field: "tag_amt", title: "Amount", type: "number", width: "100px" },
]);
const selected = ref([]);

const rowSelected = () => {
  selected.value = [];
  let selectedrows = details_table.value.getSelectedRows();
  for (const selectedrow of selectedrows) {
    selected.value.push(selectedrow.tag_id);
  }
};
const details_table = ref(null);
const show = ref(props.itemFormDialog);
const emit = defineEmits(["updateDialog"]);
const watchPassedFormData = () => {
  watchEffect(() => {
    if (props.passedFormData) {
      formData.value = {
        id: props.passedFormData.id,
        status_id: props.passedFormData.status.id,
        transaction_type_id: props.passedFormData.transaction_type.id,
        transaction_date: props.passedFormData.transaction_date,
        memo: props.passedFormData.memo,
        source_account_id: props.passedFormData.source_account_id,
        destination_account_id: props.passedFormData.destination_account_id,
        edit_date: formattedDate,
        add_date: props.passedFormData.add_date,
        tag_id: props.passedFormData.tag_id,
        total_amount: props.passedFormData.total_amount,
        description: props.passedFormData.description,
        details: fillTagTable(props.passedFormData.details),
      };
      amount.value = props.passedFormData.total_amount
        ? parseFloat(Math.abs(props.passedFormData.total_amount)).toFixed(2)
        : null;
    }
  });
};

const fillTagTable = details => {
  let table = [];
  let pretty_name = "";
  if (details) {
    for (const detail of details) {
      if (detail.tag.parent) {
        pretty_name = detail.tag.parent.tag_name + " : " + detail.tag.tag_name;
      } else {
        pretty_name = detail.tag.tag_name;
      }
      let tag_row = {
        tag_id: detail.tag.id,
        tag_amt: parseFloat(Math.abs(detail.detail_amt)).toFixed(2),
        tag_pretty_name: pretty_name,
      };
      table.push(tag_row);
    }
  }

  return table;
};
const required = [
  value => {
    if (value) return true;

    return "This field is required.";
  },
];

const checkFormComplete = async () => {
  if (
    formData.value.transaction_type_id !== null &&
    formData.value.transaction_type_id !== "" &&
    formData.value.status_id !== null &&
    formData.value.status_id !== "" &&
    formData.value.description !== "" &&
    formData.value.description !== null &&
    amount.value !== "" &&
    amount.value !== null &&
    formData.value.transaction_source_account_id !== "" &&
    formData.value.transaction_source_account_id !== null &&
    formData.value.tag_id !== "" &&
    formData.value.tag_id !== null
  ) {
    if (
      (formData.value.status_id == 3 &&
        formData.value.transaction_destination_account_id !== null) ||
      formData.value.status_id !== 3
    ) {
      formComplete.value = true;
    } else {
      formComplete.value = false;
    }
  } else {
    formComplete.value = false;
  }
};

onMounted(() => {
  watchPassedFormData();
});

const submitForm = async () => {
  if (formData.value.transaction_type_id == 2) {
    formData.value.total_amount = amount.value;
  } else {
    formData.value.total_amount = -amount.value;
  }
  if (props.isEdit == false) {
    await addTransaction(formData.value);
  } else {
    console.log("edit");
  }

  closeDialog();
};

const closeDialog = () => {
  emit("updateDialog", false);
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

const reformatNumberToMoney = () => {
  amount.value = parseFloat(amount.value).toFixed(2);
};

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
    tag_amt: parseFloat(Math.abs(tagAmount.value)).toFixed(2),
    tag_pretty_name: pretty_name,
  };
  formData.value.details.push(tag_row);
  details_table.value.reset();
};

const clickTagRemove = () => {
  if (selected.value) {
    for (const tag of selected.value) {
      formData.value.details = formData.value.details.filter(
        item => item.tag_id !== tag,
      );
    }
  }
};
</script>
