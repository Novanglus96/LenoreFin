<template>
    <v-dialog v-model="show" persistent width="1024">
        <v-card>
            <v-card-title>
                <span class="text-h5">Add Tag</span>
            </v-card-title>
            <v-card-text>
                <v-container>
                    <v-row>
                        <v-col>
                            <v-text-field
                                v-model="formData.tag_name"
                                variant="outlined"
                                label="Tag Name*"
                                :rules="required"
                                @update:model-value="checkFormComplete"
                            ></v-text-field>
                        </v-col>
                    </v-row>
                    <v-row>
                        <v-col>
                            <v-autocomplete
                                clearable
                                label="Tag Type*"
                                :items="tag_types"
                                variant="outlined"
                                :loading="tag_types_isLoading"
                                item-title="tag_type"
                                item-value="id"
                                v-model="formData.tag_type_id"
                                :rules="required"
                                @update:model-value="checkFormComplete"
                            ></v-autocomplete>
                        </v-col>
                        <v-col>
                            <v-autocomplete
                                clearable
                                label="Parent"
                                :items="parent_tags"
                                variant="outlined"
                                :loading="parent_tags_isLoading"
                                item-title="tag_name"
                                item-value="id"
                                v-model="formData.parent_id"
                            ></v-autocomplete>
                        </v-col>
                    </v-row>
                </v-container>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn
                    color="accent"
                    variant="text"
                    @click="closeDialog"
                >
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
import { ref, defineEmits } from 'vue'
import { useTags } from '@/composables/tagsComposable'
import { useParentTags } from '@/composables/tagsComposable'
import { useTagTypes } from '@/composables/tagtypesComposable'

const { tag_types, isLoading: tag_types_isLoading } = useTagTypes()
const { addTag } = useTags()
const { parent_tags, isLoading: parent_tags_isLoading } = useParentTags()
const formComplete = ref(false)
const formData = ref({
    tag_name: "",
    parent_id: null,
    tag_type_id: 1
})

const required = [
    value => {
        if (value) return true;

        return 'This field is required.';
    },
];
const emit = defineEmits(['updateDialog'])
const checkFormComplete = async () => {
    if (formData.value.tag_name !== null 
        && formData.value.tag_name !== '' 
        && formData.value.tag_type_id !== null 
        && formData.value.tag_type_id !== ''
    ) {
        formComplete.value = true
        
    } else {
        formComplete.value = false
    }
}

const submitForm = async () => {
    addTag(formData.value)
    closeDialog()
}

const closeDialog = () => {
    emit('updateDialog', false);
};
</script>