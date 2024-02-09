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

async function getRemindersFunction() {
  try {
    const response = await apiClient.get('/reminders')
    logToDB(null, 'Reminders fetched', 0, null, null, null)
    return response.data
      
    } catch (error) {
    handleApiError(error, 'Reminders not fetched: ')
    logToDB(error, 'Reminders not fetched', 2, null, null, null)
    }

}

export function useReminders() {
  const queryClient = useQueryClient()
  const { data: reminders, isLoading } = useQuery({
    queryKey: ['reminders'],
    queryFn: () => getRemindersFunction(),
    select: (response) => response,
    client: queryClient
  })
  
  return {
    isLoading,
    reminders
  }
}