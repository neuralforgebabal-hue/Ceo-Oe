import axios from 'axios'

const api = axios.create({ baseURL: '/api', timeout: 30000 })

// Projects
export const scanProjects = () => api.post('/projects/scan')
export const getProjects = () => api.get('/projects/')
export const getProject = (id) => api.get(`/projects/${id}`)
export const getProjectStats = () => api.get('/projects/stats/summary')

// Agents
export const getAgents = () => api.get('/agents/')
export const runAgent = (agentName, projectId) =>
  api.post('/agents/run', { agent_name: agentName, project_id: projectId })
export const runAllAgents = (projectId, agents = null) =>
  api.post('/agents/run-all', { project_id: projectId, agents })
export const getAgentEvents = (limit = 50) => api.get(`/agents/events?limit=${limit}`)

// Tasks
export const getTasks = (status = null) =>
  api.get('/tasks/' + (status ? `?status=${status}` : ''))

// Memory
export const getMemories = (limit = 50) => api.get(`/memory/?limit=${limit}`)
export const getBusEvents = (limit = 100) => api.get(`/memory/bus?limit=${limit}`)
export const getSharedState = () => api.get('/memory/state')

// Reports
export const getReports = (projectId) => api.get(`/reports/${projectId}`)

// Engine
export const predictProject = (projectId) =>
  api.post('/engine/predict', { project_id: projectId })
export const improveProject = (projectId) =>
  api.post('/engine/improve', { project_id: projectId })
export const generateProject = (description, template, outputName) =>
  api.post('/engine/generate', { description, template, output_name: outputName })
export const getTemplates = () => api.get('/engine/templates')
export const analyzeFile = (filePath) =>
  api.post('/engine/analyze-file', { file_path: filePath })

export default api
