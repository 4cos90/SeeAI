import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

export const getLeaderboard = () => {
  return api.get('/leaderboard').then(res => res.data)
}

export const healthCheck = () => {
  return api.get('/health').then(res => res.data)
}
