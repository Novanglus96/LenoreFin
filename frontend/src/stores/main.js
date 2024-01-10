import { defineStore } from 'pinia'

export const useMainStore = defineStore('main', {
    state: () => ({
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
                date: 'January 5th, 2024',
                amount: '-400.00',
                reminder: 'Transfer to Kids',
                notes: 'None',
            },
            {
                id: 2,
                date: 'January 5th, 2024',
                amount: '-200.00',
                reminder: 'Transfer to Money Pile',
                notes: 'None',
            },
            {
                id: 3,
                date: 'January 5th, 2024',
                amount: '991.48',
                reminder: 'Primepoint Payroll - Danielle',
                notes: 'None',
            },
            {
                id: 4,
                date: 'January 5th, 2024',
                amount: '192.30',
                reminder: 'Dependent Care Contribution',
                notes: 'None',
            },
            {
                id: 5,
                date: 'January 5th, 2024',
                amount: '-100.00',
                reminder: 'Transfer to Reno',
                notes: 'None',
            },
        ],
        transaction_items: [ // temporary
            {
                id: 1,
                status: 'Pending',
                date: '3rd Jan 2024',
                amount: '-950.00',
                balance: '-950.00',
                description: 'Rent',
                tag: 'Rent',
                account: 'Our Checking Account',
            },
            {
                id: 2,
                status: 'Pending',
                date: '4th Jan 2024',
                amount: '-503.36',
                balance: '-950.00',
                description: 'Transfer from Savings (Christmas)',
                tag: 'Transfer',
                account: 'Ally - Christmas => Our Checking Account',
            },
            {
                id: 3,
                status: 'Cleared',
                date: '4th Jan 2024',
                amount: '-1660.46',
                balance: '-950.00',
                description: 'Transfer to Checking (Kids)',
                tag: 'Transfer',
                account: 'Ally - Kids => Our Checking Account',
            },
            {
                id: 4,
                status: 'Cleared',
                date: '4th Jan 2024',
                amount: '-1530.00',
                balance: '-950.00',
                description: 'Zelle Payment to Lilys Ducklings',
                tag: 'Kids/Child Care',
                account: 'Our Checking Account',
            },
            {
                id: 5,
                status: 'Cleared',
                date: '4th Jan 2024',
                amount: '-20.00',
                balance: '-950.00',
                description: 'Transfer to Checking (Charity)',
                tag: 'Transfer',
                account: 'Ally - Charity => Our Checking Account',
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