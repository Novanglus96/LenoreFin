<template>
  <v-menu
    location="start"
    :close-on-content-click="false"
    v-model="menu"
    @update:model-value="onMenuStateChange"
  >
    <template v-slot:activator="{ props: menuProps }">
      <v-btn
        icon="mdi-cog"
        flat
        size="xs"
        v-bind="menuProps"
        :disabled="isLoading"
      ></v-btn>
    </template>
    <v-form v-model="formValid" ref="form">
      <v-card :width="isMobile ? '400' : '350'">
        <v-card-title>Widget {{ widget }}</v-card-title>
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
                ></v-text-field>
              </v-col>
            </v-row>
            <v-row dense>
              <v-col>
                <v-radio-group
                  title="Graph Type"
                  v-model="formData.graph_type"
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
                  density="compact"
                ></v-autocomplete>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-btn :disabled="!formComplete" @click="submitForm">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
  </v-menu>
</template>
<script setup>
  import { ref, reactive, computed } from "vue";
  import { useOptions } from "@/composables/optionsComposable";
  import { useTags, useParentTags } from "@/composables/tagsComposable";
  import { useDisplay } from "vuetify";

  const props = defineProps({
    widget: {
      type: Number,
      required: true,
    },
  });

  const { smAndDown } = useDisplay();
  const isMobile = smAndDown;

  const { options, isLoading, editOptions } = useOptions();
  const { tags, isLoading: tags_isLoading } = useTags();
  const { parent_tags, isLoading: parent_tags_isLoading } = useParentTags();

  const menu = ref(false);
  const formValid = ref(false);
  const formData = reactive({
    graph_name: "",
    graph_type: 1,
    tag_id: null,
    exclude: [],
  });

  const required = [v => !!v || "This field is required."];

  const formComplete = computed(() => {
    if (!formData.graph_name) return false;
    if (formData.graph_type === 4 && !formData.tag_id) return false;
    return true;
  });

  const onMenuStateChange = val => {
    if (!val || !options.value) return;
    const w = props.widget;
    formData.graph_name = options.value[`widget${w}_graph_name`] ?? "";
    formData.graph_type = options.value[`widget${w}_type`]?.id ?? 1;
    formData.tag_id = options.value[`widget${w}_tag_id`] ?? null;
    const excludeStr = options.value[`widget${w}_exclude`];
    formData.exclude = excludeStr
      ? excludeStr.split(",").map(id => parseInt(id)).filter(Boolean)
      : [];
  };

  const submitForm = () => {
    const w = props.widget;
    editOptions({
      [`widget${w}_graph_name`]: formData.graph_name,
      [`widget${w}_tag_id`]: formData.tag_id ?? null,
      [`widget${w}_type_id`]: formData.graph_type,
      [`widget${w}_exclude`]: formData.exclude?.length
        ? formData.exclude.join(",")
        : null,
    });
    menu.value = false;
  };
</script>
