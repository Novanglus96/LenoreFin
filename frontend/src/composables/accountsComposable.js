import { useQuery, useQueryClient, useMutation } from "@tanstack/vue-query";
import axios from 'axios'
import { useMainStore } from '@/stores/main'
import { logToDB } from "./logentriesComposable"

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
  const mainstore = useMainStore()
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

async function getAccountsFunction(account_type, inactive) {
  try {
    if (account_type !== 'all') {
      const response = await apiClient.get('/accounts?account_type=' + account_type)
      logToDB(null, 'Accounts of type ' + account_type + ' fetched', 0, null, null, null)
      return response.data
    } else {
      if (inactive) {
        const response = await apiClient.get('/accounts?inactive=true')
        logToDB(null, 'All inactive accounts fetched', 0, null, null, null)
        return response.data
      } else {
        const response = await apiClient.get('/accounts')
        logToDB(null, 'All accounts fetched', 0, null, null, null)
        return response.data
      }
      
    }
      
  } catch (error) {
      logToDB(error, 'Accounts not fetched', 2, null, null, null)
      handleApiError(error, 'Accounts not fetched: ')
    }

}

async function getAccountByIDFunction(account_id) {
  try {
    const response = await apiClient.get('/accounts/' + account_id)
    logToDB(null, 'Account fetched', 0, account_id, null, null)
    return response.data
      
    } catch (error) {
    handleApiError(error, 'Account not fetched: ')
    logToDB(error, 'Account not fetched', 2, account_id, null, null)
    }

}

async function createAccountFunction(newAccount) {
  const chorestore = useMainStore();
  try {
    const response = await apiClient.post('/accounts', newAccount)
    chorestore.showSnackbar('Account created successfully!', 'success')
    logToDB(null, 'Account created', 1, response.data.id, null, null)
    return response.data
  } catch (error) {
    handleApiError(error, 'Account not created: ')
    logToDB(error, 'Account not created', 2, null, null, null)
  }

}

async function deleteAccountFunction(deletedAccount) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.delete('/accounts/' + deletedAccount)
    logToDB(null, 'Account deleted', 1, deletedAccount, null, null)
    mainstore.showSnackbar('Account deleted successfully!', 'success')
    return response.data
  } catch (error) {
    handleApiError(error, 'Account not deleted: ')
    logToDB(error, 'Account not deleted', 2, deletedAccount, null, null)
  }
}

async function updateAccountFunction(updatedAccount) {
  try {
    const response = await apiClient.patch('/accounts/' + updatedAccount.id, updatedAccount)
    logToDB(null, 'Account updated', 1, updatedAccount.id, null, null)
    return response.data
  } catch (error) {
    handleApiError(error, 'Account not updated: ')
    logToDB(error, 'Account not updated', 2, updatedAccount.id, null, null)
  }
}

export function useAccounts() {
    const queryClient = useQueryClient()
    const { data: accounts, isLoading } = useQuery({
        queryKey: ['accounts', {type: 'all'}],
        queryFn: () => getAccountsFunction('all'),
        select: (response) => response,
        client: queryClient
    })

    const { data: cc_accounts, cc_isLoading } = useQuery({
        queryKey: ['accounts', {type: '1'}],
        queryFn: () => getAccountsFunction('1'),
        select: (response) => response,
        client: queryClient
    })

    const { data: checking_accounts, checking_isLoading } = useQuery({
        queryKey: ['accounts', {type: '2'}],
        queryFn: () => getAccountsFunction('2'),
        select: (response) => response,
        client: queryClient
    })

    const { data: savings_accounts, savings_isLoading } = useQuery({
        queryKey: ['accounts', {type: '3'}],
        queryFn: () => getAccountsFunction('3'),
        select: (response) => response,
        client: queryClient
    })

    const { data: investment_accounts, investment_isLoading } = useQuery({
        queryKey: ['accounts', {type: '4'}],
        queryFn: () => getAccountsFunction('4'),
        select: (response) => response,
        client: queryClient
    })

    const { data: loan_accounts, loan_isLoading } = useQuery({
        queryKey: ['accounts', {type: '5'}],
        queryFn: () => getAccountsFunction('5'),
        select: (response) => response,
        client: queryClient
    })
  
    const { data: inactive_accounts, inactive_isLoading } = useQuery({
        queryKey: ['accounts', {inactive: true}],
        queryFn: () => getAccountsFunction('all', true),
        select: (response) => response,
        client: queryClient
    })
  
    const createAccountMutation = useMutation({
      mutationFn: createAccountFunction,
      onSuccess: () => {
        console.log('Success adding account')
        queryClient.invalidateQueries({ queryKey: ['accounts'] })
      }
    })
  
    async function addAccount(newAccount) {
      createAccountMutation.mutate(newAccount);
    }

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
        loan_isLoading,
        inactive_accounts,
        inactive_isLoading,
        addAccount
    }
}

export function useAccountByID(account_id) {
  const queryClient = useQueryClient()
  const { data: account, isLoading } = useQuery({
    queryKey: ['accounts', { id: account_id }],
    queryFn: () => getAccountByIDFunction(account_id),
    select: (response) => response,
    client: queryClient
  })
  
  const deleteAccountMutation = useMutation({
  mutationFn: deleteAccountFunction,
  onSuccess: () => {
    console.log('Success deleting account')
    queryClient.invalidateQueries({ queryKey: ['transactions'] })
    queryClient.invalidateQueries({ queryKey: ['accounts'] })
    queryClient.invalidateQueries({ queryKey: ['account_forecast'] })
    queryClient.invalidateQueries({ queryKey: ['tag_graph'] })
  }
  })
  
  const updateAccountMutation = useMutation({
    mutationFn: updateAccountFunction,
    onSuccess: () => {
      console.log('Success updating account')
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      queryClient.invalidateQueries({ queryKey: ['accounts'] })
      queryClient.invalidateQueries({ queryKey: ['account_forecast'] })
      queryClient.invalidateQueries({ queryKey: ['tag_graph'] })
    }
  })

  async function editAccount(updatedAccount) {
    updateAccountMutation.mutate(updatedAccount)
  }

  async function removeAccount(deletedAccount) {
    deleteAccountMutation.mutate(deletedAccount);
  }
  
  return {
    isLoading,
    account,
    removeAccount,
    editAccount
  }
}
