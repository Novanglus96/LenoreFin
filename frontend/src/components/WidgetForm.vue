<template>
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
      ></v-btn>
    </template>
    <v-form v-model="formValid" ref="form">
      <v-card :width="isMobile ? '400' : '350'">
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
              <v-col>
                <v-radio-group
                  title="Graph Type"
                  v-model="formData.graph_type"
                  @update:model-value="checkFormComplete"
                >
                  <v-radio label="All Expenses" :value="1"></v-radio>
                  <v-radio label="All Income" :value="2"></v-radio>
                  <v-radio label="Untagged" :value="3"></v-radio>
                  <v-radio label="Custom" :value="4"></v-radio>
                </v-radio-group>
              </v-col>
            </v-row>
            <v-row dense v-if="formData.graph_type == 4">
              <v-col>
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
                ></v-autocomplete>
              </v-col>
            </v-row>
            <v-row dense v-if="formData.graph_type != 3">
              <v-col>
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
                ></v-autocomplete>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <!--<v-btn @click="resetForm">Reset</v-btn>-->
          <v-btn :disabled="!formComplete" @click="submitForm()" type="submit">
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
  </v-menu>
</template>
