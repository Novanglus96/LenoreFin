<template>
  <v-dialog v-model="dialog" persistent width="300">
    <template v-slot:activator="{ props }">
      <v-btn color="primary" size="small" v-bind="props">Add Payee</v-btn>
    </template>
    <form @submit.prevent="submit">
      <v-card>
        <v-card-title>
          <span class="text-h5">Add Payee</span>
        </v-card-title>
        <v-card-text>
          <v-container>
            <v-row>
              <v-col>
                <v-text-field
                  label="Payee Name*"
                  variant="outlined"
                  v-model="payee_name.value.value"
                  :error-messages="payee_name.errorMessage.value"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-container>
          <span class="text-error text-subtitle-2 font-italic">* required</span>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="text" @click="closeDialog">Close</v-btn>
          <v-btn color="primary" variant="text" type="submit">Save</v-btn>
        </v-card-actions>
      </v-card>
    </form>
  </v-dialog>
</template>
<script setup>
  import { ref } from "vue";
  import { usePayees } from "@/composables/payeesComposable";
  import { useField, useForm } from "vee-validate";
  import * as yup from "yup";

  const { addPayee } = usePayees();
  const dialog = ref(false);

  const schema = yup.object({
    payee_name: yup.string().required("Payee name is required."),
  });

  const { handleSubmit, resetForm } = useForm({ validationSchema: schema });
  const payee_name = useField("payee_name");

  const submit = handleSubmit(values => {
    addPayee(values);
    closeDialog();
  });

  const closeDialog = () => {
    resetForm();
    dialog.value = false;
  };
</script>
