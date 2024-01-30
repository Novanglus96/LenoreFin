<template>
    <v-card>
        <v-card-title>Options</v-card-title>
        <v-card-text>
            <v-container>
                <v-row>
                    <v-col>
                        <v-autocomplete
                            clearable
                            label="Log Level*"
                            :items="error_levels"
                            variant="outlined"
                            :loading="error_levels_isLoading"
                            item-title="error_level"
                            item-value="id"
                            v-model="formData.log_level_id"
                            :rules="required"
                            @update:model-value="checkFormComplete"
                        ></v-autocomplete>
                    </v-col>
                </v-row>
                <v-row>
                    <v-col>
                        <v-text-field
                            v-model="formData.alert_balance"
                            variant="outlined"
                            label="Alert Balance*"
                            :rules="required"
                            prefix="$"
                            @update:model-value="checkFormComplete"
                        ></v-text-field>
                    </v-col>
                    <v-col>
                        <v-text-field
                            v-model="formData.alert_period"
                            variant="outlined"
                            label="Alert Period(months)*"
                            :rules="required"
                            @update:model-value="checkFormComplete"
                        ></v-text-field>
                    </v-col>
                </v-row>
            </v-container>
        </v-card-text>
        <v-card-actions>
            <v-btn :disabled="!formComplete" @click="submitForm()">
                Save
            </v-btn>
        </v-card-actions>
    </v-card>
</template>
<script setup>
import { useErrorLevels } from '@/composables/errorLevelsComposable'
import { ref } from 'vue'
import { useMainStore } from '@/stores/main'
import { useOptions } from '@/composables/optionsComposable'

const mainstore = useMainStore()
const formComplete = ref(false)
const { editOptions } = useOptions()
const formData = ref({
    log_level_id: mainstore.options.log_level.id,
    alert_balance: mainstore.options.alert_balance,
    alert_period: mainstore.options.alert_period
})
const { error_levels, isLoading: error_levels_isLoading } = useErrorLevels()
const checkFormComplete = async () => {
    if (formData.value.log_level_id !== null
        && formData.value.log_level_id !== ''
        && formData.value.alert_balance !== null
        && formData.value.alert_balance !== ''
        && formData.value.alert_period !== null
        && formData.value.alert_period !== ''
    ) {
        formComplete.value = true

    } else {
        formComplete.value = false
    }
}
const required = [
    value => {
        if (value) return true;

        return 'This field is required.';
    },
]
const submitForm = () => {
    editOptions(formData.value)
    //const { options } = useOptions()
    //mainstore.options = options
}
</script>