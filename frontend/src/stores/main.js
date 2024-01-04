import { defineStore } from 'pinia'

export const useMainStore = defineStore('main', {
    state: () => ({
        snackbarText: '',
        snackbarColor: '',
        snackbar: false,
        snackbarTimeout: 1500,
        graphColors: [
            '#7fb1b1',
            '#597c7c',
            '#7f8cb1',
            '#7fb17f',
            '#597c59',
            '#b17fa5',
            '#7c5973',
            '#b1a77f',
            '#edffff',
            '#dbffff',
        ]
    }),
    getters: {
    },
    actions: {
        async showSnackbar(text, color) {
            this.snackbarText = text;
            this.snackbarColor = color;
            this.snackbar = true;
        },
    },
})