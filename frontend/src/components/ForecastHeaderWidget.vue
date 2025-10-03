<template>
  <div>
    <v-card
      variant="outlined"
      :elevation="4"
      class="bg-primary"
      v-if="!accounts_isLoading && accounts && accounts.length > 0"
    >
      <v-card-title v-if="smAndDown">
        <span class="text-subtitle-2 text-white">&nbsp;</span>
      </v-card-title>
      <v-card-text>
        <v-row desnity="compact" v-if="!smAndDown">
          <v-col col="2">
            <v-slide-group
              v-model="account_selected"
              class="pa-4"
              selected-class="bg-accent"
              show-arrows
              center-active
            >
              <v-slide-group-item
                v-for="account in accounts"
                :key="account.id"
                v-slot="{ toggle, selectedClass }"
                :value="account.id"
                @group:selected="clickAccountUpdate"
              >
                <v-card
                  color="secondary"
                  :class="['ma-4', selectedClass]"
                  height="75"
                  width="350"
                  @click="toggle"
                >
                  <template v-slot:prepend>
                    <v-icon :icon="account.account_type.icon"></v-icon>
                  </template>
                  <template v-slot:title>
                    <span class="text-subtitle-1 font-weight-bold">
                      {{ account.account_name }}
                    </span>
                  </template>
                  <template v-slot:subtitle>
                    <span>{{ account.bank.bank_name }}</span>
                  </template>
                </v-card>
              </v-slide-group-item>
            </v-slide-group>
          </v-col>
        </v-row>
        <v-row desnity="compact" v-else>
          <v-select
            :items="accounts"
            variant="outlined"
            :loading="accounts_isLoading"
            item-title="account_name"
            item-value="id"
            v-model="account_selected"
            density="compact"
            @update:model-value="clickAccountUpdate"
            bg-color="secondary"
            menu
            color="primary"
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
          </v-select>
        </v-row>
      </v-card-text>
    </v-card>
    <v-skeleton-loader
      type="card"
      v-if="accounts_isLoading"
    ></v-skeleton-loader>
    <v-card
      variant="outlined"
      :elevation="4"
      class="bg-primary"
      v-if="accounts && accounts.length === 0"
      title="No Accounts"
    ></v-card>
  </div>
</template>
<script setup>
  import { useAccounts } from "@/composables/accountsComposable";
  import { ref, defineEmits } from "vue";
  import { useDisplay } from "vuetify";

  const emit = defineEmits(["updateAccount"]);
  const account_selected = ref(null);
  const { accounts, isLoading: accounts_isLoading } = useAccounts();
  const { smAndDown } = useDisplay();

  const clickAccountUpdate = () => {
    emit("updateAccount", account_selected.value);
  };
</script>
