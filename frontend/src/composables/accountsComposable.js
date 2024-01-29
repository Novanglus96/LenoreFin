import { useQuery, useQueryClient, useMutation } from "@tanstack/vue-query";
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

async function logToDB(error, message, errorlevel, account_id, reminder_id, transaction_id) {
  const mainstore = useMainStore()
  let error_num = 0
  if (error) {
    error_num = error.response.status
  } else {
    error_num = null
  }
  const logEntry = {
    log_entry: message,
    account_id: account_id,
    reminder_id: reminder_id,
    transaction_id: transaction_id,
    error_num: error_num,
    error_level_id: errorlevel
  }
  if (errorlevel >= mainstore.log_level) {
    const response = await apiClient.post('/logentries', logEntry)
    return response.data
  }
}

async function getAccountsFunction(account_type) {
  try {
    if (account_type !== 'all') {
      const response = await apiClient.get('/accounts?account_type=' + account_type)
      logToDB(null, 'Accounts of type ' + account_type + ' fetched', 0, null, null, null)
      return response.data
    } else {
      const response = await apiClient.get('/accounts')
      logToDB(null, 'All accounts fetched', 0, null, null, null)
      return response.data
    }
      
  } catch (error) {
      logToDB(error, 'Accounts not fetched', 2, null, null, null)
      handleApiError(error, 'Accounts not fetched: ')
    }

}

async function getAccountByIDFunction(account_id) {
  try {
    const response = await apiClient.get('/accounts/' + account_id)
    return response.data
      
    } catch (error) {
      handleApiError(error, 'Account not fetched: ')
    }

}

async function createAccountFunction(newAccount) {
  const chorestore = useMainStore();
  try {
    const response = await apiClient.post('/accounts', newAccount)
    chorestore.showSnackbar('Account created successfully!', 'success')
    console.log('Account created')
    logToDB(null, 'Account created', 1, response.data.id, null, null)
    return response.data
  } catch (error) {
    handleApiError(error, 'Account not created: ')
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
  
  return {
    isLoading,
    account
  }
}
