<template>
  <div>
    <v-card
      variant="outlined"
      :elevation="4"
      class="bg-secondary"
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
              >
                Add Tag
              </v-btn>
              <TagForm
                v-model="tagAddFormDialog"
                @update-dialog="updateAddDialog"
              />
            </div>
            <v-slide-group
              v-model="tag_selected"
              class="pa-4"
              selected-class="bg-accent"
              show-arrows
              center-active
            >
              <v-slide-group-item
                v-for="tag in tags"
                :key="tag.id"
                v-slot="{ toggle, selectedClass }"
                @group:selected="clickSelectTag"
                :value="tag.id"
              >
                <v-card
                  color="primary"
                  :class="['ma-4', selectedClass]"
                  height="75"
                  width="250"
                  @click="toggle"
                >
                  <template v-slot:prepend>
                    <v-icon
                      icon="mdi-tag"
                      :color="tagColor(tag.tag_type.id)"
                    ></v-icon>
                  </template>
                  <template v-slot:title>
                    <span class="text-subtitle-1 font-weight-bold">{{
                      tag.parent ? tag.parent.tag_name : tag.tag_name
                    }}</span>
                  </template>
                  <template v-slot:subtitle>
                    <span :class="!tag.child ? 'text-primary' : 'text-black'">{{
                      !tag.child ? "..." : tag.child.tag_name
                    }}</span>
                  </template>
                </v-card>
              </v-slide-group-item>
            </v-slide-group>
          </v-col>
        </v-row>
      </template>
    </v-card>
    <v-skeleton-loader type="card" v-if="isLoading"></v-skeleton-loader>
  </div>
</template>
<script setup>
import { ref, defineEmits } from "vue";
import { useTags } from "@/composables/tagsComposable";
import TagForm from "@/components/TagForm.vue";

const tagAddFormDialog = ref(false);
const emit = defineEmits(["tagSelected"]);
const tag_selected = ref(null);
const { tags, isLoading } = useTags();

const clickSelectTag = () => {
  emit("tagSelected", tag_selected.value);
};

const updateAddDialog = () => {
  tagAddFormDialog.value = false;
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
</script>
