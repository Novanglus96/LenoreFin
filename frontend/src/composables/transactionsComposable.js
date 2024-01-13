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
  const mainstore = useMainStore()
  let details = []
  try {
    const response = await apiClient.post('/transactions', newTransaction)
    mainstore.showSnackbar('Transaction created successfully!', 'success')

    if (newTransaction.transaction_type_id == 3) {
      details = [
        {
          transaction_id: response.data.id,
          account_id: newTransaction.source_account_id,
          detail_amt: newTransaction.total_amount,
          tag_id: newTransaction.tag_id
        },
        {
          transaction_id: response.data.id,
          account_id: newTransaction.destination_account_id,
          detail_amt: -newTransaction.total_amount,
          tag_id: newTransaction.tag_id
        }
      ]
    } else {
      details = [
        {
          transaction_id: response.data.id,
          account_id: newTransaction.source_account_id,
          detail_amt: newTransaction.total_amount,
          tag_id: newTransaction.tag_id
        }
      ]

    }
    return details
  } catch (error) {
    handleApiError(error, 'Transaction not created: ')
  }

}

async function createTransactionDetailFunction(newTransactionDetail) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.post('/transactions/details', newTransactionDetail)
    mainstore.showSnackbar('Transaction detail created successfully!', 'success')
    return response.data
  } catch (error) {
    handleApiError(error, 'Transaction detail not created: ')
  }

}

async function deleteTransactionFunction(deletedTransaction) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.delete('/transactions/' + deletedTransaction)
    mainstore.showSnackbar('Transaction deleted successfully!', 'success')
    return response.data
  } catch (error) {
    handleApiError(error, 'Transaction not deleted: ')
  }
}

async function clearTransactionFunction(clearedTransaction) {
  const mainstore = useMainStore();
  const payload = {
    status_id: 2
  }
  try {
    const response = await apiClient.patch('/transactions/clear/' + clearedTransaction, payload)
    mainstore.showSnackbar('Transaction cleared successfully!', 'success')
    return response.data
  } catch (error) {
    handleApiError(error, 'Transaction not cleared: ')
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
  onSuccess: (data) => {
    console.log('Success adding transaction', data)
    queryClient.invalidateQueries({ queryKey: ['transactions'] })
    queryClient.invalidateQueries({ queryKey: ['accounts'] })

    for (const detail of data) {
      createTransactionDetailMutation.mutate(detail)
    }
  }
})
  
const createTransactionDetailMutation = useMutation({
  mutationFn: createTransactionDetailFunction,
  onSuccess: () => {
    console.log('Success adding transaction detail')
    queryClient.invalidateQueries({ queryKey: ['transactions'] })
    queryClient.invalidateQueries({ queryKey: ['accounts'] })
  }
})
  
const deleteTransactionMutation = useMutation({
  mutationFn: deleteTransactionFunction,
  onSuccess: () => {
    console.log('Success deleting transaction')
    queryClient.invalidateQueries({ queryKey: ['transactions'] })
    queryClient.invalidateQueries({ queryKey: ['accounts'] })
  }
})
  
const clearTransactionMutation = useMutation({
  mutationFn: clearTransactionFunction,
  onSuccess: () => {
    console.log('Success clearing transaction')
    queryClient.invalidateQueries({ queryKey: ['transactions'] })
    queryClient.invalidateQueries({ queryKey: ['accounts'] })
  }
})

async function addTransaction(newTransaction) {
  createTransactionMutation.mutate(newTransaction);
}
  
async function removeTransaction(deletedTransaction) {
  deleteTransactionMutation.mutate(deletedTransaction);
}
  
async function clearTransaction(clearedTransaction) {
  clearTransactionMutation.mutate(clearedTransaction);
}
  
  return {
    isLoading,
    transactions,
    addTransaction,
    removeTransaction,
    clearTransaction
  }
}