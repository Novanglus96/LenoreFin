<template>
  <v-container>
    <v-row class="pa-1" no-gutters>
      <v-col>
        <v-card variant="outlined" class="bg-surface">
          <v-card-title class="d-flex align-center">
            Payees
            <v-spacer></v-spacer>
            <v-dialog v-model="addDialog" persistent width="400">
              <template v-slot:activator="{ props }">
                <v-btn
                  color="primary"
                  prepend-icon="mdi-plus"
                  v-bind="props"
                  v-if="authStore.isFullAccess"
                >
                  Add Payee
                </v-btn>
              </template>
              <form @submit.prevent="submitAdd">
                <v-card>
                  <v-card-title>Add Payee</v-card-title>
                  <v-card-text>
                    <v-text-field
                      label="Payee Name*"
                      variant="outlined"
                      v-model="add_payee_name.value.value"
                      :error-messages="add_payee_name.errorMessage.value"
                    ></v-text-field>
                  </v-card-text>
                  <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn variant="text" @click="closeAddDialog">Cancel</v-btn>
                    <v-btn color="primary" variant="text" type="submit">Save</v-btn>
                  </v-card-actions>
                </v-card>
              </form>
            </v-dialog>
          </v-card-title>
          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="payees ?? []"
              :loading="isLoading"
              item-value="id"
              density="compact"
              :search="search"
            >
              <template v-slot:top>
                <v-text-field
                  v-model="search"
                  label="Search"
                  prepend-inner-icon="mdi-magnify"
                  variant="outlined"
                  density="compact"
                  class="mb-2"
                  hide-details
                ></v-text-field>
              </template>
              <template v-slot:item.actions="{ item }" v-if="authStore.isFullAccess">
                <v-btn
                  icon="mdi-pencil"
                  variant="text"
                  size="small"
                  @click="openEditDialog(item)"
                ></v-btn>
                <v-btn
                  icon="mdi-delete"
                  variant="text"
                  size="small"
                  color="error"
                  @click="openDeleteDialog(item)"
                ></v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Edit dialog -->
    <v-dialog v-model="editDialog" persistent width="400">
      <form @submit.prevent="submitEdit">
        <v-card>
          <v-card-title>Edit Payee</v-card-title>
          <v-card-text>
            <v-text-field
              label="Payee Name*"
              variant="outlined"
              v-model="edit_payee_name.value.value"
              :error-messages="edit_payee_name.errorMessage.value"
            ></v-text-field>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn variant="text" @click="closeEditDialog">Cancel</v-btn>
            <v-btn color="primary" variant="text" type="submit">Save</v-btn>
          </v-card-actions>
        </v-card>
      </form>
    </v-dialog>

    <!-- Delete confirm dialog -->
    <v-dialog v-model="deleteDialog" persistent width="400">
      <v-card>
        <v-card-title>Delete Payee</v-card-title>
        <v-card-text>
          Are you sure you want to delete
          <strong>{{ selectedPayee?.payee_name }}</strong>?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="deleteDialog = false">Cancel</v-btn>
          <v-btn color="error" variant="text" @click="confirmDelete">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>
<script setup>
  import { ref } from "vue";
  import { usePayees } from "@/composables/payeesComposable";
  import { useField, useForm } from "vee-validate";
  import * as yup from "yup";
  import { useAuthStore } from "@/stores/auth";

  const authStore = useAuthStore();
  const { payees, isLoading, addPayee, editPayee, removePayee } = usePayees();

  const search = ref("");
  const addDialog = ref(false);
  const editDialog = ref(false);
  const deleteDialog = ref(false);
  const selectedPayee = ref(null);

  const headers = [
    { title: "Payee Name", key: "payee_name", sortable: true },
    { title: "Actions", key: "actions", sortable: false, align: "end" },
  ];

  // Add form
  const addSchema = yup.object({
    payee_name: yup.string().required("Payee name is required."),
  });
  const { handleSubmit: handleAdd, resetForm: resetAdd } = useForm({
    validationSchema: addSchema,
  });
  const add_payee_name = useField("payee_name");

  const submitAdd = handleAdd(values => {
    addPayee(values);
    closeAddDialog();
  });

  const closeAddDialog = () => {
    resetAdd();
    addDialog.value = false;
  };

  // Edit form
  const editSchema = yup.object({
    edit_payee_name: yup.string().required("Payee name is required."),
  });
  const { handleSubmit: handleEdit, resetForm: resetEdit } = useForm({
    validationSchema: editSchema,
  });
  const edit_payee_name = useField("edit_payee_name");

  const openEditDialog = payee => {
    selectedPayee.value = payee;
    edit_payee_name.value.value = payee.payee_name;
    editDialog.value = true;
  };

  const submitEdit = handleEdit(values => {
    editPayee({ id: selectedPayee.value.id, payee_name: values.edit_payee_name });
    closeEditDialog();
  });

  const closeEditDialog = () => {
    resetEdit();
    selectedPayee.value = null;
    editDialog.value = false;
  };

  // Delete
  const openDeleteDialog = payee => {
    selectedPayee.value = payee;
    deleteDialog.value = true;
  };

  const confirmDelete = () => {
    removePayee(selectedPayee.value.id);
    selectedPayee.value = null;
    deleteDialog.value = false;
  };
</script>
