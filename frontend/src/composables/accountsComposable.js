import { useQuery, useQueryClient } from "@tanstack/vue-query";
import axios from 'axios'
import { useMainStore } from '@/stores/main'

const apiClient = axios.create({
  baseURL: '/api/v1',
  withCredentials: false,
  headers: {
    Accept: 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer sVruPBzWnGEDrLb7JjfVNrs9wk8LtgnDQef6iXDXc4bWMUk3XFcsCtEgT8dKzhJd' //TODO: Pull API_KEY from somewhere secure
  }
})

function handleApiError(error, message) {
  const mainstore = useMainStore();
  if (error.response) {
    console.error('Response error:', error.response.data)
    console.error('Status code:', error.response.status)
    console.error('Headers', error.response.headers)
  } else if (error.request){
    console.error('No response received:', error.request)
  } else {
    console.error('Error during request setup:', error.message)
  }
  mainstore.showSnackbar(message + 'Error #' + error.response.status, 'error')
  throw error
}

async function getAccountsFunction(account_type) {
  try {
    if (account_type !== 'all') {
      const response = await apiClient.get('/accounts?account_type=' + account_type)
      return response.data
    } else {
      const response = await apiClient.get('/accounts')
      return response.data
    }
      
    } catch (error) {
      handleApiError(error, 'Accounts not fetched: ')
    }

}

export function useAccounts() {
    const queryClient = useQueryClient()
    const { data: accounts, isLoading } = useQuery({
        queryKey: ['accounts', 'all'],
        queryFn: () => getAccountsFunction('all'),
        select: (response) => response,
        client: queryClient
    })

    const { data: cc_accounts, cc_isLoading } = useQuery({
        queryKey: ['accounts', '1'],
        queryFn: () => getAccountsFunction('1'),
        select: (response) => response,
        client: queryClient
    })

    const { data: checking_accounts, checking_isLoading } = useQuery({
        queryKey: ['accounts', '2'],
        queryFn: () => getAccountsFunction('2'),
        select: (response) => response,
        client: queryClient
    })

    const { data: savings_accounts, savings_isLoading } = useQuery({
        queryKey: ['accounts', '3'],
        queryFn: () => getAccountsFunction('3'),
        select: (response) => response,
        client: queryClient
    })

    const { data: investment_accounts, investment_isLoading } = useQuery({
        queryKey: ['accounts', '4'],
        queryFn: () => getAccountsFunction('4'),
        select: (response) => response,
        client: queryClient
    })

    const { data: loan_accounts, loan_isLoading } = useQuery({
        queryKey: ['accounts', '5'],
        queryFn: () => getAccountsFunction('5'),
        select: (response) => response,
        client: queryClient
    })

    return {
        accounts,
        isLoading,
        cc_accounts,
        cc_isLoading,
        checking_accounts,
        checking_isLoading,
        savings_accounts,
        savings_isLoading,
        investment_accounts,
        investment_isLoading,
        loan_accounts,
        loan_isLoading
    }
}