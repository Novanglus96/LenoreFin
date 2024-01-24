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
        <v-menu location="start">
            <template v-slot:activator="{ props }">
                <v-btn class="text-none" stacked v-bind="props">
                <v-badge :content="messages.unread_count" color="error" v-if="messages.unread_count > 0">
                    <v-icon icon="mdi-inbox-full"></v-icon>
                </v-badge>
                <v-icon icon="mdi-inbox" v-else></v-icon>
                </v-btn>
            </template>
            <v-card width="500" density="compact">
                <v-card-text>
                    <v-list density="compact" nav>
                        <v-list-item :prepend-icon="message.unread ? 'mdi-message-text' : 'mdi-message-text-outline'" v-for="message in messages.messages" :key="message.id">
                            <v-list-item-title><span :class="message.unread ? 'font-weight-bold' : ''">{{ message.message }}</span></v-list-item-title>
                            <v-list-item-subtitle><span :class="message.unread ? 'font-weight-bold' : ''">{{ message.message_date }}</span></v-list-item-subtitle>
                        </v-list-item>
                        <v-list-item v-if="messages.total_count == 0">
                            No messages : You're all caught up!
                        </v-list-item>
                    </v-list>
                </v-card-text>
                <v-card-actions v-if="messages.total_count > 0">
                    <v-spacer></v-spacer>
                    <v-btn color="accent" @click="markRead">
                        Mark All Read
                    </v-btn>
                    <v-btn color="accent" @click="deleteAll">
                        Delete All
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-menu>
    </v-app-bar>
    <v-navigation-drawer color="accent" rail permanent v-if="!mdAndUp">
        <v-list density="compact" nav>
            <v-list-item prepend-icon="mdi-view-dashboard-variant" to="/"></v-list-item>
            <v-list-item prepend-icon="mdi-bank" to="/accounts"></v-list-item>
            <v-list-item prepend-icon="mdi-chart-bar" to="/forecast"></v-list-item>
            <v-list-item prepend-icon="mdi-bell" to="/reminders"></v-list-item>
            <v-list-item prepend-icon="mdi-folder" to="/planning"></v-list-item>
            <v-list-item prepend-icon="mdi-tag" to="/tags"></v-list-item>
            <v-list-item prepend-icon="mdi-cog" to="/settings"></v-list-item>
        </v-list>
    </v-navigation-drawer>
    <v-navigation-drawer color="accent" rail permanent v-if="mdAndUp">
        <v-list density="compact" nav>
            <v-tooltip text="Dashboard">
                <template v-slot:activator="{ props }">
                <v-list-item prepend-icon="mdi-view-dashboard-variant" to="/" v-bind="props"></v-list-item>
                </template>
            </v-tooltip>
            <v-tooltip text="Accounts">
                <template v-slot:activator="{ props }">
                    <v-list-item
                    active-color="white"
                    :active="nav_toggle"
                    prepend-icon="mdi-bank"
                    @click="nav_toggle = true"
                    v-bind="props"
                    ></v-list-item>
                </template>
            </v-tooltip>
            <v-tooltip text="Forecast">
                <template v-slot:activator="{ props }">
                    <v-list-item prepend-icon="mdi-chart-bar" to="/forecast" v-bind="props"></v-list-item>
                </template>
            </v-tooltip>
            <v-tooltip text="Reminders">
                <template v-slot:activator="{ props }">
                    <v-list-item prepend-icon="mdi-bell" to="/reminders" v-bind="props"></v-list-item>
                </template>
            </v-tooltip>
            <v-tooltip text="Planning">
                <template v-slot:activator="{ props }">
                    <v-list-item active-color="white" :active="!nav_toggle" prepend-icon="mdi-folder" @click="nav_toggle = false" v-bind="props"></v-list-item>
                </template>
            </v-tooltip>
            <v-tooltip text="Tags">
                <template v-slot:activator="{ props }">
                    <v-list-item prepend-icon="mdi-tag" to="/tags" v-bind="props"></v-list-item>
                </template>
            </v-tooltip>
            <v-tooltip text="Settings">
                <template v-slot:activator="{ props }">
                    <v-list-item prepend-icon="mdi-cog" to="/settings" v-bind="props"></v-list-item>
                </template>
            </v-tooltip>
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
import { useMessages } from '@/composables/messagesComposable'

const { messages, markRead, deleteAll } = useMessages()
const { mdAndUp } = useDisplay()
const nav_toggle = ref(true)

</script>
