import { useQuery, useQueryClient } from "@tanstack/vue-query";
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

async function getAccountForecastFunction(account_id, start_integer, end_integer) {
  try {
    const response = await apiClient.get('/accounts/' + account_id + '/forecast?start_interval=' + start_integer + '&end_interval=' + end_integer)
    logToDB(null, 'Account forecast fetched', 0, account_id, null, null)
    return response.data
      
    } catch (error) {
    handleApiError(error, 'Account forecast not fetched: ')
    logToDB(error, 'Account forecast not fetched', 2, account_id, null, null)
    }

}

export function useAccountForecasts(account_id, start_integer, end_integer) {
  const queryClient = useQueryClient()
  const { data: account_forecast, isLoading } = useQuery({
    queryKey: ['account_forecast', { account: account_id }],
    queryFn: () => getAccountForecastFunction(account_id, start_integer, end_integer),
    select: (response) => response,
    client: queryClient
  })
  
  return {
    isLoading,
    account_forecast
  }
}