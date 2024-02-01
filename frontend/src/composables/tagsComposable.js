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
    logToDB(null, 'Tags fetched', 0, null, null, null)
    return response.data
      
  } catch (error) {
    handleApiError(error, 'Tags not fetched: ')
    logToDB(error, 'Tags not fetched', 2, null, null, null)
  }

}

async function getParentTagsFunction() {
  try {
    const response = await apiClient.get('/tags?parent_only=true')
    logToDB(null, 'Parent Tags fetched', 0, null, null, null)
    return response.data
      
  } catch (error) {
    handleApiError(error, 'Parent Tags not fetched: ')
    logToDB(error, 'Parent Tags not fetched', 2, null, null, null)
  }

}

async function getGraphByTagsFunction(tag_id, expense, month, exclude, graph_name) {
  try {
    let query_params = '?graph_name=' + graph_name + '&month=' + month + '&expense=' + expense
    if (tag_id !== null) {
      query_params += `&tagID=${tag_id}`
    }
    exclude.forEach(id => {
      query_params += `&exclude=${id}`;
    })
    const response = await apiClient.get('/graphs_bytags' + query_params)
    logToDB(null, 'Graph by tags fetched', 0, null, null, null)
    return response.data
      
  } catch (error) {
    handleApiError(error, 'Graph by tags not fetched: ')
    logToDB(error, 'Graph by tags not fetched', 2, null, null, null)
  }

}

async function createTagFunction(newTag) {
  const mainstore = useMainStore();
  try {
    const response = await apiClient.post('/tags', newTag)
    mainstore.showSnackbar('Tag created successfully!', 'success')
    logToDB(null, 'Tag created: ' + newTag.tag_name, 1, null, null, null)
    return response.data
  } catch (error) {
    handleApiError(error, 'Tag not created: ')
    logToDB(error, 'Tag not created: ' + newTag.tag_name, 2, null, null, null)
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

export function useParentTags() {
  const queryClient = useQueryClient()
  const { data: parent_tags, isLoading } = useQuery({
    queryKey: ['tags', { parent_only: true }],
    queryFn: () => getParentTagsFunction(),
    select: (response) => response,
    client: queryClient
  })

  return {
    isLoading,
    parent_tags
  }
}

export function useGraphs(tag_id, expense, month, exclude, graph_name) {
  const queryClient = useQueryClient()
    const { data: tag_graph, isLoading } = useQuery({
      queryKey: ['tag_graph', { tagID: tag_id, expense: expense, month: month, exlude: exclude, graph_name: graph_name }],
      queryFn: () => getGraphByTagsFunction(tag_id, expense, month, exclude, graph_name),
      select: (response) => response,
      client: queryClient
  })

  return {
    isLoading,
    tag_graph
  }
}
