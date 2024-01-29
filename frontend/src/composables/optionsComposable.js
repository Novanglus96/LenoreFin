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

async function getOptionsFunction() {
  try {
    const response = await apiClient.get('/options/1')
    return response.data
      
    } catch (error) {
      handleApiError(error, 'Options not fetched: ')
    }

}

async function updateOptionsFunction(updatedOptions) {
  try {
    const response = await apiClient.put('/options/1', updatedOptions)
    return response.data
  } catch (error) {
    handleApiError(error, 'Options not updated: ')
  }
}

export function useOptions() {
  const queryClient = useQueryClient()
  const { data: options, isLoading } = useQuery({
    queryKey: ['options'],
    queryFn: () => getOptionsFunction(),
    select: (response) => response,
    client: queryClient
  })
  
const updateOptionsMutation = useMutation({
  mutationFn: updateOptionsFunction,
  onSuccess: () => {
    console.log('Success updating options')
    queryClient.invalidateQueries({ queryKey: ['options'] })
  }
})

async function editOptions(updatedOptions) {
  updateOptionsMutation.mutate(updatedOptions)
}

return {
  isLoading,
  options,
  editOptions
}
}