<template>
    <div>
    <v-app-bar color="primary" density="compact">
        <v-app-bar-nav-icon><v-img
                    :width="32"
                    aspect-ratio="1/1"
                    cover
                    src="Logo.png"
                ></v-img></v-app-bar-nav-icon>
        <v-app-bar-title>Money v1.0</v-app-bar-title>
    </v-app-bar>
    <v-navigation-drawer color="accent" rail permanent v-if="!mdAndUp">
        <v-list density="compact" nav>
            <v-list-item prepend-icon="mdi-view-dashboard" to="/"></v-list-item>
            <v-list-item prepend-icon="mdi-bank" to="/accounts" ></v-list-item>
            <v-list-item prepend-icon="mdi-chart-bar" to="/forecast"></v-list-item>
            <v-list-item prepend-icon="mdi-bell" to="/reminders"></v-list-item>
            <v-list-item prepend-icon="mdi-folder" to="/planning"></v-list-item>
            <v-list-item prepend-icon="mdi-tag" to="/tags"></v-list-item>
            <v-list-item prepend-icon="mdi-cog" to="/settings"></v-list-item>
        </v-list>
    </v-navigation-drawer>
    <v-navigation-drawer color="accent" rail permanent v-if="mdAndUp">
        <v-list density="compact" nav>
            <v-list-item prepend-icon="mdi-view-dashboard" to="/"></v-list-item>
            <v-list-item
            prepend-icon="mdi-bank"
            @click="nav_toggle = true"
            ></v-list-item>

            <v-list-item prepend-icon="mdi-chart-bar" to="/forecast"></v-list-item>
            <v-list-item prepend-icon="mdi-bell" to="/reminders"></v-list-item>
            <v-list-item prepend-icon="mdi-folder" @click="nav_toggle = false"></v-list-item>
            <v-list-item prepend-icon="mdi-tag" to="/tags"></v-list-item>
            <v-list-item prepend-icon="mdi-cog" to="/settings"></v-list-item>
        </v-list>
        </v-navigation-drawer>

        <v-navigation-drawer permanent widht="250" color="primary" v-if="mdAndUp">
        <AccountsMenu v-if="nav_toggle"/>
        <PlanningMenu v-if="!nav_toggle"/>
    </v-navigation-drawer>
</div>
</template>
<script setup>
import { ref } from 'vue'
import { useDisplay } from 'vuetify'
import AccountsMenu from '@/components/AccountsMenu.vue'
import PlanningMenu from '@/components/PlanningMenu.vue'

const { mdAndUp } = useDisplay()
const nav_toggle = ref(true)

</script>
