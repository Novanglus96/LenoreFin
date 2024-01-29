import { defineStore } from 'pinia'

export const useMainStore = defineStore('main', {
    state: () => ({
        log_level: 0,
        units: [
            {
                name: 'day(s)',
                letter: 'd'
            },
            {
                name: 'week(s)',
                letter: 'w'
            },
            {
                name: 'month(s)',
                letter: 'm'
            },
            {
                name: 'year(s)',
                letter: 'y'
            },
        ],
        time_frames: [
            {
                days: 30,
                title: '30 Days'
            },
            {
                days: 60,
                title: '60 Days'
            },
            {
                days: 90,
                title: '90 Days'
            },
            {
                days: 180,
                title: '6 Months'
            },
            {
                days: 365,
                title: '1 Year'
            },
            {
                days: 730,
                title: '2 Years'
            },
            {
                days: 1095,
                title: '3 Years'
            },
            {
                days: 1825,
                title: '5 Years'
            },
            {
                days: 3650,
                title: '10 Years'
            }
        ],
        intervals: [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31],
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
        ],
        kids_expenses_widget: { // temporary
            labels: [
                'Child Care',
                'Diapers/Wipes',
            ],
            data: [
                1530.00,
                12.30,
            ]
        },
        main_expenses_widget: { // temporary
            labels: [
                'Money Pile',
                'Kids',
                'Rent',
                'Subscriptions'
            ],
            data: [
                .33,
                58.05,
                36.04,
                5.58]
        },
        money_pile_expenses_widget: { // temporary
            labels: [
                'Eating Out',
            ],
            data: [
                8.79,
            ]
        },
        reminder_items: [ // temporary
            {
                id: 1,
                date: '2024-01-05',
                amount: '-400.00',
                reminder: 'Transfer to Kids',
                notes: 'None',
            },
            {
                id: 2,
                date: '2024-01-05',
                amount: '-200.00',
                reminder: 'Transfer to Money Pile',
                notes: 'None',
            },
            {
                id: 3,
                date: '2024-01-05',
                amount: '991.48',
                reminder: 'Primepoint Payroll - Danielle',
                notes: 'None',
            },
            {
                id: 4,
                date: '2024-01-05',
                amount: '192.30',
                reminder: 'Dependent Care Contribution',
                notes: 'None',
            },
            {
                id: 5,
                date: '2024-01-05',
                amount: '-100.00',
                reminder: 'Transfer to Reno',
                notes: 'None',
            },
        ],
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