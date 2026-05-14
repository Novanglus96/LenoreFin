<template>
  <div>
    <v-card
      variant="outlined"
      :elevation="4"
      class="bg-primary"
      v-if="!isLoading"
    >
      <template v-slot:text>
        <v-row desnity="compact">
          <v-col>
            <div class="text-center">
              <v-btn
                prepend-icon="mdi-plus"
                size="small"
                variant="text"
                @click="tagAddFormDialog = true"
                v-if="authStore.isFullAccess"
              >
                Add Tag
              </v-btn>
              <v-btn
                icon="mdi-pencil"
                size="small"
                variant="text"
                @click="openEditDialog"
                v-if="authStore.isFullAccess && selectedTag && !selectedTag.is_system"
              ></v-btn>
              <v-btn
                icon="mdi-delete"
                size="small"
                variant="text"
                color="error"
                @click="deleteDialog = true"
                v-if="authStore.isFullAccess && selectedTag && !selectedTag.is_system"
              ></v-btn>
              <TagForm
                v-model="tagAddFormDialog"
                @update-dialog="updateAddDialog"
              />
              <TagForm
                v-model="tagEditFormDialog"
                :is-edit="true"
                :tag-data="selectedTag"
                @update-dialog="updateEditDialog"
              />
            </div>
            <v-slide-group
              v-model="tag_selected"
              class="pa-4"
              selected-class="bg-selected"
              show-arrows
              center-active
              v-if="!smAndDown"
            >
              <v-slide-group-item
                v-for="tag in tags"
                :key="tag.id"
                v-slot="{ toggle, selectedClass }"
                @group:selected="clickSelectTag"
                :value="tag.id"
              >
                <v-card
                  color="surface"
                  :class="['ma-4', selectedClass]"
                  height="75"
                  width="250"
                  @click="toggle"
                >
                  <template v-slot:prepend>
                    <v-icon
                      :icon="tag.is_system ? 'mdi-tag' : 'mdi-tag-outline'"
                      :color="tagColor(tag.tag_type.id)"
                    ></v-icon>
                  </template>
                  <template v-slot:title>
                    <span class="text-subtitle-1 font-weight-bold">
                      {{ tag.parent ? tag.parent.tag_name : tag.tag_name }}
                    </span>
                  </template>
                  <template v-slot:subtitle>
                    <span
                      :class="
                        !tag.child
                          ? 'text-secondary'
                          : 'text-secondary-lighten-2'
                      "
                    >
                      {{ !tag.child ? "..." : tag.child.tag_name }}
                    </span>
                  </template>
                </v-card>
              </v-slide-group-item>
            </v-slide-group>
            <v-select
              :items="tags"
              variant="outlined"
              :loading="isLoading"
              item-title="tag_name"
              item-value="id"
              v-model="tag_selected"
              density="compact"
              @update:model-value="clickSelectTag"
              bg-color="secondary"
              menu
              color="primary"
              v-else
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
                      :icon="item.raw.is_system ? 'mdi-tag' : 'mdi-tag-outline'"
                      :color="tagColor(item.raw.tag_type.id)"
                    ></v-icon>
                  </template>
                </v-list-item>
              </template>
            </v-select>
          </v-col>
        </v-row>
      </template>
    </v-card>
    <v-skeleton-loader type="card" v-if="isLoading"></v-skeleton-loader>

    <v-dialog v-model="deleteDialog" max-width="400" persistent>
      <v-card>
        <v-card-title class="text-h6">Delete Tag</v-card-title>
        <v-card-text>
          Are you sure you want to delete
          <strong>{{ selectedTag ? selectedTag.tag_name : "" }}</strong>?
          This cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="deleteDialog = false">Cancel</v-btn>
          <v-btn color="error" variant="text" @click="confirmDelete">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>
<script setup>
  import { ref, computed, defineEmits } from "vue";
  import { useTags } from "@/composables/tagsComposable";
  import TagForm from "@/components/TagForm.vue";
  import { useDisplay } from "vuetify";
  import { useAuthStore } from "@/stores/auth";

  const tagAddFormDialog = ref(false);
  const tagEditFormDialog = ref(false);
  const deleteDialog = ref(false);
  const emit = defineEmits(["tagSelected"]);
  const authStore = useAuthStore();
  const tag_selected = ref(null);
  const { tags, isLoading, removeTag } = useTags();
  const { smAndDown } = useDisplay();

  const selectedTag = computed(() =>
    tags.value ? tags.value.find(t => t.id === tag_selected.value) ?? null : null,
  );

  const clickSelectTag = () => {
    emit("tagSelected", tag_selected.value);
  };

  const updateAddDialog = () => {
    tagAddFormDialog.value = false;
  };

  const updateEditDialog = () => {
    tagEditFormDialog.value = false;
  };

  const openEditDialog = () => {
    tagEditFormDialog.value = true;
  };

  const confirmDelete = () => {
    if (selectedTag.value) {
      removeTag(selectedTag.value.id);
      tag_selected.value = null;
      emit("tagSelected", null);
    }
    deleteDialog.value = false;
  };

  const tagColor = typeID => {
    if (typeID == 1) {
      return "error";
    } else if (typeID == 2) {
      return "success";
    } else if (typeID == 3) {
      return "info";
    }
  };
</script>
