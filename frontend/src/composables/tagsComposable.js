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

async function getTagsFunction() {
  try {
    const response = await apiClient.get('/tags')
    return response.data
      
    } catch (error) {
      handleApiError(error, 'Tags not fetched: ')
    }

}

async function createTagFunction(newTag) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.post('/tags', newTag)
    mainstore.showSnackbar('Tag created successfully!', 'success')
    return response.data
  } catch (error) {
    handleApiError(error, 'Tag not created: ')
  }

}

export function useTags() {
  const queryClient = useQueryClient()
  const { data: tags, isLoading } = useQuery({
    queryKey: ['tags'],
    queryFn: () => getTagsFunction(),
    select: (response) => response,
    client: queryClient
})

const createTagMutation = useMutation({
    mutationFn: createTagFunction,
    onSuccess: () => {
      console.log('Success adding tag')
      queryClient.invalidateQueries({ queryKey: ['tags'] })
    }
})

async function addTag(newTag) {
  createTagMutation.mutate(newTag);
}

return {
  isLoading,
  tags,
  addTag
}
}