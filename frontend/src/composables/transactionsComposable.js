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

async function getTransactionsFunction(account_id) {
  try {
    if (account_id) {
      const response = await apiClient.get('/transactions?account=' + account_id)
      return response.data
    } else {
      const response = await apiClient.get('/transactions')
      return response.data
    }
      
    } catch (error) {
      handleApiError(error, 'Transactions not fetched: ')
    }

}

async function createTransactionFunction(newTransaction) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.post('/transactions', newTransaction)
    mainstore.showSnackbar('Transaction created successfully!', 'success')
    return response.data
  } catch (error) {
    handleApiError(error, 'Transaction not created: ')
  }

}

export function useTransactions(account_id) {
  const queryClient = useQueryClient()
  const { data: transactions, isLoading } = useQuery({
    queryKey: ['transactions', { account: account_id }],
    queryFn: () => getTransactionsFunction(account_id),
    select: (response) => response,
    client: queryClient
})

const createTransactionMutation = useMutation({
  mutationFn: createTransactionFunction,
  onSuccess: () => {
    console.log('Success adding transaction')
    queryClient.invalidateQueries({ queryKey: ['transactions'] })
    queryClient.invalidateQueries({ queryKey: ['accounts'] })
  }
})

async function addTransaction(newTransaction) {
  createTransactionMutation.mutate(newTransaction);
}
  
  return {
    isLoading,
    transactions,
    addTransaction
  }
}